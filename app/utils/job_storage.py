"""
Job storage utility for persisting and retrieving job data.

This module provides functionality to store fetched jobs in JSON format
and retrieve them for scoring and analysis.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from app.models.models import Job

# Configure logging
logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_DIR = "data"
JOBS_FILE = "fetched_jobs.json"
JOBS_BACKUP_DIR = "data/backups"

class JobStorage:
    """Handles storage and retrieval of job data."""
    
    def __init__(self, storage_dir: str = STORAGE_DIR):
        self.storage_dir = storage_dir
        self.jobs_file = os.path.join(storage_dir, JOBS_FILE)
        self.backup_dir = os.path.join(storage_dir, "backups")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create storage directories if they don't exist."""
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_jobs(self, jobs: List[Job], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save jobs to JSON file with metadata.
        
        Args:
            jobs: List of Job objects to save
            metadata: Optional metadata about the job fetch (query, timestamp, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert jobs to dictionaries with datetime handling
            jobs_data = []
            for job in jobs:
                job_dict = job.model_dump()
                # Convert datetime to ISO string for JSON serialization
                if "posted_date" in job_dict and job_dict["posted_date"]:
                    job_dict["posted_date"] = job_dict["posted_date"].isoformat()
                jobs_data.append(job_dict)
            
            # Create storage object with metadata
            storage_data = {
                "metadata": metadata or {},
                "jobs": jobs_data,
                "total_jobs": len(jobs),
                "saved_at": datetime.now().isoformat()
            }
            
            # Create backup of existing file if it exists
            if os.path.exists(self.jobs_file):
                self._create_backup()
            
            # Save to file
            with open(self.jobs_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved {len(jobs)} jobs to {self.jobs_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
            return False
    
    def load_jobs(self) -> List[Job]:
        """
        Load jobs from JSON file.
        
        Returns:
            List of Job objects
        """
        try:
            if not os.path.exists(self.jobs_file):
                logger.warning(f"Jobs file not found: {self.jobs_file}")
                return []
            
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
            
            # Convert dictionaries back to Job objects
            jobs = []
            for job_data in storage_data.get("jobs", []):
                try:
                    # Handle datetime conversion
                    if "posted_date" in job_data:
                        job_data["posted_date"] = datetime.fromisoformat(job_data["posted_date"])
                    job = Job(**job_data)
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"Error parsing job data: {e}")
                    continue
            
            logger.info(f"Successfully loaded {len(jobs)} jobs from {self.jobs_file}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error loading jobs: {e}")
            return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about stored jobs.
        
        Returns:
            Dictionary containing metadata
        """
        try:
            if not os.path.exists(self.jobs_file):
                return {}
            
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
            
            return storage_data.get("metadata", {})
            
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def append_jobs(self, new_jobs: List[Job], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Append new jobs to existing storage (with deduplication).
        
        Args:
            new_jobs: List of new Job objects to append
            metadata: Optional metadata about the new jobs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing jobs
            existing_jobs = self.load_jobs()
            
            # Create set of existing job IDs for deduplication
            existing_ids = {job.id for job in existing_jobs}
            
            # Filter out duplicates
            unique_new_jobs = [job for job in new_jobs if job.id not in existing_ids]
            
            if not unique_new_jobs:
                logger.info("No new unique jobs to append")
                return True
            
            # Combine jobs
            all_jobs = existing_jobs + unique_new_jobs
            
            # Update metadata
            current_metadata = self.get_metadata()
            if metadata:
                current_metadata.update(metadata)
            current_metadata["last_updated"] = datetime.now().isoformat()
            current_metadata["total_unique_jobs"] = len(all_jobs)
            
            # Save combined jobs
            return self.save_jobs(all_jobs, current_metadata)
            
        except Exception as e:
            logger.error(f"Error appending jobs: {e}")
            return False
    
    def _create_backup(self):
        """Create a backup of the current jobs file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"jobs_backup_{timestamp}.json")
            
            with open(self.jobs_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            logger.info(f"Created backup: {backup_file}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def clear_storage(self) -> bool:
        """
        Clear all stored jobs.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.jobs_file):
                os.remove(self.jobs_file)
                logger.info("Cleared job storage")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored jobs.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            jobs = self.load_jobs()
            metadata = self.get_metadata()
            
            # Count jobs by source
            source_counts = {}
            for job in jobs:
                source = job.source_platform
                source_counts[source] = source_counts.get(source, 0) + 1
            
            stats = {
                "total_jobs": len(jobs),
                "jobs_by_source": source_counts,
                "metadata": metadata,
                "storage_file": self.jobs_file,
                "file_size_mb": round(os.path.getsize(self.jobs_file) / (1024 * 1024), 2) if os.path.exists(self.jobs_file) else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}

# Convenience functions
def save_jobs(jobs: List[Job], metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to save jobs."""
    storage = JobStorage()
    return storage.save_jobs(jobs, metadata)

def load_jobs() -> List[Job]:
    """Convenience function to load jobs."""
    storage = JobStorage()
    return storage.load_jobs()

def append_jobs(new_jobs: List[Job], metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to append jobs."""
    storage = JobStorage()
    return storage.append_jobs(new_jobs, metadata)

def save_resume(resume_data, metadata=None):
    """
    Save parsed resume data to data/parsed_resume.json.
    Args:
        resume_data: ResumeData object (or dict)
        metadata: Optional dict with additional info (e.g., source file, timestamp)
    Returns:
        bool: True if saved successfully, False otherwise
    """
    import os
    import json
    from datetime import datetime
    
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", "parsed_resume.json")
    try:
        # Convert to dict if needed
        if hasattr(resume_data, 'model_dump'):
            data = resume_data.model_dump()
        elif hasattr(resume_data, '__dict__'):
            data = dict(resume_data.__dict__)
        else:
            data = dict(resume_data)
        
        storage = {
            "metadata": metadata or {},
            "resume": data,
            "saved_at": datetime.now().isoformat()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(storage, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[save_resume] Error: {e}")
        return False

# For testing
if __name__ == "__main__":
    # Test the storage system
    storage = JobStorage()
    
    # Test stats
    stats = storage.get_storage_stats()
    print("Storage Stats:", json.dumps(stats, indent=2))
    
    # Test loading
    jobs = storage.load_jobs()
    print(f"Loaded {len(jobs)} jobs") 