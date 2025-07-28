#!/usr/bin/env python3
"""
Test script for semantic similarity matching using Sentence-BERT.
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scoring.semantic_matcher import (
    compute_semantic_similarity,
    compute_semantic_similarity_batch,
    extract_resume_text_for_semantic_matching,
    extract_job_text_for_semantic_matching
)


def test_basic_semantic_similarity():
    """Test basic semantic similarity with sample texts."""
    print("🧪 Testing Basic Semantic Similarity")
    print("=" * 50)
    
    # Sample resume text
    resume_text = """
    Skills: Python, Machine Learning, Data Science, SQL, AWS, Docker, Git
    Experience: Senior Data Scientist at TechCorp for 3 years. Built ML models for customer segmentation and predictive analytics.
    Education: Master's in Computer Science from University of Technology
    Projects: Customer Churn Prediction using Python and scikit-learn. Technologies: Python, Pandas, Scikit-learn, SQL
    Summary: Experienced data scientist with 5 years in machine learning and analytics, specializing in Python and cloud platforms.
    """
    
    # Sample job descriptions with varying relevance
    job_descriptions = [
        {
            "title": "Senior Data Scientist",
            "description": "We are looking for a Senior Data Scientist with Python experience. Must have machine learning expertise and experience with cloud platforms like AWS. Knowledge of SQL and statistical analysis required.",
            "skills": ["Python", "Machine Learning", "AWS", "SQL", "Statistics"]
        },
        {
            "title": "Python Developer",
            "description": "Python developer needed for web application development. Experience with Django, Flask, and database design required. Knowledge of Git and deployment processes.",
            "skills": ["Python", "Django", "Flask", "SQL", "Git"]
        },
        {
            "title": "Frontend Developer",
            "description": "Frontend developer position available. Must have strong JavaScript skills, React experience, and knowledge of modern web development practices.",
            "skills": ["JavaScript", "React", "HTML", "CSS", "Web Development"]
        },
        {
            "title": "Machine Learning Engineer",
            "description": "ML Engineer position focusing on production machine learning systems. Python, TensorFlow, and cloud deployment experience required. Must understand data pipelines and model serving.",
            "skills": ["Python", "Machine Learning", "TensorFlow", "AWS", "Data Engineering"]
        }
    ]
    
    print(f"📄 Resume Text Preview: {resume_text[:150]}...")
    print()
    
    # Test each job description
    for i, job in enumerate(job_descriptions, 1):
        job_text = f"Job Title: {job['title']}. Job Description: {job['description']}. Required Skills: {', '.join(job['skills'])}"
        
        similarity = compute_semantic_similarity(resume_text, job_text)
        
        print(f"🎯 Job {i}: {job['title']}")
        print(f"   Semantic Match: {similarity:.1%}")
        print(f"   Description: {job['description'][:80]}...")
        print(f"   Skills: {', '.join(job['skills'])}")
        print()


def test_with_real_data():
    """Test semantic similarity with real parsed resume and job data."""
    print("🧪 Testing with Real Data")
    print("=" * 50)
    
    # Check if files exist
    resume_file = "data/parsed_resume.json"
    jobs_file = "data/fetched_jobs.json"
    
    if not os.path.exists(resume_file):
        print(f"❌ Resume file not found: {resume_file}")
        return
    
    if not os.path.exists(jobs_file):
        print(f"❌ Jobs file not found: {jobs_file}")
        return
    
    # Load resume data
    with open(resume_file, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    # Load jobs data
    with open(jobs_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    resume_info = resume_data.get('resume', {})
    jobs = jobs_data.get('jobs', [])
    
    if not jobs:
        print("❌ No jobs found in the jobs file")
        return
    
    # Extract resume text for semantic matching
    resume_text = extract_resume_text_for_semantic_matching(resume_info)
    
    print(f"📄 Resume Text Preview: {resume_text[:200]}...")
    print(f"📊 Total Jobs: {len(jobs)}")
    print()
    
    # Test with first 3 jobs
    test_jobs = jobs[:3]
    
    for i, job in enumerate(test_jobs, 1):
        job_text = extract_job_text_for_semantic_matching(job)
        similarity = compute_semantic_similarity(resume_text, job_text)
        
        print(f"🎯 Job {i}: {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company_name', 'N/A')}")
        print(f"   Semantic Match: {similarity:.1%}")
        print(f"   Current Score: {job.get('match_score', 'N/A')}")
        print(f"   Description: {job.get('description', 'N/A')[:100]}...")
        print()


def test_batch_similarity():
    """Test batch semantic similarity computation."""
    print("🧪 Testing Batch Semantic Similarity")
    print("=" * 50)
    
    # Sample resume text
    resume_text = "Python developer with machine learning experience. Skills include Python, SQL, AWS, and data analysis."
    
    # Multiple job descriptions
    job_descriptions = [
        "Python developer needed for web development",
        "Data scientist position requiring machine learning skills",
        "Frontend developer with React experience",
        "DevOps engineer for cloud infrastructure",
        "Machine learning engineer with Python and AWS experience"
    ]
    
    # Compute batch similarity
    similarities = compute_semantic_similarity_batch(resume_text, job_descriptions)
    
    print(f"📄 Resume: {resume_text}")
    print()
    
    for i, (job_desc, similarity) in enumerate(zip(job_descriptions, similarities), 1):
        print(f"🎯 Job {i} Similarity: {similarity:.1%}")
        print(f"   Description: {job_desc}")
        print()


def main():
    """Main test function."""
    print("🚀 Semantic Similarity Testing Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test 1: Basic semantic similarity
        test_basic_semantic_similarity()
        
        print("-" * 60)
        
        # Test 2: Batch similarity
        test_batch_similarity()
        
        print("-" * 60)
        
        # Test 3: Real data (if available)
        test_with_real_data()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 