# Job ingestion pipelines package
# Contains modules for orchestrating job data collection from multiple sources

from .job_ingestor import ingest_all_sources

__all__ = ["ingest_all_sources"] 