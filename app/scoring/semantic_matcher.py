"""
Semantic Similarity Scoring Module using Sentence-BERT
Computes semantic similarity between resume and job descriptions.
"""

import functools
import re
from typing import Optional, List
import numpy as np
from sentence_transformers import SentenceTransformer, util


# Global model cache to avoid reloading
_model_cache = None


@functools.lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """
    Get the Sentence-BERT model with caching to avoid reloading.
    Uses 'paraphrase-MiniLM-L6-v2' model for fast inference and good semantic similarity.
    """
    global _model_cache
    if _model_cache is None:
        print("🔄 Loading Sentence-BERT model (paraphrase-MiniLM-L6-v2)...")
        try:
            _model_cache = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not load model: {e}")
            print("🔄 Falling back to basic similarity calculation...")
            _model_cache = None
    return _model_cache


def compute_semantic_similarity(resume_text: str, job_text: str) -> float:
    """
    Uses Sentence-BERT to compute cosine similarity between a resume and job description.
    
    Args:
        resume_text: Text content from the resume (skills, experience, education, etc.)
        job_text: Job description and requirements text
        
    Returns:
        float: Similarity score between 0.0 and 1.0 (e.g., 0.83 = 83% match)
        
    Raises:
        ValueError: If inputs are empty or invalid
    """
    try:
        # Input validation
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text cannot be empty")
        if not job_text or not job_text.strip():
            raise ValueError("Job text cannot be empty")
        
        # Clean and normalize text
        resume_clean = resume_text.strip()
        job_clean = job_text.strip()
        
        # Get the model
        model = _get_model()
        
        # If model failed to load, use basic keyword similarity
        if model is None:
            return _compute_basic_similarity(resume_clean, job_clean)
        
        # Encode texts to embeddings
        resume_embedding = model.encode(resume_clean, convert_to_tensor=True)
        job_embedding = model.encode(job_clean, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity_score = util.cos_sim(resume_embedding, job_embedding)
        
        # Convert to float and ensure it's between 0 and 1
        score = float(similarity_score.item())
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
        
    except Exception as e:
        print(f"❌ Error computing semantic similarity: {e}")
        return _compute_basic_similarity(resume_text, job_text)


def _compute_basic_similarity(resume_text: str, job_text: str) -> float:
    """
    Compute basic keyword-based similarity as fallback when BERT model is unavailable.
    """
    try:
        # Convert to lowercase for comparison
        resume_lower = resume_text.lower()
        job_lower = job_text.lower()
        
        # Extract words
        resume_words = set(re.findall(r'\b\w+\b', resume_lower))
        job_words = set(re.findall(r'\b\w+\b', job_lower))
        
        if not resume_words or not job_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(resume_words & job_words)
        union = len(resume_words | job_words)
        
        if union == 0:
            return 0.0
        
        similarity = intersection / union
        
        # Boost similarity for important keywords
        important_keywords = ['python', 'machine learning', 'data science', 'aws', 'sql', 'docker', 'git']
        keyword_matches = sum(1 for keyword in important_keywords if keyword in resume_lower and keyword in job_lower)
        
        # Add bonus for keyword matches
        bonus = min(0.2, keyword_matches * 0.05)
        
        return min(1.0, similarity + bonus)
        
    except Exception as e:
        print(f"❌ Error computing basic similarity: {e}")
        return 0.0


def compute_semantic_similarity_batch(resume_text: str, job_texts: List[str]) -> List[float]:
    """
    Compute semantic similarity between resume and multiple job descriptions.
    
    Args:
        resume_text: Text content from the resume
        job_texts: List of job description texts
        
    Returns:
        list[float]: List of similarity scores for each job
    """
    try:
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text cannot be empty")
        if not job_texts:
            return []
        
        # Clean inputs
        resume_clean = resume_text.strip()
        job_texts_clean = [text.strip() for text in job_texts if text and text.strip()]
        
        if not job_texts_clean:
            return []
        
        # Get the model
        model = _get_model()
        
        # If model failed to load, use basic similarity for each job
        if model is None:
            return [_compute_basic_similarity(resume_clean, job_text) for job_text in job_texts_clean]
        
        # Encode resume
        resume_embedding = model.encode(resume_clean, convert_to_tensor=True)
        
        # Encode all job texts
        job_embeddings = model.encode(job_texts_clean, convert_to_tensor=True)
        
        # Compute cosine similarities
        similarities = util.cos_sim(resume_embedding, job_embeddings)
        
        # Convert to list of floats
        scores = [max(0.0, min(1.0, float(score.item()))) for score in similarities[0]]
        return scores
        
    except Exception as e:
        print(f"❌ Error computing batch semantic similarity: {e}")
        # Fallback to basic similarity
        return [_compute_basic_similarity(resume_text, job_text) for job_text in job_texts]


def extract_resume_text_for_semantic_matching(resume_data: dict) -> str:
    """
    Extract and combine relevant text from resume data for semantic matching.
    
    Args:
        resume_data: Parsed resume data dictionary
        
    Returns:
        str: Combined text for semantic matching
    """
    text_parts = []
    
    # Add skills
    skills = resume_data.get('skills', [])
    if skills:
        text_parts.append(f"Skills: {', '.join(skills)}")
    
    # Add experience
    experience = resume_data.get('experience', [])
    for exp in experience:
        title = exp.get('title', '')
        company = exp.get('company', '')
        description = exp.get('description', '')
        if title or company or description:
            exp_text = f"Experience: {title} at {company}. {description}"
            text_parts.append(exp_text)
    
    # Add education
    education = resume_data.get('education', [])
    for edu in education:
        degree = edu.get('degree', '')
        institution = edu.get('institution', '')
        if degree or institution:
            edu_text = f"Education: {degree} from {institution}"
            text_parts.append(edu_text)
    
    # Add projects
    projects = resume_data.get('projects', [])
    for project in projects:
        name = project.get('name', '')
        description = project.get('description', '')
        technologies = project.get('technologies', [])
        if name or description or technologies:
            proj_text = f"Project: {name}. {description}. Technologies: {', '.join(technologies)}"
            text_parts.append(proj_text)
    
    # Add certifications
    certifications = resume_data.get('certifications', [])
    for cert in certifications:
        name = cert.get('name', '')
        issuer = cert.get('issuer', '')
        if name or issuer:
            cert_text = f"Certification: {name} from {issuer}"
            text_parts.append(cert_text)
    
    # Add summary
    summary = resume_data.get('summary', '')
    if summary:
        text_parts.append(f"Summary: {summary}")
    
    return " ".join(text_parts)


def extract_job_text_for_semantic_matching(job_data: dict) -> str:
    """
    Extract and combine relevant text from job data for semantic matching.
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        str: Combined text for semantic matching
    """
    text_parts = []
    
    # Add job title
    title = job_data.get('title', '')
    if title:
        text_parts.append(f"Job Title: {title}")
    
    # Add job description
    description = job_data.get('description', '')
    if description:
        text_parts.append(f"Job Description: {description}")
    
    # Add required skills
    skills = job_data.get('required_skills', [])
    if skills:
        text_parts.append(f"Required Skills: {', '.join(skills)}")
    
    # Add company name
    company = job_data.get('company_name', '')
    if company:
        text_parts.append(f"Company: {company}")
    
    # Add location
    location = job_data.get('location', '')
    if location:
        text_parts.append(f"Location: {location}")
    
    return " ".join(text_parts)


if __name__ == "__main__":
    # Test the semantic similarity function
    print("🧪 Testing Semantic Similarity Module")
    print("=" * 50)
    
    # Sample resume text
    resume_text = """
    Skills: Python, Machine Learning, Data Science, SQL, AWS, Docker
    Experience: Senior Data Scientist at TechCorp. Built ML models for customer segmentation.
    Education: Master's in Computer Science from University of Technology
    Projects: Customer Churn Prediction using Python and scikit-learn. Technologies: Python, Pandas, Scikit-learn
    Summary: Experienced data scientist with 5 years in machine learning and analytics
    """
    
    # Sample job descriptions
    job_descriptions = [
        "We are looking for a Python Developer with experience in machine learning and data science. Must know SQL and cloud platforms like AWS.",
        "Senior Software Engineer needed for web development. Experience with JavaScript, React, and Node.js required.",
        "Data Scientist position available. Looking for someone with Python, machine learning, and statistical analysis skills. Experience with customer analytics preferred."
    ]
    
    print(f"📄 Resume Text: {resume_text[:100]}...")
    print()
    
    for i, job_desc in enumerate(job_descriptions, 1):
        similarity = compute_semantic_similarity(resume_text, job_desc)
        print(f"🎯 Job {i} Similarity: {similarity:.1%}")
        print(f"   Job Description: {job_desc[:80]}...")
        print()
    
    print("✅ Semantic similarity test completed!") 