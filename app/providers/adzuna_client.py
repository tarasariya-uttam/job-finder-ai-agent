"""
Adzuna API client for fetching job listings.

This module provides functionality to fetch and normalize job data from Adzuna,
a comprehensive job search platform with global coverage.
"""

import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import os

from app.models.models import Job

# Configure logging
logger = logging.getLogger(__name__)

# Adzuna API configuration
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api"
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "your-app-id")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "your-api-key")

# Default country and location for Adzuna API
DEFAULT_COUNTRY = "gb"  # Great Britain
DEFAULT_LOCATION = "london"

# Default headers for API requests
DEFAULT_HEADERS = {
    "User-Agent": "JobFinderAI/1.0 (https://github.com/your-repo)",
    "Accept": "application/json",
}

# Skills extraction patterns (same as Remotive for consistency)
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

def parse_salary_range(salary_min: Optional[str], salary_max: Optional[str], currency: str = "GBP") -> Optional[str]:
    """
    Parse and format salary range from Adzuna data.
    
    Args:
        salary_min: Minimum salary
        salary_max: Maximum salary
        currency: Currency code
        
    Returns:
        Formatted salary range string or None
    """
    if not salary_min and not salary_max:
        return None
    
    try:
        min_val = float(salary_min) if salary_min else None
        max_val = float(salary_max) if salary_max else None
        
        if min_val and max_val:
            return f"{currency} {min_val:,.0f} - {max_val:,.0f}"
        elif min_val:
            return f"{currency} {min_val:,.0f}+"
        elif max_val:
            return f"Up to {currency} {max_val:,.0f}"
        else:
            return None
    except (ValueError, TypeError):
        return None

def normalize_adzuna_job(raw_job: Dict[str, Any]) -> Job:
    """
    Normalize a raw job from Adzuna API to our Job model.
    
    Args:
        raw_job: Raw job data from Adzuna API
        
    Returns:
        Normalized Job object
    """
    try:
        # Extract and clean job data
        job_id = str(raw_job.get("id", ""))
        title = raw_job.get("title", "").strip()
        company_name = raw_job.get("company", {}).get("display_name", "").strip()
        location = raw_job.get("location", {}).get("display_name", "Unknown")
        description = raw_job.get("description", "").strip()
        url = raw_job.get("redirect_url", "").strip()
        
        # Parse salary information
        salary_range = parse_salary_range(
            raw_job.get("salary_min"),
            raw_job.get("salary_max"),
            raw_job.get("salary_currency", "GBP")
        )
        
        # Parse posted date
        posted_date = datetime.now()
        if raw_job.get("created"):
            try:
                posted_date = datetime.fromisoformat(raw_job["created"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date for job {job_id}: {raw_job.get('created')}")
        
        # Extract skills from description and category
        required_skills = extract_skills_from_text(description)
        
        # Add job category as a skill if available
        category = raw_job.get("category", {}).get("label", "")
        if category and category.lower() not in [skill.lower() for skill in required_skills]:
            required_skills.append(category)
        
        # Add contract type as a skill if relevant
        contract_type = raw_job.get("contract_time", "")
        if contract_type and contract_type.lower() not in [skill.lower() for skill in required_skills]:
            required_skills.append(contract_type)
        
        return Job(
            id=f"adzuna_{job_id}",
            title=title,
            company_name=company_name,
            location=location,
            description=description,
            salary_range=salary_range,
            required_skills=required_skills,
            source_platform="adzuna",
            posted_date=posted_date,
            url=url
        )
        
    except Exception as e:
        logger.error(f"Error normalizing Adzuna job {raw_job.get('id', 'unknown')}: {e}")
        raise

async def fetch_jobs(query: str, limit: int = 50, country: str = DEFAULT_COUNTRY) -> List[Job]:
    """
    Fetch jobs from Adzuna API based on search query.
    
    Args:
        query: Search query for jobs
        limit: Maximum number of jobs to fetch (default: 50)
        country: Country code for Adzuna API (default: "gb")
        
    Returns:
        List of normalized Job objects
        
    Raises:
        Exception: If API request fails or data cannot be processed
    """
    logger.info(f"Fetching jobs from Adzuna with query: '{query}' in country: {country}")
    
    # Check if API credentials are configured
    if ADZUNA_APP_ID == "your-app-id" or ADZUNA_API_KEY == "your-api-key":
        logger.warning("Adzuna API credentials not configured. Please set ADZUNA_APP_ID and ADZUNA_API_KEY environment variables.")
        return []
    
    try:
        # Prepare request parameters
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "results_per_page": min(limit, 50),  # Adzuna API limit
            "what": query,
            "content-type": "application/json"
        }
        
        # Construct API URL
        api_url = f"{ADZUNA_BASE_URL}/jobs/{country}/search/1"
        
        async with aiohttp.ClientSession(headers=DEFAULT_HEADERS) as session:
            async with session.get(api_url, params=params) as response:
                if response.status != 200:
                    error_msg = f"Adzuna API returned status {response.status}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                data = await response.json()
                
                if not isinstance(data, dict) or "results" not in data:
                    logger.error("Invalid response format from Adzuna API")
                    raise Exception("Invalid response format from Adzuna API")
                
                jobs_data = data["results"]
                if not isinstance(jobs_data, list):
                    logger.error("Jobs data is not a list")
                    raise Exception("Jobs data is not a list")
                
                # Normalize jobs
                normalized_jobs = []
                for raw_job in jobs_data:
                    try:
                        normalized_job = normalize_adzuna_job(raw_job)
                        normalized_jobs.append(normalized_job)
                    except Exception as e:
                        logger.warning(f"Skipping job due to normalization error: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(normalized_jobs)} jobs from Adzuna")
                return normalized_jobs
                
    except aiohttp.ClientError as e:
        error_msg = f"Network error while fetching from Adzuna: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while fetching from Adzuna: {e}"
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