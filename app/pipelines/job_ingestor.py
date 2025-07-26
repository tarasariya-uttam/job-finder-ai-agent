"""
Central job ingestion pipeline for collecting jobs from multiple sources.

This module orchestrates the fetching of job data from various providers,
handles errors gracefully, and provides a unified interface for job ingestion.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from app.models.models import Job
from app.providers.remotive_client import fetch_jobs as fetch_remotive_jobs
from app.providers.adzuna_client import fetch_jobs as fetch_adzuna_jobs

# Configure logging
logger = logging.getLogger(__name__)

class JobIngestionResult:
    """Result object for job ingestion operations."""
    
    def __init__(self):
        self.jobs: List[Job] = []
        self.errors: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {
            "total_jobs": 0,
            "remotive_jobs": 0,
            "adzuna_jobs": 0,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0
        }
    
    def add_jobs(self, jobs: List[Job], source: str):
        """Add jobs from a specific source."""
        self.jobs.extend(jobs)
        self.stats[f"{source}_jobs"] = len(jobs)
        self.stats["total_jobs"] = len(self.jobs)
    
    def add_error(self, source: str, error: Exception):
        """Add an error from a specific source."""
        error_info = {
            "source": source,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_info)
        logger.error(f"Error fetching from {source}: {error}")

async def fetch_from_remotive(query: str, limit: int = 25) -> List[Job]:
    """
    Fetch jobs from Remotive.io with error handling.
    
    Args:
        query: Search query
        limit: Maximum number of jobs to fetch
        
    Returns:
        List of jobs from Remotive
    """
    try:
        logger.info(f"Starting Remotive.io job fetch for query: '{query}'")
        jobs = await fetch_remotive_jobs(query, limit)
        logger.info(f"Successfully fetched {len(jobs)} jobs from Remotive.io")
        return jobs
    except Exception as e:
        logger.error(f"Failed to fetch jobs from Remotive.io: {e}")
        raise

async def fetch_from_adzuna(query: str, limit: int = 25) -> List[Job]:
    """
    Fetch jobs from Adzuna with error handling.
    
    Args:
        query: Search query
        limit: Maximum number of jobs to fetch
        
    Returns:
        List of jobs from Adzuna
    """
    try:
        logger.info(f"Starting Adzuna job fetch for query: '{query}'")
        jobs = await fetch_adzuna_jobs(query, limit)
        logger.info(f"Successfully fetched {len(jobs)} jobs from Adzuna")
        return jobs
    except Exception as e:
        logger.error(f"Failed to fetch jobs from Adzuna: {e}")
        raise

async def ingest_all_sources(query: str, limit_per_source: int = 25) -> JobIngestionResult:
    """
    Fetch jobs from all available sources concurrently.
    
    This function fetches jobs from multiple providers in parallel,
    handles errors gracefully, and returns a comprehensive result object.
    
    Args:
        query: Search query for jobs
        limit_per_source: Maximum number of jobs to fetch from each source
        
    Returns:
        JobIngestionResult containing all jobs and error information
    """
    logger.info(f"Starting job ingestion for query: '{query}' from all sources")
    
    result = JobIngestionResult()
    result.stats["start_time"] = datetime.now()
    
    # Define the sources to fetch from
    sources = [
        ("remotive", fetch_from_remotive),
        ("adzuna", fetch_from_adzuna)
    ]
    
    # Create tasks for concurrent execution
    tasks = []
    for source_name, fetch_func in sources:
        task = asyncio.create_task(
            fetch_func(query, limit_per_source),
            name=f"fetch_{source_name}"
        )
        tasks.append((source_name, task))
    
    # Execute all tasks concurrently
    for source_name, task in tasks:
        try:
            jobs = await task
            result.add_jobs(jobs, source_name)
            logger.info(f"Successfully processed {len(jobs)} jobs from {source_name}")
        except Exception as e:
            result.add_error(source_name, e)
            logger.error(f"Failed to fetch from {source_name}: {e}")
    
    # Calculate final statistics
    result.stats["end_time"] = datetime.now()
    duration = (result.stats["end_time"] - result.stats["start_time"]).total_seconds()
    result.stats["duration_seconds"] = duration
    
    # Log summary
    logger.info(f"Job ingestion completed:")
    logger.info(f"  Total jobs: {result.stats['total_jobs']}")
    logger.info(f"  Remotive jobs: {result.stats['remotive_jobs']}")
    logger.info(f"  Adzuna jobs: {result.stats['adzuna_jobs']}")
    logger.info(f"  Errors: {len(result.errors)}")
    logger.info(f"  Duration: {duration:.2f} seconds")
    
    return result

async def ingest_sources_sequentially(query: str, limit_per_source: int = 25) -> JobIngestionResult:
    """
    Fetch jobs from all sources sequentially (alternative to concurrent approach).
    
    This function fetches jobs from providers one at a time,
    which can be useful for debugging or when rate limiting is a concern.
    
    Args:
        query: Search query for jobs
        limit_per_source: Maximum number of jobs to fetch from each source
        
    Returns:
        JobIngestionResult containing all jobs and error information
    """
    logger.info(f"Starting sequential job ingestion for query: '{query}'")
    
    result = JobIngestionResult()
    result.stats["start_time"] = datetime.now()
    
    # Define the sources to fetch from
    sources = [
        ("remotive", fetch_from_remotive),
        ("adzuna", fetch_from_adzuna)
    ]
    
    # Execute sources sequentially
    for source_name, fetch_func in sources:
        try:
            jobs = await fetch_func(query, limit_per_source)
            result.add_jobs(jobs, source_name)
            logger.info(f"Successfully processed {len(jobs)} jobs from {source_name}")
        except Exception as e:
            result.add_error(source_name, e)
            logger.error(f"Failed to fetch from {source_name}: {e}")
    
    # Calculate final statistics
    result.stats["end_time"] = datetime.now()
    duration = (result.stats["end_time"] - result.stats["start_time"]).total_seconds()
    result.stats["duration_seconds"] = duration
    
    logger.info(f"Sequential job ingestion completed in {duration:.2f} seconds")
    return result

def deduplicate_jobs(jobs: List[Job]) -> List[Job]:
    """
    Remove duplicate jobs based on title and company name.
    
    Args:
        jobs: List of jobs to deduplicate
        
    Returns:
        List of unique jobs
    """
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        # Create a unique identifier based on title and company
        identifier = f"{job.title.lower().strip()}_{job.company_name.lower().strip()}"
        
        if identifier not in seen:
            seen.add(identifier)
            unique_jobs.append(job)
    
    logger.info(f"Deduplication: {len(jobs)} jobs -> {len(unique_jobs)} unique jobs")
    return unique_jobs

# For testing purposes
if __name__ == "__main__":
    async def test_ingestion():
        try:
            result = await ingest_all_sources("python developer", limit_per_source=10)
            print(f"Fetched {result.stats['total_jobs']} total jobs")
            print(f"Errors: {len(result.errors)}")
            
            # Show first few jobs
            for i, job in enumerate(result.jobs[:3]):
                print(f"{i+1}. {job.title} at {job.company_name} ({job.source_platform})")
                
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test_ingestion()) 