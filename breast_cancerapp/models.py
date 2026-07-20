from django.db import models
from django.utils import timezone

class RiskAssessment(models.Model):
    """Model to store risk assessment predictions"""
    created_at = models.DateTimeField(default=timezone.now)
    
    # Patient demographics
    age = models.IntegerField()
    age_first_menstrual = models.IntegerField()
    age_first_childbirth = models.IntegerField(null=True, blank=True)
    
    # Medical history
    history_breast_cancer_or_radiation = models.CharField(max_length=10)
    brca_mutation_or_genetic_syndrome = models.CharField(max_length=10)
    biopsy_benign = models.CharField(max_length=10)
    biopsy_benign_count = models.IntegerField(default=0)
    biopsy_atypical_hyperplasia = models.CharField(max_length=10)
    relatives_breast_cancer = models.CharField(max_length=10)
    sub_ethnicity_or_birthplace = models.CharField(max_length=100, blank=True)
    
    # Prediction results
    prediction = models.IntegerField()  # 0 or 1
    probability = models.FloatField()
    confidence_percent = models.FloatField()
    
    class Meta:
        ordering = ['-created_at']

class ImageAnalysis(models.Model):
    """Model to store image analysis predictions"""
    created_at = models.DateTimeField(default=timezone.now)
    
    # Image information
    image_name = models.CharField(max_length=255)
    image_size = models.IntegerField(null=True, blank=True)
    
    # Prediction results
    prediction = models.IntegerField()  # 0 = Benign, 1 = Malignant
    prediction_label = models.CharField(max_length=20)
    confidence = models.FloatField()
    confidence_percent = models.FloatField()
    stage = models.CharField(max_length=50)
    
    # Detailed probabilities
    benign_probability = models.FloatField()
    malignant_probability = models.FloatField()
    
    class Meta:
        ordering = ['-created_at']
