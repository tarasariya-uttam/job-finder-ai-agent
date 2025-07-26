from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class Job(BaseModel):
    id: str
    title: str
    company_name: str
    location: str
    description: str
    salary_range: Optional[str]
    required_skills: List[str]
    source_platform: Literal["linkedin", "indeed", "monster", "remotive", "adzuna", "other"]
    posted_date: datetime
    url: str

class Candidate(BaseModel):
    id: str
    full_name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    current_position: Optional[str]
    skills: List[str]
    preferences: Dict[str, Any]

class Resume(BaseModel):
    id: str
    candidate_id: str
    content: str
    parsed_skills: List[str]
    parsed_experience: List[str]
    parsed_education: List[str]
    uploaded_at: datetime
    file_url: Optional[str]

class Application(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    resume_id: str
    cover_letter: str
    status: Literal["pending", "submitted", "failed", "interview", "rejected"]
    applied_at: datetime
    platform_response: Optional[str]
