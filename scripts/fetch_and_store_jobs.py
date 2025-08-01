#!/usr/bin/env python3
"""
Sample script to demonstrate job ingestion from multiple sources.

This script fetches jobs from Remotive.io and Adzuna, displays the results,
and saves them to storage for later scoring.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipelines.job_ingestor import ingest_all_sources, deduplicate_jobs
from app.models.models import Job
from app.utils.job_storage import save_jobs, append_jobs

def print_job_summary(job: Job, index: int) -> None:
    """
    Print a formatted summary of a job.
    
    Args:
        job: Job object to display
        index: Index number for display
    """
    print(f"\n{index}. {job.title}")
    print(f"   Company: {job.company_name}")
    print(f"   Location: {job.location}")
    print(f"   Source: {job.source_platform}")
    print(f"   Posted: {job.posted_date.strftime('%Y-%m-%d')}")
    if job.salary_range:
        print(f"   Salary: {job.salary_range}")
    if job.required_skills:
        print(f"   Skills: {', '.join(job.required_skills[:5])}{'...' if len(job.required_skills) > 5 else ''}")
    print(f"   URL: {job.url}")

def job_to_dict(job: Job) -> Dict[str, Any]:
    """
    Convert a Job object to a dictionary for JSON serialization.
    
    Args:
        job: Job object to convert
        
    Returns:
        Dictionary representation of the job
    """
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "location": job.location,
        "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
        "salary_range": job.salary_range,
        "required_skills": job.required_skills,
        "source_platform": job.source_platform,
        "posted_date": job.posted_date.isoformat(),
        "url": job.url
    }

async def main():
    """
    Main function to demonstrate job ingestion.
    """
    print("🚀 Job Finder AI Agent - Job Ingestion Demo")
    print("=" * 50)
    
    # Get search queries from command line or use default
    queries_input = sys.argv[1] if len(sys.argv) > 1 else "python developer"
    limit_per_source = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # Split queries by comma and clean them
    queries = [query.strip() for query in queries_input.split(",")]
    
    print(f"Searching for: {', '.join(queries)}")
    print(f"Limit per source: {limit_per_source}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        # Fetch jobs from all sources for all queries
        print("📡 Fetching jobs from all sources for all queries...")
        all_jobs = []
        all_errors = []
        total_stats = {
            "total_jobs": 0,
            "remotive_jobs": 0,
            "adzuna_jobs": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "duration_seconds": 0
        }
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 Processing query {i}/{len(queries)}: '{query}'")
            result = await ingest_all_sources(query, limit_per_source)
            
            # Collect jobs and errors
            all_jobs.extend(result.jobs)
            all_errors.extend(result.errors)
            
            # Update stats
            total_stats["remotive_jobs"] += result.stats["remotive_jobs"]
            total_stats["adzuna_jobs"] += result.stats["adzuna_jobs"]
            
            print(f"   ✅ Found {len(result.jobs)} jobs for '{query}'")
        
        # Calculate final stats
        total_stats["end_time"] = datetime.now()
        duration = (total_stats["end_time"] - total_stats["start_time"]).total_seconds()
        total_stats["duration_seconds"] = duration
        total_stats["total_jobs"] = len(all_jobs)
        
        # Display statistics
        print(f"\n📊 Ingestion Statistics:")
        print(f"   Total jobs fetched: {total_stats['total_jobs']}")
        print(f"   Remotive jobs: {total_stats['remotive_jobs']}")
        print(f"   Adzuna jobs: {total_stats['adzuna_jobs']}")
        print(f"   Errors encountered: {len(all_errors)}")
        print(f"   Duration: {total_stats['duration_seconds']:.2f} seconds")
        
        # Display errors if any
        if all_errors:
            print(f"\n❌ Errors encountered:")
            for error in all_errors:
                print(f"   {error['source']}: {error['error']}")
        
        # Deduplicate jobs
        unique_jobs = deduplicate_jobs(all_jobs)
        print(f"\n🔄 Deduplication: {len(all_jobs)} -> {len(unique_jobs)} unique jobs")
        
        # Display first 3 jobs
        if unique_jobs:
            print(f"\n📋 First 3 Job Results:")
            for i, job in enumerate(unique_jobs[:3], 1):
                print_job_summary(job, i)
            
            # Convert to dictionaries for JSON output
            job_dicts = [job_to_dict(job) for job in unique_jobs[:3]]
            
            print(f"\n📄 JSON Output (first 3 jobs):")
            print(json.dumps(job_dicts, indent=2, ensure_ascii=False))
            
            # Save jobs to storage
            print(f"\n💾 Saving jobs to storage...")
            metadata = {
                "queries": queries,
                "limit_per_source": limit_per_source,
                "total_queries": len(queries),
                "fetch_timestamp": datetime.now().isoformat()
            }
            
            # Save all jobs (this will replace existing jobs)
            success = save_jobs(unique_jobs, metadata)
            
            if success:
                print(f"   ✅ Successfully saved {len(unique_jobs)} jobs to storage")
                print(f"   📁 Storage location: data/fetched_jobs.json")
            else:
                print(f"   ❌ Failed to save jobs to storage")
            
            print(f"   Sample job ID: {unique_jobs[0].id if unique_jobs else 'N/A'}")
                
        else:
            print("\n❌ No jobs found. This could be due to:")
            print("   - API rate limiting")
            print("   - Network connectivity issues")
            print("   - Invalid search query")
            print("   - API credentials not configured (for Adzuna)")
        
        print(f"\n✅ Job ingestion demo completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set up basic logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the main function
    asyncio.run(main()) 