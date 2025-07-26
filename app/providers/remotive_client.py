"""
Remotive.io API client for fetching remote job listings.

This module provides functionality to fetch and normalize job data from Remotive.io,
a platform specializing in remote job opportunities.
"""

import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

from app.models.models import Job

# Configure logging
logger = logging.getLogger(__name__)

# Remotive API endpoints
REMOTIVE_BASE_URL = "https://remotive.com/api"
REMOTIVE_JOBS_ENDPOINT = f"{REMOTIVE_BASE_URL}/remote-jobs"

# Default headers for API requests
DEFAULT_HEADERS = {
    "User-Agent": "JobFinderAI/1.0 (https://github.com/your-repo)",
    "Accept": "application/json",
}

# Skills extraction patterns
SKILLS_PATTERNS = [
    r'\b(?:Python|JavaScript|Java|C\+\+|C#|Go|Rust|TypeScript|React|Angular|Vue|Node\.js|Django|Flask|FastAPI|AWS|Azure|GCP|Docker|Kubernetes|SQL|MongoDB|PostgreSQL|Redis|Git|Linux|Agile|Scrum)\b',
    r'\b(?:Frontend|Backend|Full Stack|DevOps|Data Science|Machine Learning|AI|ML|UI/UX|Product Manager|Project Manager|QA|Testing|Analytics|Business Intelligence)\b'
]

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from job description text.
    
    Args:
        text: Job description or requirements text
        
    Returns:
        List of extracted skills
    """
    if not text:
        return []
    
    skills = set()
    text_lower = text.lower()
    
    for pattern in SKILLS_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(match.lower() for match in matches)
    
    return list(skills)

def normalize_remotive_job(raw_job: Dict[str, Any]) -> Job:
    """
    Normalize a raw job from Remotive API to our Job model.
    
    Args:
        raw_job: Raw job data from Remotive API
        
    Returns:
        Normalized Job object
    """
    try:
        # Extract and clean job data
        job_id = str(raw_job.get("id", ""))
        title = raw_job.get("title", "").strip()
        company_name = raw_job.get("company_name", "").strip()
        location = raw_job.get("candidate_required_location", "Remote")
        description = raw_job.get("description", "").strip()
        url = raw_job.get("url", "").strip()
        
        # Parse salary information
        salary_range = None
        salary_text = raw_job.get("salary", "")
        if salary_text and salary_text.lower() not in ["", "n/a", "not specified"]:
            salary_range = salary_text.strip()
        
        # Parse posted date
        posted_date = datetime.now()  # Remotive doesn't always provide exact dates
        if raw_job.get("publication_date"):
            try:
                posted_date = datetime.fromisoformat(raw_job["publication_date"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date for job {job_id}: {raw_job.get('publication_date')}")
        
        # Extract skills from description
        required_skills = extract_skills_from_text(description)
        
        # Add job category as a skill if available
        category = raw_job.get("category", "")
        if category and category.lower() not in [skill.lower() for skill in required_skills]:
            required_skills.append(category)
        
        return Job(
            id=f"remotive_{job_id}",
            title=title,
            company_name=company_name,
            location=location,
            description=description,
            salary_range=salary_range,
            required_skills=required_skills,
            source_platform="remotive",
            posted_date=posted_date,
            url=url
        )
        
    except Exception as e:
        logger.error(f"Error normalizing Remotive job {raw_job.get('id', 'unknown')}: {e}")
        raise

async def fetch_jobs(query: str, limit: int = 50) -> List[Job]:
    """
    Fetch jobs from Remotive.io API based on search query.
    
    Args:
        query: Search query for jobs
        limit: Maximum number of jobs to fetch (default: 50)
        
    Returns:
        List of normalized Job objects
        
    Raises:
        Exception: If API request fails or data cannot be processed
    """
    logger.info(f"Fetching jobs from Remotive.io with query: '{query}'")
    
    try:
        # Prepare request parameters
        params = {
            "search": query,
            "limit": min(limit, 100)  # Remotive API limit
        }
        
        async with aiohttp.ClientSession(headers=DEFAULT_HEADERS) as session:
            async with session.get(REMOTIVE_JOBS_ENDPOINT, params=params) as response:
                if response.status != 200:
                    error_msg = f"Remotive API returned status {response.status}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                data = await response.json()
                
                if not isinstance(data, dict) or "jobs" not in data:
                    logger.error("Invalid response format from Remotive API")
                    raise Exception("Invalid response format from Remotive API")
                
                jobs_data = data["jobs"]
                if not isinstance(jobs_data, list):
                    logger.error("Jobs data is not a list")
                    raise Exception("Jobs data is not a list")
                
                # Normalize jobs
                normalized_jobs = []
                for raw_job in jobs_data:
                    try:
                        normalized_job = normalize_remotive_job(raw_job)
                        normalized_jobs.append(normalized_job)
                    except Exception as e:
                        logger.warning(f"Skipping job due to normalization error: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(normalized_jobs)} jobs from Remotive.io")
                return normalized_jobs
                
    except aiohttp.ClientError as e:
        error_msg = f"Network error while fetching from Remotive: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while fetching from Remotive: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)

# For testing purposes
if __name__ == "__main__":
    async def test_fetch():
        try:
            jobs = await fetch_jobs("python developer")
            print(f"Fetched {len(jobs)} jobs")
            for job in jobs[:3]:
                print(f"- {job.title} at {job.company_name}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test_fetch()) 