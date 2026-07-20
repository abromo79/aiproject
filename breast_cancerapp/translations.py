# Simple translation dictionary for Swahili
SWAHILI_TRANSLATIONS = {
    # Dashboard and Navigation
    "Breast Cancer AI Dashboard": "Dashibodi ya AI ya Saratani ya Matiti",
    "Advanced AI-powered breast cancer detection and risk assessment": "Ugunduzi wa juu wa saratani ya matiti unaoendeshwa na AI na tathmini ya hatari",
    "Image Analysis": "Uchambuzi wa Picha",
    "Risk Assessment": "Tathmini ya Hatari",
    "Patients Analyzed": "Wagonjwa Waliotathminiwa",
    "Model Accuracy": "Usahihi wa Mfumo",
    "Clinical Decision Support": "Msaada wa Maamuzi ya Kliniki",
    
    # Medical Terms
    "Benign": "Si ya Kansa",
    "Malignant": "Ya Kansa",
    "Low Risk": "Hatari ya Chini",
    "High Risk": "Hatari ya Juu",
    "Prediction": "Ubashiri",
    "Confidence": "Uhakika",
    "Stage": "Hatua",
    
    # Actions
    "Analyze Image": "Chambua Picha",
    "Assess Risk": "Tathmini Hatari",
    "Upload Image": "Pakia Picha",
    "View Report": "Ona Ripoti",
    "Export Report": "Toa Ripoti",
    "Back to Dashboard": "Rudi kwenye Dashibodi",
    
    # User Interface
    "Login": "Ingia",
    "Logout": "Toka",
    "Username": "Jina la Mtumiaji",
    "Password": "Nywila",
    "Profile": "Wasifu",
    "Language": "Lugha",
    
    # Common Messages
    "Welcome": "Karibu",
    "Success": "Mafanikio",
    "Error": "Kosa",
    "Loading": "Inapakia",
    "Search": "Tafuta",
    "Filter": "Chuja",
    "Date": "Tarehe",
    "Time": "Saa",
    
    # Statistics
    "Total": "Jumla",
    "Count": "Hesabu",
    "Percentage": "Asilimia",
    "Average": "Wastani",
    
    # Medical Labels
    "Age": "Umri",
    "Gender": "Jinsia",
    "Medical History": "Historia ya Matibabu",
    "Family History": "Historia ya Familia",
    "Symptoms": "Dalili",
    "Diagnosis": "Ugunduzi",
    "Treatment": "Matibabu",
    "Recommendations": "Mapendekezo",
    
    # Navigation Labels
    "Dashboard": "Dashibodi",
    "Home": "Nyumbani",
    "Reports": "Ripoti",
    "Analytics": "Uchambuzi",
    "Settings": "Mipangilio",
    
    # Time Related
    "Today": "Leo",
    "This Month": "Mwezi Huu",
    "This Year": "Mwaka Huu",
    "All Time": "Wakati Wote",
    
    # Image Analysis Results
    "Image Analysis Results": "Matokeo ya Uchambuzi wa Picha",
    "AI-powered analysis of uploaded histopathology image": "Uchambuzi unaoendeshwa na AI wa picha iliyopakiliwa ya histopathology",
    "Medical Recommendations": "Mapendekezo ya Matibabu",
    "Immediate Actions": "Hatua za Haraka",
    "Follow-up Care": "Matunzo ya Kufuatia",
    "Treatment Planning": "Mpango wa Matibabu",
    "Lifestyle Recommendations": "Mapendekezo ya Maisha",
    "Monitoring": "Ufuatiliaji",
    "Support Services": "Huduma za Msaada",
    
    # Reports
    "Breast Cancer Reports & Analytics": "Ripoti na Uchambuzi wa Saratani ya Matiti",
    "Comprehensive insights and clinical reporting": "Mawazo ya kina na ripoti za kliniki",
    "AI-powered histopathology image analysis": "Uchambuzi wa picha za histopathology unaoendeshwa na AI",
    "Risk Assessment Analytics": "Uchambuzi wa Tathmini ya Hatari",
    "Comprehensive breast cancer risk assessment reports and insights": "Ripoti za kina za tathmini ya hatari ya saratani ya matiti na mawazo",
    "Image Analysis Analytics": "Uchambuzi wa Uchambuzi wa Picha",
    "AI-powered histopathology image analysis reports and insights": "Ripoti na mawazo ya uchambuzi wa picha za histopathology unaoendeshwa na AI",
    
    # Card descriptions
    "Histopathology & Mammography": "Histopathology na Mammography",
    "Patient Risk Analysis": "Uchambuzi wa Hatari ya Mgonjwa",
    "All time image analyses": "Uchambuzi wa picha wakati wote",
    "All time assessments": "Tathmini zote wakati wote",
    "Low risk majority": "Wengi wana hatari ya chini",
    "High risk minority": "Wachache wana hatari ya juu",
    "Benign majority": "Wengi si ya kansa",
    "Malignant minority": "Wachache ni ya kansa",
    "Benign majority": "Wengi si ya kansa",
    "Malignant minority": "Wachache ni ya kansa",
}

def get_translation(text, language='en'):
    """Get translation for text based on language"""
    if language == 'sw' and text in SWAHILI_TRANSLATIONS:
        return SWAHILI_TRANSLATIONS[text]
    return text
