"""
Scoring Configuration Management

This module handles the storage and retrieval of custom scoring weights.
Allows administrators to customize how much each category contributes to the total score.
Now uses database models instead of JSON files.
"""

from django.core.cache import cache


class ScoringConfig:
    """
    Manages scoring configuration with database storage.
    Uses the ScoringWeight model to store custom weights.
    """
    
    CACHE_KEY = 'scoring_weights'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_weights(cls):
        """
        Get current scoring weights from database.
        
        Returns:
            dict: Scoring weights for each category
        """
        # Check cache first
        cached_weights = cache.get(cls.CACHE_KEY)
        if cached_weights:
            return cached_weights
        
        # Get from database
        from .models import ScoringWeight
        config = ScoringWeight.get_active_config()
        weights = config.to_dict()
        
        # Cache the weights
        cache.set(cls.CACHE_KEY, weights, cls.CACHE_TIMEOUT)
        
        return weights
    
    @classmethod
    def set_weights(cls, weights):
        """
        Set custom scoring weights in database.
        
        Args:
            weights: Dictionary of weights for each category
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validate weights structure
        if not isinstance(weights, dict):
            return False, "Invalid weights format."
        
        # Check if total is 100 (with tolerance for floating point)
        total = 0
        for category_weights in weights.values():
            if isinstance(category_weights, dict):
                total += sum(category_weights.values())
            else:
                total += category_weights
        
        if abs(total - 100) > 0.1:  # Allow small floating point differences
            return False, f"Weights must sum to 100. Current total: {round(total, 1)}"
        
        # Save to database
        try:
            from .models import ScoringWeight
            
            # Get or create active config
            config = ScoringWeight.get_active_config()
            
            # Update all fields
            config.years_of_experience = weights.get('experience_skills', {}).get('years_of_experience', 27)
            config.idle_time = weights.get('experience_skills', {}).get('idle_time', 5)
            config.worked_at_pinte_before = weights.get('experience_skills', {}).get('worked_at_pinte_before', 0)
            config.has_relatives_in_company = weights.get('experience_skills', {}).get('has_relatives_in_company', 0)
            config.referred_by = weights.get('experience_skills', {}).get('referred_by', 0)
            
            config.education_level = weights.get('education', {}).get('education_level', 16)
            config.courses = weights.get('education', {}).get('courses', 0)
            config.skills = weights.get('education', {}).get('skills', 2)
            config.certifications = weights.get('education', {}).get('certifications', 0)
            
            config.immediate_availability = weights.get('availability_logistics', {}).get('immediate_availability', 5)
            config.own_transportation = weights.get('availability_logistics', {}).get('own_transportation', 5)
            config.travel_availability = weights.get('availability_logistics', {}).get('travel_availability', 5)
            config.height_painting = weights.get('availability_logistics', {}).get('height_painting', 5)
            
            config.average_rating = weights.get('interview_performance', {}).get('average_rating', 30)
            
            config.save()
            
            # Clear cache to force reload
            cache.delete(cls.CACHE_KEY)
            
            return True, "Weights updated successfully"
        except Exception as e:
            return False, f"Failed to save weights: {str(e)}"
    
    @classmethod
    def reset_to_defaults(cls):
        """
        Reset weights to default values by creating a new default configuration.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            from .models import ScoringWeight
            
            # Create a new default configuration (will deactivate the old one)
            ScoringWeight.objects.create(is_active=True)
            
            # Clear cache
            cache.delete(cls.CACHE_KEY)
            
            return True, "Weights reset to defaults"
        except Exception as e:
            return False, f"Failed to reset weights: {str(e)}"
    
    @classmethod
    def get_config_info(cls):
        """
        Get information about current configuration.
        
        Returns:
            dict: Configuration info including weights, total, and status
        """
        from .models import ScoringWeight
        
        config = ScoringWeight.get_active_config()
        weights = config.to_dict()
        
        # Calculate total
        total = config.get_total_points()
        
        # Check if it's the first/default config
        is_custom = ScoringWeight.objects.filter(is_active=True).count() > 0 and config.pk is not None
        
        return {
            'weights': weights,
            'total': round(total, 1),
            'is_custom': is_custom,
            'is_valid': abs(total - 100) < 0.1,  # Allow small floating point differences
        }
