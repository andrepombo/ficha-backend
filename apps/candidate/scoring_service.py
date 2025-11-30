"""
Candidate Scoring Service

This service calculates objective scores for candidates based on multiple criteria:
- Experience & Skills (30 points)
- Education & Qualifications (20 points)
- Availability & Logistics (20 points)
- Interview Performance (30 points)

Total: 100 points
"""

from django.db.models import Avg
from datetime import date


class CandidateScorer:
    """
    Service class to calculate candidate scores based on various criteria.
    """
    
    # Default scoring weights (total = 100)
    # These can be customized via ScoringConfig
    DEFAULT_WEIGHTS = {
        'experience_skills': 30,
        'education': 20,
        'availability_logistics': 20,
        'interview_performance': 30,
    }
    
    @classmethod
    def get_weights(cls):
        """Get current scoring weights (custom or default)."""
        from .scoring_config import ScoringConfig
        return ScoringConfig.get_weights()
    
    # Education level scores (normalized to 0-1)
    EDUCATION_SCORES = {
        'fundamental_incompleto': 0.2,
        'fundamental_completo': 0.3,
        'medio_incompleto': 0.5,
        'medio_completo': 0.6,
        'tecnica_incompleta': 0.7,
        'tecnica_completa': 0.8,
        'superior_incompleta': 0.85,
        'superior_completa': 0.95,
        'pos_graduacao': 1.0,
    }
    
    @classmethod
    def _calculate_total_experience_years(cls, candidate):
        """
        Calculate total years of experience from professional experience records.
        If no records exist, falls back to years_of_experience field.
        
        Args:
            candidate: Candidate model instance
            
        Returns:
            float: Total years of experience
        """
        from datetime import date
        
        # Check if candidate has professional_experiences
        experiences = candidate.professional_experiences.all()
        
        if not experiences.exists():
            # Fall back to years_of_experience field if no professional experiences
            return candidate.years_of_experience or 0
        
        total_days = 0
        
        for exp in experiences:
            if exp.data_admissao:
                # If no termination date, assume still working there (use today)
                end_date = exp.data_desligamento if exp.data_desligamento else date.today()
                start_date = exp.data_admissao
                
                # Calculate days between dates
                if end_date >= start_date:
                    days = (end_date - start_date).days
                    total_days += days
        
        # Convert days to years (assuming 365.25 days per year)
        total_years = round(total_days / 365.25, 1)
        
        return total_years
    
    @classmethod
    def calculate_score(cls, candidate):
        """
        Calculate the total score for a candidate.
        
        Args:
            candidate: Candidate model instance
            
        Returns:
            dict: Dictionary containing total score and breakdown by category
        """
        scores = {
            'experience_skills': cls._score_experience_skills(candidate),
            'education': cls._score_education(candidate),
            'availability_logistics': cls._score_availability_logistics(candidate),
            'interview_performance': cls._score_interview_performance(candidate),
        }
        
        # Calculate total score
        total = sum(scores.values())
        
        return {
            'total': round(total, 1),
            'breakdown': {
                'experience_skills': round(scores['experience_skills'], 1),
                'education': round(scores['education'], 1),
                'availability_logistics': round(scores['availability_logistics'], 1),
                'interview_performance': round(scores['interview_performance'], 1),
            },
            'grade': cls._get_grade(total),
        }
    
    @classmethod
    def _score_experience_skills(cls, candidate):
        """
        Score based on years of experience and idle time (configurable per criterion).
        """
        score = 0
        weights = cls.get_weights()
        criteria = weights['experience_skills']
        
        # Years of experience
        years_max = criteria['years_of_experience']
        years = cls._calculate_total_experience_years(candidate)
        if years >= 6:
            score += years_max
        elif years >= 4:
            score += years_max * 0.87
        elif years >= 2:
            score += years_max * 0.67
        elif years >= 1:
            score += years_max * 0.33
        else:
            score += years_max * 0.13
        
        # Idle time (tempo parado) - if configured
        if 'idle_time' in criteria:
            idle_time_max = criteria['idle_time']
            idle_time_score = cls._score_idle_time(candidate, idle_time_max)
            score += idle_time_score
        
        # Worked at Pinte before - if configured
        if 'worked_at_pinte_before' in criteria:
            worked_before_max = criteria['worked_at_pinte_before']
            if worked_before_max > 0:  # Only score if points are configured
                if candidate.worked_at_pinte_before == 'sim':
                    score += worked_before_max
        
        # Has relatives/friends in company - if configured
        if 'has_relatives_in_company' in criteria:
            relatives_max = criteria['has_relatives_in_company']
            if relatives_max > 0:  # Only score if points are configured
                if candidate.has_relatives_in_company == 'sim':
                    score += relatives_max
        
        # Referred by someone - if configured
        if 'referred_by' in criteria:
            referred_max = criteria['referred_by']
            if referred_max > 0:  # Only score if points are configured
                if candidate.referred_by and candidate.referred_by.strip():
                    score += referred_max
        
        return score
    
    @classmethod
    def _score_idle_time(cls, candidate, max_score):
        """
        Score based on idle time (time since last job).
        Less idle time = higher score.
        Currently employed = maximum score.
        
        Args:
            candidate: Candidate model instance
            max_score: Maximum points for this criterion
            
        Returns:
            float: Score for idle time
        """
        experiences = candidate.professional_experiences.all()
        
        if not experiences.exists():
            # No experience records, return minimum score
            return max_score * 0.2
        
        # Find the most recent job (with the latest data_desligamento)
        most_recent_job = None
        latest_date = None
        
        for exp in experiences:
            if exp.data_desligamento:
                if latest_date is None or exp.data_desligamento > latest_date:
                    latest_date = exp.data_desligamento
                    most_recent_job = exp
            else:
                # No end date means currently employed
                most_recent_job = exp
                break
        
        # If currently employed (no end date on most recent job)
        if most_recent_job and not most_recent_job.data_desligamento:
            return max_score  # Full points for being currently employed
        
        # If no end date found at all, assume they have experience but unknown status
        if not most_recent_job or not most_recent_job.data_desligamento:
            return max_score * 0.5
        
        # Calculate idle time in days
        idle_days = most_recent_job.get_idle_time_days()
        
        if idle_days is None:
            return max_score * 0.5
        
        # Score based on idle time
        # 0-30 days (1 month): 100% of max
        # 31-90 days (3 months): 80% of max
        # 91-180 days (6 months): 60% of max
        # 181-365 days (1 year): 40% of max
        # 366-730 days (2 years): 20% of max
        # 730+ days (2+ years): 10% of max
        
        if idle_days <= 30:
            return max_score
        elif idle_days <= 90:
            return max_score * 0.8
        elif idle_days <= 180:
            return max_score * 0.6
        elif idle_days <= 365:
            return max_score * 0.4
        elif idle_days <= 730:
            return max_score * 0.2
        else:
            return max_score * 0.1
    
    @classmethod
    def _score_education(cls, candidate):
        """
        Score based on education level, courses, skills, and certifications (configurable per criterion).
        """
        weights = cls.get_weights()
        criteria = weights['education']
        score = 0
        
        # Education level
        level_max = criteria['education_level']
        education_level = candidate.highest_education
        
        # Match actual database values
        if education_level == 'pos_graduacao':
            score += level_max
        elif education_level == 'superior_completa':
            score += level_max * 0.95
        elif education_level == 'superior_incompleta':
            score += level_max * 0.85
        elif education_level == 'tecnica_completa':
            score += level_max * 0.80
        elif education_level == 'tecnica_incompleta':
            score += level_max * 0.70
        elif education_level == 'medio_completo':
            score += level_max * 0.60
        elif education_level == 'medio_incompleto':
            score += level_max * 0.40
        elif education_level == 'fundamental_completo':
            score += level_max * 0.30
        elif education_level == 'fundamental_incompleto':
            score += level_max * 0.20
        elif education_level == 'analfabeto':
            score += level_max * 0.10
        
        # Additional courses (bonus)
        courses_max = criteria['courses']
        # Count courses if they exist (assuming comma-separated list)
        # This is a simple implementation - adjust based on your data structure
        if hasattr(candidate, 'additional_courses') and candidate.additional_courses:
            course_count = len([c.strip() for c in candidate.additional_courses.split(',') if c.strip()])
            score += min(course_count * 0.5, courses_max)
        
        # Skills
        skills_max = criteria.get('skills', 0)
        if skills_max > 0:
            skills = candidate.skills or ''
            if skills.strip():
                skill_count = len([s.strip() for s in skills.split(',') if s.strip()])
                if skill_count >= 5:
                    score += skills_max
                elif skill_count >= 3:
                    score += skills_max * 0.75
                elif skill_count >= 1:
                    score += skills_max * 0.5
        
        # Certifications
        cert_max = criteria.get('certifications', 0)
        if cert_max > 0:
            certifications = candidate.certifications or ''
            if certifications.strip():
                cert_count = len([c.strip() for c in certifications.split(',') if c.strip()])
                if cert_count >= 3:
                    score += cert_max
                elif cert_count >= 2:
                    score += cert_max * 0.71
                elif cert_count >= 1:
                    score += cert_max * 0.43
        
        return score
    
    @classmethod
    def _score_availability_logistics(cls, candidate):
        """
        Score based on availability and logistics (configurable per criterion).
        """
        score = 0
        weights = cls.get_weights()
        criteria = weights['availability_logistics']
        
        # Immediate availability
        avail_max = criteria['immediate_availability']
        availability = candidate.availability_start or ''
        if availability == 'imediato':
            score += avail_max
        elif availability == '15_dias':
            score += avail_max * 0.75
        elif availability == '30_dias':
            score += avail_max * 0.5
        elif availability:
            score += avail_max * 0.25
        
        # Own transportation
        transport_max = criteria['own_transportation']
        if candidate.has_own_transportation == 'sim':
            score += transport_max
        
        # Travel availability
        travel_max = criteria['travel_availability']
        travel = candidate.travel_availability or ''
        if travel == 'sim':
            score += travel_max
        elif travel == 'ocasionalmente':
            score += travel_max * 0.5
        
        # Height painting (if configured)
        if 'height_painting' in criteria:
            height_max = criteria['height_painting']
            if candidate.height_painting == 'sim':
                score += height_max
        
        return score
    
    @classmethod
    def _score_interview_performance(cls, candidate):
        """
        Score based on interview performance.
        Uses the average rating from completed interviews, scaled to the configured maximum.
        """
        score = 0
        weights = cls.get_weights()
        criteria = weights['interview_performance']
        
        # Get all interviews for this candidate
        interviews = candidate.interviews.filter(status='completed')
        
        if not interviews.exists():
            return 0
        
        # Get the max score for average_rating
        rating_max = criteria.get('average_rating', 30)
        
        # Calculate average rating and scale to max score
        avg_rating = interviews.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            # Scale the rating (1-5) to the max score
            score = (avg_rating / 5.0) * rating_max
        
        return score
    
    @classmethod
    def _get_grade(cls, score):
        """
        Convert numeric score to letter grade.
        
        Args:
            score: Numeric score (0-100)
            
        Returns:
            str: Letter grade (A+, A, B+, B, C+, C, D, F)
        """
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    @classmethod
    def get_score_color(cls, score):
        """
        Get color code based on score.
        
        Args:
            score: Numeric score (0-100)
            
        Returns:
            str: Color code for UI display
        """
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellow'
        elif score >= 40:
            return 'orange'
        else:
            return 'red'
