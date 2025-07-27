"""
Job-Resume Matching and Scoring System
Calculates a score out of 100 for each job based on resume compatibility.
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass
import json
import os


@dataclass
class ScoringWeights:
    """Weights for different scoring factors"""
    skills_match: float = 0.35      # 35% - Skills alignment
    experience_level: float = 0.25   # 25% - Experience requirements
    education_match: float = 0.15    # 15% - Education requirements
    location_match: float = 0.10     # 10% - Location preferences
    title_match: float = 0.10        # 10% - Job title relevance
    salary_expectation: float = 0.05  # 5% - Salary expectations


class JobResumeMatcher:
    """Matches resume against job requirements and calculates compatibility score"""
    
    def __init__(self, weights: ScoringWeights = None):
        self.weights = weights or ScoringWeights()
        
        # Common skill mappings for better matching
        self.skill_mappings = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
            'javascript': ['javascript', 'js', 'node.js', 'react', 'vue', 'angular', 'typescript'],
            'java': ['java', 'spring', 'android', 'kotlin'],
            'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'database'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'cloud'],
            'docker': ['docker', 'kubernetes', 'containerization'],
            'git': ['git', 'github', 'gitlab', 'version control'],
            'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence', 'deep learning', 'neural networks'],
            'data science': ['data science', 'data analysis', 'statistics', 'analytics'],
            'devops': ['devops', 'ci/cd', 'jenkins', 'terraform', 'ansible']
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        if not text:
            return ""
        return re.sub(r'[^\w\s]', ' ', text.lower()).strip()
    
    def calculate_skills_match(self, job_skills: List[str], resume_skills: List[str]) -> float:
        """Calculate skills match percentage"""
        if not job_skills:
            return 0.0
        
        job_skills_normalized = [self.normalize_text(skill) for skill in job_skills]
        resume_skills_normalized = [self.normalize_text(skill) for skill in resume_skills]
        
        # Direct matches
        direct_matches = set(job_skills_normalized) & set(resume_skills_normalized)
        
        # Mapped matches (using skill mappings)
        mapped_matches = set()
        for job_skill in job_skills_normalized:
            for category, related_skills in self.skill_mappings.items():
                if job_skill in related_skills:
                    for resume_skill in resume_skills_normalized:
                        if resume_skill in related_skills:
                            mapped_matches.add(job_skill)
                            break
        
        total_matches = len(direct_matches | mapped_matches)
        return min(1.0, total_matches / len(job_skills_normalized))
    
    def calculate_experience_match(self, job_description: str, resume_experience: int, job_title: str) -> float:
        """Calculate experience level match"""
        if not job_description:
            return 0.5  # Neutral score if no description
        
        description_lower = job_description.lower()
        
        # Experience level indicators
        junior_keywords = ['junior', 'entry level', '0-2 years', '1-2 years', 'recent graduate', 'new grad']
        mid_keywords = ['mid level', '3-5 years', '4-6 years', 'intermediate', 'experienced']
        senior_keywords = ['senior', 'lead', 'principal', '5+ years', '7+ years', 'expert', 'advanced']
        
        # Determine job level
        job_level = 'mid'  # default
        if any(keyword in description_lower for keyword in junior_keywords):
            job_level = 'junior'
        elif any(keyword in description_lower for keyword in senior_keywords):
            job_level = 'senior'
        
        # Score based on experience alignment
        if job_level == 'junior':
            if resume_experience <= 2:
                return 1.0
            elif resume_experience <= 4:
                return 0.7
            else:
                return 0.4
        elif job_level == 'mid':
            if 2 <= resume_experience <= 6:
                return 1.0
            elif resume_experience <= 1:
                return 0.6
            else:
                return 0.8
        else:  # senior
            if resume_experience >= 5:
                return 1.0
            elif resume_experience >= 3:
                return 0.7
            else:
                return 0.3
    
    def calculate_education_match(self, job_description: str, resume_education: List[Dict]) -> float:
        """Calculate education requirements match"""
        if not job_description or not resume_education:
            return 0.5
        
        description_lower = job_description.lower()
        
        # Education requirements
        requires_degree = any(keyword in description_lower for keyword in ['degree', 'bachelor', 'master', 'phd', 'graduate'])
        requires_masters = any(keyword in description_lower for keyword in ['master', 'graduate degree', 'ms', 'ma'])
        requires_phd = any(keyword in description_lower for keyword in ['phd', 'doctorate', 'doctoral'])
        
        # Check resume education
        has_degree = any('bachelor' in edu.get('degree', '').lower() for edu in resume_education)
        has_masters = any('postgraduate' in edu.get('degree', '').lower() or 'master' in edu.get('degree', '').lower() for edu in resume_education)
        has_phd = any('phd' in edu.get('degree', '').lower() or 'doctorate' in edu.get('degree', '').lower() for edu in resume_education)
        
        if requires_phd and has_phd:
            return 1.0
        elif requires_masters and (has_masters or has_phd):
            return 1.0
        elif requires_degree and (has_degree or has_masters or has_phd):
            return 1.0
        elif not requires_degree:
            return 0.8  # No specific requirement
        else:
            return 0.3  # Missing required education
    
    def calculate_location_match(self, job_location: str, resume_location: str) -> float:
        """Calculate location compatibility"""
        if not job_location or not resume_location:
            return 0.5
        
        job_loc_lower = job_location.lower()
        resume_loc_lower = resume_location.lower()
        
        # Exact match
        if job_loc_lower == resume_loc_lower:
            return 1.0
        
        # Same country/region
        if 'remote' in job_loc_lower or 'anywhere' in job_loc_lower:
            return 0.9
        
        # Same city/state
        if any(word in resume_loc_lower for word in job_loc_lower.split()):
            return 0.8
        
        # Same country (basic check)
        countries = ['canada', 'usa', 'united states', 'india', 'uk', 'united kingdom']
        job_country = next((c for c in countries if c in job_loc_lower), None)
        resume_country = next((c for c in countries if c in resume_loc_lower), None)
        
        if job_country and resume_country and job_country == resume_country:
            return 0.6
        
        return 0.3
    
    def calculate_title_match(self, job_title: str, resume_experience: List[Dict], resume_skills: List[str]) -> float:
        """Calculate job title relevance"""
        if not job_title:
            return 0.5
        
        title_lower = job_title.lower()
        
        # Check if current position matches
        for exp in resume_experience:
            current_title = exp.get('title', '').lower()
            if current_title and any(word in title_lower for word in current_title.split()):
                return 1.0
        
        # Check if skills align with title
        title_keywords = title_lower.split()
        relevant_skills = 0
        
        for skill in resume_skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in title_keywords):
                relevant_skills += 1
        
        if relevant_skills > 0:
            return min(1.0, relevant_skills / len(title_keywords))
        
        return 0.3
    
    def calculate_salary_match(self, job_salary: str, resume_experience: int) -> float:
        """Calculate salary expectation match (basic implementation)"""
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated salary analysis
        if not job_salary:
            return 0.5
        
        # Basic scoring based on experience level
        if resume_experience <= 2:
            return 0.8  # Junior level - likely flexible
        elif resume_experience <= 5:
            return 0.7  # Mid level - moderate expectations
        else:
            return 0.6  # Senior level - higher expectations
    
    def calculate_overall_score(self, job: Dict, resume_data: Dict) -> float:
        """Calculate overall compatibility score (0-100)"""
        try:
            # Extract job data
            job_skills = job.get('required_skills', [])
            job_description = job.get('description', '')
            job_title = job.get('title', '')
            job_location = job.get('location', '')
            job_salary = job.get('salary_range', '')
            
            # Extract resume data
            resume_skills = resume_data.get('skills', [])
            resume_experience_years = resume_data.get('years_of_experience', 0)
            resume_education = resume_data.get('education', [])
            resume_location = resume_data.get('location', '')
            resume_experience = resume_data.get('experience', [])
            
            # Calculate individual scores
            skills_score = self.calculate_skills_match(job_skills, resume_skills)
            experience_score = self.calculate_experience_match(job_description, resume_experience_years, job_title)
            education_score = self.calculate_education_match(job_description, resume_education)
            location_score = self.calculate_location_match(job_location, resume_location)
            title_score = self.calculate_title_match(job_title, resume_experience, resume_skills)
            salary_score = self.calculate_salary_match(job_salary, resume_experience_years)
            
            # Calculate weighted score
            weighted_score = (
                skills_score * self.weights.skills_match +
                experience_score * self.weights.experience_level +
                education_score * self.weights.education_match +
                location_score * self.weights.location_match +
                title_score * self.weights.title_match +
                salary_score * self.weights.salary_expectation
            )
            
            # Convert to percentage (0-100)
            return round(weighted_score * 100, 1)
            
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 0.0


def score_all_jobs(jobs_file: str = "data/fetched_jobs.json", resume_file: str = "data/parsed_resume.json") -> bool:
    """
    Score all jobs in the jobs file against the parsed resume.
    Updates the jobs file with score field for each job.
    """
    try:
        # Load jobs
        if not os.path.exists(jobs_file):
            print(f"Jobs file not found: {jobs_file}")
            return False
        
        with open(jobs_file, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        # Load resume
        if not os.path.exists(resume_file):
            print(f"Resume file not found: {resume_file}")
            return False
        
        with open(resume_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        resume_info = resume_data.get('resume', {})
        
        # Initialize matcher
        matcher = JobResumeMatcher()
        
        # Score each job
        jobs = jobs_data.get('jobs', [])
        print(f"Scoring {len(jobs)} jobs...")
        
        for i, job in enumerate(jobs):
            score = matcher.calculate_overall_score(job, resume_info)
            job['match_score'] = score
            
            if (i + 1) % 10 == 0:
                print(f"Scored {i + 1}/{len(jobs)} jobs...")
        
        # Sort jobs by score (highest first)
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Update metadata
        jobs_data['metadata']['scored_at'] = datetime.now().isoformat()
        jobs_data['metadata']['total_jobs_scored'] = len(jobs)
        jobs_data['metadata']['highest_score'] = max(job.get('match_score', 0) for job in jobs)
        jobs_data['metadata']['average_score'] = round(sum(job.get('match_score', 0) for job in jobs) / len(jobs), 1)
        
        # Save updated jobs
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully scored {len(jobs)} jobs!")
        print(f"📊 Score range: {min(job.get('match_score', 0) for job in jobs)} - {max(job.get('match_score', 0) for job in jobs)}")
        print(f"📈 Average score: {jobs_data['metadata']['average_score']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error scoring jobs: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    from datetime import datetime
    success = score_all_jobs()
    if success:
        print("🎯 Job scoring completed successfully!")
    else:
        print("💥 Job scoring failed!") 