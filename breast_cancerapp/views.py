from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.translation import activate, get_language
from django.urls import translate_url
import joblib, json, os
import pandas as pd
from .image_predictor import get_image_predictor
from .models import RiskAssessment, ImageAnalysis
from .nlp_recommender import NLPRecommender
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64


# Path to pipeline
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "models", "best_model_RandomForest.joblib")

# Hugging Face Token for NLP recommendations
HF_TOKEN = "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"

_PIPELINE_CACHE = None
_NLP_RECOMMENDER = None

def _get_nlp_recommender():
    global _NLP_RECOMMENDER
    if _NLP_RECOMMENDER is None:
        _NLP_RECOMMENDER = NLPRecommender(HF_TOKEN)
    return _NLP_RECOMMENDER

def _get_pipeline():
    global _PIPELINE_CACHE
    if _PIPELINE_CACHE is None:
        if not os.path.exists(PIPELINE_PATH):
            raise FileNotFoundError(f"Model pipeline not found at {PIPELINE_PATH}")
        _PIPELINE_CACHE = joblib.load(PIPELINE_PATH)
    return _PIPELINE_CACHE

@login_required
def dashbord(request: HttpRequest) -> HttpResponse:
    """Render the prediction form."""
    return render(request, "predict_form.html")

@login_required
def predict(request: HttpRequest) -> HttpResponse:
    """Handle form submission, run prediction, and render results."""
    if request.method != "POST":
        return render(request, "predict_form.html", {
            "error": "Please submit the form to get a prediction."
        })

    # Extract and coerce inputs. Use the exact feature names expected by the model
    def _to_int(value, default=None):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    history_breast_cancer_or_radiation = request.POST.get("history_breast_cancer_or_radiation")
    brca_mutation_or_genetic_syndrome = request.POST.get("brca_mutation_or_genetic_syndrome")
    age = _to_int(request.POST.get("age"))
    sub_ethnicity_or_birthplace = request.POST.get("sub_ethnicity_or_birthplace")
    biopsy_benign = request.POST.get("biopsy_benign")
    biopsy_benign_count = _to_int(request.POST.get("biopsy_benign_count"), 0)
    biopsy_atypical_hyperplasia = request.POST.get("biopsy_atypical_hyperplasia")
    age_first_menstrual = _to_int(request.POST.get("age_first_menstrual"))
    age_first_childbirth = _to_int(request.POST.get("age_first_childbirth"), 0)
    relatives_breast_cancer = request.POST.get("relatives_breast_cancer")

    payload = {
        "history_breast_cancer_or_radiation": history_breast_cancer_or_radiation,
        "brca_mutation_or_genetic_syndrome": brca_mutation_or_genetic_syndrome,
        "age": age,
        "sub_ethnicity_or_birthplace": sub_ethnicity_or_birthplace,
        "biopsy_benign": biopsy_benign,
        "biopsy_benign_count": biopsy_benign_count,
        "biopsy_atypical_hyperplasia": biopsy_atypical_hyperplasia,
        "age_first_menstrual": age_first_menstrual,
        "age_first_childbirth": age_first_childbirth,
        "relatives_breast_cancer": relatives_breast_cancer,
    }

    # Basic validation: ensure required numeric fields are present
    missing = []
    for key in ["age", "age_first_menstrual"]:
        if payload.get(key) is None:
            missing.append(key)

    if missing:
        return render(request, "predict_form.html", {
            "error": f"Missing or invalid fields: {', '.join(missing)}",
            "form_values": payload,
        })

    try:
        clf = _get_pipeline()
        df = pd.DataFrame([payload])
        
        # The model expects 'Outcome' as a feature, so we need to add it with a default value
        # Since we don't have the actual outcome, we'll use a neutral value (0)
        if 'Outcome' not in df.columns:
            df['Outcome'] = 0  # Default neutral value
        
        # Ensure all required features are present
        required_features = ['history_breast_cancer_or_radiation', 'brca_mutation_or_genetic_syndrome', 
                           'age', 'sub_ethnicity_or_birthplace', 'biopsy_benign', 'biopsy_benign_count', 
                           'biopsy_atypical_hyperplasia', 'age_first_menstrual', 'age_first_childbirth', 
                           'relatives_breast_cancer', 'Outcome']
        
        # Check if all required features are present
        missing_features = [col for col in required_features if col not in df.columns]
        if missing_features:
            return render(request, "predict_form.html", {
                "error": f"Missing required features: {', '.join(missing_features)}",
                "form_values": payload,
            })
        
        pred = int(clf.predict(df)[0])
        proba = float(getattr(clf, "predict_proba")(df)[0, 1]) if hasattr(clf, "predict_proba") else float(pred)
        percent = round(proba * 100.0, 2)
        class_label = "Positive (1)" if pred == 1 else "Negative (0)"

        # Get NLP recommendations
        risk_factors = {
            "history_breast_cancer_or_radiation": history_breast_cancer_or_radiation,
            "brca_mutation_or_genetic_syndrome": brca_mutation_or_genetic_syndrome,
            "sub_ethnicity_or_birthplace": sub_ethnicity_or_birthplace,
            "biopsy_benign": biopsy_benign,
            "biopsy_atypical_hyperplasia": biopsy_atypical_hyperplasia,
            "relatives_breast_cancer": relatives_breast_cancer,
        }
        
        try:
            nlp_recommender = _get_nlp_recommender()
            recommendations = nlp_recommender.get_breast_cancer_recommendations(
                prediction=pred,
                probability=proba,
                age=age,
                risk_factors=risk_factors
            )
        except Exception as e:
            print(f"Error getting NLP recommendations: {e}")
            recommendations = {
                "immediate_actions": "Consult with your healthcare provider for personalized recommendations.",
                "screening_schedule": "Follow standard screening guidelines based on your age and risk factors.",
                "lifestyle_changes": "Maintain a healthy lifestyle with regular exercise and balanced diet.",
                "follow_up_care": "Schedule regular follow-up appointments as recommended by your doctor."
            }

        # Prepare items for display
        input_items = [
            ("history_breast_cancer_or_radiation", history_breast_cancer_or_radiation),
            ("brca_mutation_or_genetic_syndrome", brca_mutation_or_genetic_syndrome),
            ("age", age),
            ("sub_ethnicity_or_birthplace", sub_ethnicity_or_birthplace),
            ("biopsy_benign", biopsy_benign),
            ("biopsy_benign_count", biopsy_benign_count),
            ("biopsy_atypical_hyperplasia", biopsy_atypical_hyperplasia),
            ("age_first_menstrual", age_first_menstrual),
            ("age_first_childbirth", age_first_childbirth),
            ("relatives_breast_cancer", relatives_breast_cancer),
        ]

        # Save to database (with error handling)
        try:
            RiskAssessment.objects.create(
                age=age,
                age_first_menstrual=age_first_menstrual,
                age_first_childbirth=age_first_childbirth,
                history_breast_cancer_or_radiation=history_breast_cancer_or_radiation,
                brca_mutation_or_genetic_syndrome=brca_mutation_or_genetic_syndrome,
                biopsy_benign=biopsy_benign,
                biopsy_benign_count=biopsy_benign_count,
                biopsy_atypical_hyperplasia=biopsy_atypical_hyperplasia,
                relatives_breast_cancer=relatives_breast_cancer,
                sub_ethnicity_or_birthplace=sub_ethnicity_or_birthplace,
                prediction=pred,
                probability=proba,
                confidence_percent=percent
            )
        except Exception as db_error:
            print(f"Database save failed: {db_error}")
            # Continue without saving to database

        # Process recommendations for template display
        processed_recommendations = {}
        for key, value in recommendations.items():
            if isinstance(value, str):
                processed_recommendations[key] = value.split(" | ")
            else:
                processed_recommendations[key] = [str(value)]

        context = {
            "input_items": input_items,
            "predicted_class": class_label,
            "predicted_proba": proba,
            "percent": percent,
            "recommendations": recommendations,
            "processed_recommendations": processed_recommendations,
        }
        return render(request, "prediction_result.html", context)
    except Exception as e:
        return render(request, "predict_form.html", {
            "error": f"Prediction failed: {e}",
            "form_values": payload,
        })

@login_required
def doctor(request: HttpRequest) -> HttpResponse:
    """Render the doctor dashboard."""
    return render(request, "doctor_dashboard.html")

@login_required
def image_predict_form(request: HttpRequest) -> HttpResponse:
    """Render the image prediction form."""
    return render(request, "image_predict_form.html")

@login_required
def image_predict(request: HttpRequest) -> HttpResponse:
    """Handle image upload and prediction."""
    if request.method != "POST":
        return render(request, "image_predict_form.html", {
            "error": "Please upload an image to get a prediction."
        })
    
    # Check if image file is uploaded
    if 'image' not in request.FILES:
        return render(request, "image_predict_form.html", {
            "error": "Please select an image file."
        })
    
    image_file = request.FILES['image']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
    if image_file.content_type not in allowed_types:
        return render(request, "image_predict_form.html", {
            "error": "Please upload a valid image file (JPEG, PNG, BMP, or TIFF)."
        })
    
    try:
        # Save uploaded file temporarily
        file_path = default_storage.save(f'temp/{image_file.name}', ContentFile(image_file.read()))
        full_path = default_storage.path(file_path)
        
        # Get prediction
        predictor = get_image_predictor()
        result = predictor.predict_image(full_path)
        
        # Clean up temporary file
        default_storage.delete(file_path)
        
        # Prepare context
        prediction_label = "Malignant" if result['prediction'] == 1 else "Benign"
        confidence_percent = round(result['confidence'] * 100, 2)
        
        # Calculate percentage probabilities
        benign_percent = round(result['probabilities']['benign'] * 100, 2)
        malignant_percent = round(result['probabilities']['malignant'] * 100, 2)
        
        # Get NLP recommendations for image analysis
        try:
            nlp_recommender = _get_nlp_recommender()
            image_recommendations = nlp_recommender.get_image_analysis_recommendations(
                prediction=result['prediction'],
                stage=result['stage'],
                confidence=result['confidence']
            )
        except Exception as e:
            print(f"Error getting NLP recommendations for image: {e}")
            image_recommendations = {
                "immediate_actions": [
                    "Review results with your healthcare provider immediately.",
                    "Discuss the confidence level and implications with your doctor.",
                    "Bring all previous medical records to your consultation."
                ],
                "follow_up": [
                    "Schedule follow-up imaging as recommended by your radiologist.",
                    "Consider additional diagnostic tests if recommended.",
                    "Keep a record of symptoms and changes for follow-up visits."
                ],
                "treatment_planning": [
                    "Consult with an oncologist for treatment options if malignant.",
                    "Discuss surgical options if applicable.",
                    "Consider second opinion for confirmed diagnosis."
                ],
                "lifestyle": [
                    "Maintain a healthy diet rich in fruits and vegetables.",
                    "Engage in regular physical activity as approved by your doctor.",
                    "Avoid smoking and limit alcohol consumption."
                ],
                "monitoring": [
                    "Report any new symptoms or changes immediately.",
                    "Perform regular self-examinations as taught by your healthcare provider.",
                    "Keep a diary of any changes or concerns."
                ],
                "support_services": [
                    "Consider joining a support group for emotional support.",
                    "Seek counseling services to cope with anxiety.",
                    "Contact patient advocacy organizations for resources."
                ]
            }
        
        # Save to database (with error handling)
        try:
            ImageAnalysis.objects.create(
                image_name=image_file.name,
                image_size=image_file.size,
                prediction=result['prediction'],
                prediction_label=prediction_label,
                confidence=result['confidence'],
                confidence_percent=confidence_percent,
                stage=result['stage'],
                benign_probability=result['probabilities']['benign'],
                malignant_probability=result['probabilities']['malignant']
            )
        except Exception as db_error:
            print(f"Database save failed: {db_error}")
            # Continue without saving to database

        # Process recommendations to ensure they are lists
        processed_recommendations = {}
        for key, value in image_recommendations.items():
            if isinstance(value, str):
                # Convert string to list by splitting on periods or newlines
                if '.' in value:
                    processed_recommendations[key] = [item.strip() for item in value.split('.') if item.strip()]
                elif '\n' in value:
                    processed_recommendations[key] = [item.strip() for item in value.split('\n') if item.strip()]
                else:
                    processed_recommendations[key] = [value]
            elif isinstance(value, list):
                processed_recommendations[key] = value
            else:
                processed_recommendations[key] = [str(value)]

        context = {
            'prediction': result['prediction'],
            'prediction_label': prediction_label,
            'confidence': result['confidence'],
            'confidence_percent': confidence_percent,
            'stage': result['stage'],
            'probabilities': result['probabilities'],
            'benign_percent': benign_percent,
            'malignant_percent': malignant_percent,
            'image_name': image_file.name,
            'recommendations': image_recommendations,
            'processed_recommendations': processed_recommendations
        }
        
        return render(request, "image_prediction_result.html", context)
        
    except Exception as e:
        # Clean up temporary file if it exists
        try:
            if 'file_path' in locals():
                default_storage.delete(file_path)
        except:
            pass
            
        return render(request, "image_predict_form.html", {
            "error": f"Prediction failed: {str(e)}"
        })

@login_required
def reports_dashboard(request):
    """Main reports dashboard with overview statistics"""
    try:
        # Get statistics
        total_risk_assessments = RiskAssessment.objects.count()
        total_image_analyses = ImageAnalysis.objects.count()
        
        # Risk assessment statistics
        risk_benign = RiskAssessment.objects.filter(prediction=0).count()
        risk_malignant = RiskAssessment.objects.filter(prediction=1).count()
        
        # Image analysis statistics
        image_benign = ImageAnalysis.objects.filter(prediction=0).count()
        image_malignant = ImageAnalysis.objects.filter(prediction=1).count()
        
        # Recent activity
        recent_risk = RiskAssessment.objects.all()[:5]
        recent_images = ImageAnalysis.objects.all()[:5]
    except Exception as e:
        # If database tables don't exist, use default values
        total_risk_assessments = 0
        total_image_analyses = 0
        risk_benign = 0
        risk_malignant = 0
        image_benign = 0
        image_malignant = 0
        recent_risk = []
        recent_images = []
    
    context = {
        'total_risk_assessments': total_risk_assessments,
        'total_image_analyses': total_image_analyses,
        'risk_benign': risk_benign,
        'risk_malignant': risk_malignant,
        'image_benign': image_benign,
        'image_malignant': image_malignant,
        'recent_risk': recent_risk,
        'recent_images': recent_images,
    }
    
    return render(request, "reports_dashboard.html", context)

@login_required
def risk_assessment_reports(request):
    """Risk assessment reports with graphs"""
    try:
        assessments = RiskAssessment.objects.all()
        
        # Create charts
        benign_count = assessments.filter(prediction=0).count()
        malignant_count = assessments.filter(prediction=1).count()
        
        # Age distribution chart
        age_chart = create_age_distribution_chart(assessments)
        
        # Prediction distribution chart
        prediction_chart = create_prediction_chart(benign_count, malignant_count, "Risk Assessment")
    except Exception as e:
        # If database tables don't exist, use default values
        assessments = []
        benign_count = 0
        malignant_count = 0
        age_chart = None
        prediction_chart = None
    
    context = {
        'assessments': assessments,
        'benign_count': benign_count,
        'malignant_count': malignant_count,
        'age_chart': age_chart,
        'prediction_chart': prediction_chart,
    }
    
    return render(request, "risk_assessment_reports.html", context)

@login_required
def image_analysis_reports(request):
    """Image analysis reports with graphs"""
    try:
        analyses = ImageAnalysis.objects.all()
        
        # Create charts
        benign_count = analyses.filter(prediction=0).count()
        malignant_count = analyses.filter(prediction=1).count()
        
        # Stage distribution chart
        stage_chart = create_stage_distribution_chart(analyses)
        
        # Prediction distribution chart
        prediction_chart = create_prediction_chart(benign_count, malignant_count, "Image Analysis")
    except Exception as e:
        # If database tables don't exist, use default values
        analyses = []
        benign_count = 0
        malignant_count = 0
        stage_chart = None
        prediction_chart = None
    
    context = {
        'analyses': analyses,
        'benign_count': benign_count,
        'malignant_count': malignant_count,
        'stage_chart': stage_chart,
        'prediction_chart': prediction_chart,
    }
    
    return render(request, "image_analysis_reports.html", context)

@login_required
def checkup_history(request):
    """List of all checkups"""
    try:
        risk_assessments = RiskAssessment.objects.all()
        image_analyses = ImageAnalysis.objects.all()
        
        # Combine and sort by date
        all_checkups = []
        
        for assessment in risk_assessments:
            all_checkups.append({
                'type': 'Risk Assessment',
                'date': assessment.created_at,
                'prediction': 'Low Risk' if assessment.prediction == 0 else 'High Risk',
                'confidence': assessment.confidence_percent,
                'details': f"Age: {assessment.age}, Confidence: {assessment.confidence_percent}%"
            })
        
        for analysis in image_analyses:
            all_checkups.append({
                'type': 'Image Analysis',
                'date': analysis.created_at,
                'prediction': analysis.prediction_label,
                'confidence': analysis.confidence_percent,
                'details': f"Image: {analysis.image_name}, Stage: {analysis.stage}"
            })
        
        # Sort by date (newest first)
        all_checkups.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate statistics
        risk_assessment_count = len([c for c in all_checkups if c['type'] == 'Risk Assessment'])
        image_analysis_count = len([c for c in all_checkups if c['type'] == 'Image Analysis'])
        benign_count = len([c for c in all_checkups if 'Low' in c['prediction'] or 'Benign' in c['prediction']])
        
    except Exception as e:
        # If database tables don't exist, use empty list
        all_checkups = []
        risk_assessment_count = 0
        image_analysis_count = 0
        benign_count = 0
    
    context = {
        'checkups': all_checkups,
        'risk_assessment_count': risk_assessment_count,
        'image_analysis_count': image_analysis_count,
        'benign_count': benign_count,
        'today': timezone.now().date(),
    }
    
    return render(request, "checkup_history.html", context)

@login_required
def user_guide(request):
    """User guide page"""
    return render(request, "user_guide.html")

def logout_view(request):
    """Logout functionality"""
    logout(request)
    return redirect('login')

@login_required
def export_pdf(request, report_type):
    """Export reports as PDF"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add report content based on type
    if report_type == 'risk_assessment':
        assessments = RiskAssessment.objects.all()
        benign_count = assessments.filter(prediction=0).count()
        malignant_count = assessments.filter(prediction=1).count()
        
        story.append(Paragraph(f"Total Risk Assessments: {len(assessments)}", styles['Normal']))
        story.append(Paragraph(f"Low Risk Predictions: {benign_count}", styles['Normal']))
        story.append(Paragraph(f"High Risk Predictions: {malignant_count}", styles['Normal']))
        
    elif report_type == 'image_analysis':
        analyses = ImageAnalysis.objects.all()
        benign_count = analyses.filter(prediction=0).count()
        malignant_count = analyses.filter(prediction=1).count()
        
        story.append(Paragraph(f"Total Image Analyses: {len(analyses)}", styles['Normal']))
        story.append(Paragraph(f"Benign Predictions: {benign_count}", styles['Normal']))
        story.append(Paragraph(f"Malignant Predictions: {malignant_count}", styles['Normal']))
    
    doc.build(story)
    return response

def create_age_distribution_chart(assessments):
    """Create age distribution chart"""
    ages = [a.age for a in assessments]
    
    plt.figure(figsize=(8, 6))
    plt.hist(ages, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('Age Distribution of Risk Assessments')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    
    return graphic

def create_prediction_chart(benign_count, malignant_count, title):
    """Create prediction distribution chart"""
    labels = ['Benign/Low Risk', 'Malignant/High Risk']
    sizes = [benign_count, malignant_count]
    colors = ['#2ecc71', '#e74c3c']
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title(f'{title} Predictions Distribution')
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    
    return graphic

def create_stage_distribution_chart(analyses):
    """Create stage distribution chart"""
    stages = [a.stage for a in analyses if a.prediction == 1]  # Only malignant cases
    
    if not stages:
        return None
    
    stage_counts = {}
    for stage in stages:
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    plt.figure(figsize=(10, 6))
    plt.bar(stage_counts.keys(), stage_counts.values(), color='#e74c3c', alpha=0.7)
    plt.title('Cancer Stage Distribution (Malignant Cases)')
    plt.xlabel('Cancer Stage')
    plt.ylabel('Number of Cases')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Convert to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    
    return graphic

def set_language(request):
    """
    Set language for the session and redirect to the same page in the new language.
    """
    lang_code = request.GET.get('lang', 'en')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    
    # Validate language code
    from django.conf import settings
    available_languages = [lang[0] for lang in settings.LANGUAGES]
    
    if lang_code in available_languages:
        # Store language in session
        request.session['django_language'] = lang_code
        
        # Try to activate language, but handle missing translation files gracefully
        try:
            activate(lang_code)
            # Translate the next URL if possible
            try:
                next_url = translate_url(next_url, lang_code)
            except:
                pass
        except:
            # If translation files are missing, just store the language in session
            pass
    
    return redirect(next_url)
