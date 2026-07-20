import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class NLPRecommender:
    """
    NLP-based recommendation service using Hugging Face Inference API
    """
    
    def __init__(self, hf_token: str):
        self.hf_token = hf_token
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Authorization": f"Bearer {hf_token}"}
    
    def get_breast_cancer_recommendations(self, 
                                        prediction: int, 
                                        probability: float, 
                                        age: int, 
                                        risk_factors: Dict[str, str]) -> Dict[str, str]:
        """
        Generate personalized recommendations based on risk assessment results
        
        Args:
            prediction: 0 (low risk) or 1 (high risk)
            probability: Confidence score (0.0 to 1.0)
            age: Patient age
            risk_factors: Dictionary of patient risk factors
            
        Returns:
            Dictionary containing recommendation categories and text
        """
        try:
            # Create a comprehensive prompt for the model
            risk_level = "HIGH RISK" if prediction == 1 else "LOW RISK"
            confidence_percent = round(probability * 100, 1)
            
            prompt = f"""
            Based on the following breast cancer risk assessment:
            - Risk Level: {risk_level}
            - Confidence: {confidence_percent}%
            - Age: {age} years
            - Risk Factors: {', '.join([f"{k}: {v}" for k, v in risk_factors.items()])}
            
            Provide personalized medical recommendations in the following format:
            1. IMMEDIATE ACTIONS (what to do now)
            2. SCREENING SCHEDULE (when to get tested)
            3. LIFESTYLE CHANGES (preventive measures)
            4. FOLLOW-UP CARE (next steps)
            
            Make recommendations specific, actionable, and medically appropriate.
            """
            
            # Call Hugging Face API
            response = self._call_hf_api(prompt)
            
            if response:
                # Parse and structure the response
                recommendations = self._parse_recommendations(response, risk_level, age)
                return recommendations
            else:
                # Fallback to predefined recommendations
                return self._get_fallback_recommendations(prediction, probability, age, risk_factors)
                
        except Exception as e:
            logger.error(f"Error generating NLP recommendations: {e}")
            return self._get_fallback_recommendations(prediction, probability, age, risk_factors)
    
    def _call_hf_api(self, prompt: str) -> Optional[str]:
        """Call Hugging Face Inference API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
            
            logger.warning(f"HF API returned status {response.status_code}: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error calling HF API: {e}")
            return None
    
    def _parse_recommendations(self, response: str, risk_level: str, age: int) -> Dict[str, str]:
        """Parse the NLP response into structured recommendations"""
        try:
            # Clean the response
            cleaned_response = response.replace(prompt, "").strip()
            
            # Split into sections (this is a simplified parser)
            sections = {
                "immediate_actions": "Consult with your healthcare provider immediately for a comprehensive evaluation.",
                "screening_schedule": "Follow age-appropriate screening guidelines.",
                "lifestyle_changes": "Maintain a healthy lifestyle with regular exercise and balanced diet.",
                "follow_up_care": "Schedule regular follow-up appointments as recommended by your doctor."
            }
            
            # Try to extract specific recommendations from the response
            if "IMMEDIATE ACTIONS" in cleaned_response:
                immediate_start = cleaned_response.find("IMMEDIATE ACTIONS")
                next_section = cleaned_response.find("2.", immediate_start)
                if next_section == -1:
                    next_section = cleaned_response.find("SCREENING", immediate_start)
                if next_section > immediate_start:
                    sections["immediate_actions"] = cleaned_response[immediate_start:next_section].strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing recommendations: {e}")
            return self._get_fallback_recommendations(
                1 if risk_level == "HIGH RISK" else 0, 
                0.8 if risk_level == "HIGH RISK" else 0.2, 
                age, 
                {}
            )
    
    def _get_fallback_recommendations(self, 
                                    prediction: int, 
                                    probability: float, 
                                    age: int, 
                                    risk_factors: Dict[str, str]) -> Dict[str, str]:
        """Provide fallback recommendations when NLP fails"""
        
        is_high_risk = prediction == 1 and probability > 0.5
        
        # Analyze specific risk factors
        has_family_history = risk_factors.get('relatives_breast_cancer') == 'Yes'
        has_genetic_mutation = risk_factors.get('brca_mutation_or_genetic_syndrome') == 'Yes'
        has_radiation_history = risk_factors.get('history_breast_cancer_or_radiation') == 'Yes'
        
        if is_high_risk:
            # High-risk recommendations
            immediate_actions = []
            
            if probability > 0.8:
                immediate_actions.append("URGENT: Schedule comprehensive breast cancer evaluation within 2 weeks")
            else:
                immediate_actions.append("Schedule consultation with breast cancer specialist within 4 weeks")
            
            if has_genetic_mutation:
                immediate_actions.append("Immediate genetic counseling and BRCA testing confirmation")
            if has_family_history:
                immediate_actions.append("Discuss family screening protocols with genetic counselor")
            if has_radiation_history:
                immediate_actions.append("Prioritize imaging due to radiation exposure history")
            
            immediate_actions.append("Consider risk-reducing medications (tamoxifen/raloxifene) after specialist consultation")
            
            screening_schedule = []
            screening_schedule.append(f"High-risk protocol for age {age}:")
            screening_schedule.append("Annual mammogram + annual breast MRI (staggered 6 months apart)")
            screening_schedule.append("Clinical breast examination every 6 months")
            screening_schedule.append("Monthly breast self-examination")
            
            if age < 30:
                screening_schedule.append("Consider ultrasound as primary imaging modality")
            
            if has_genetic_mutation:
                screening_schedule.append("Enhanced surveillance: Consider 6-month MRI intervals")
            
            lifestyle_changes = []
            lifestyle_changes.append("Weight management: Maintain BMI 18.5-24.9 through diet and exercise")
            lifestyle_changes.append("Physical activity: 150-300 minutes moderate exercise weekly OR 75-150 minutes vigorous exercise")
            lifestyle_changes.append("Diet: Mediterranean diet rich in fruits, vegetables, whole grains, and lean proteins")
            lifestyle_changes.append("Limit alcohol: Maximum 1 drink/day (women) or avoid completely")
            lifestyle_changes.append("Avoid tobacco products completely")
            lifestyle_changes.append("Stress management: Practice mindfulness, yoga, or meditation 15-30 minutes daily")
            lifestyle_changes.append("Sleep: Aim for 7-9 hours quality sleep per night")
            
            follow_up_care = []
            follow_up_care.append("Enroll in high-risk breast cancer surveillance program")
            follow_up_care.append("Establish multidisciplinary care team (oncologist, surgeon, radiologist, genetic counselor)")
            follow_up_care.append("Keep detailed health diary including symptoms, screenings, and family history updates")
            follow_up_care.append("Discuss chemoprevention options with oncologist")
            follow_up_care.append("Consider risk-reducing surgery if BRCA positive (prophylactic mastectomy)")
            follow_up_care.append("Regular bone density scans if considering aromatase inhibitors")
            
        else:
            # Low-risk recommendations
            immediate_actions = []
            immediate_actions.append("Continue routine breast health monitoring")
            immediate_actions.append("Schedule annual wellness visit with primary care provider")
            
            if age >= 40:
                immediate_actions.append("Book mammogram screening if not done in past year")
            
            if has_family_history:
                immediate_actions.append("Discuss earlier screening with healthcare provider")
            
            screening_schedule = []
            screening_schedule.append(f"Standard screening protocol for age {age}:")
            
            if age >= 40:
                screening_schedule.append("Annual mammogram screening")
            elif age >= 25:
                screening_schedule.append("Clinical breast exam every 1-3 years")
            else:
                screening_schedule.append("Clinical breast exam every 3 years")
            
            screening_schedule.append("Monthly breast self-examination")
            screening_schedule.append("Report any breast changes immediately (lumps, pain, discharge, skin changes)")
            
            if has_family_history:
                screening_schedule.append("Consider starting mammograms 10 years before earliest family case")
            
            lifestyle_changes = []
            lifestyle_changes.append("Maintain healthy weight through balanced diet and regular exercise")
            lifestyle_changes.append("Exercise: 150 minutes moderate activity weekly (brisk walking, swimming, cycling)")
            lifestyle_changes.append("Diet: Plant-based diet with limited processed foods and red meat")
            lifestyle_changes.append("Alcohol: Limit to 1 drink daily or avoid completely")
            lifestyle_changes.append("Avoid smoking and secondhand smoke exposure")
            lifestyle_changes.append("Breastfeeding: If possible, breastfeed children (reduces risk)")
            lifestyle_changes.append("Hormone therapy: Discuss risks/benefits with provider, limit duration")
            
            follow_up_care = []
            follow_up_care.append("Annual physical examinations with breast health assessment")
            follow_up_care.append("Update family history regularly with healthcare provider")
            follow_up_care.append("Stay current with recommended preventive care and vaccinations")
            follow_up_care.append("Consider participating in breast cancer research studies if eligible")
            follow_up_care.append("Maintain health records including all screenings and results")
        
        return {
            "immediate_actions": " | ".join(immediate_actions),
            "screening_schedule": " | ".join(screening_schedule),
            "lifestyle_changes": " | ".join(lifestyle_changes),
            "follow_up_care": " | ".join(follow_up_care)
        }
    
    def get_image_analysis_recommendations(self, 
                                         prediction: int, 
                                         stage: str, 
                                         confidence: float) -> Dict[str, str]:
        """
        Generate recommendations for image analysis results
        
        Args:
            prediction: 0 (benign) or 1 (malignant)
            stage: Cancer stage if malignant
            confidence: Prediction confidence
            
        Returns:
            Dictionary containing recommendation categories and text
        """
        
        if prediction == 0:  # Benign
            immediate_actions = []
            immediate_actions.append("Benign findings confirmed - no evidence of malignancy detected")
            immediate_actions.append("Continue routine breast health monitoring")
            immediate_actions.append("Schedule annual mammogram as per standard guidelines")
            
            follow_up = []
            follow_up.append("Follow-up imaging in 6-12 months as recommended by radiologist")
            follow_up.append("Annual clinical breast examination with healthcare provider")
            follow_up.append("Maintain personal breast health diary")
            
            lifestyle = []
            lifestyle.append("Continue regular physical activity (150 minutes moderate exercise weekly)")
            lifestyle.append("Maintain healthy weight and balanced diet rich in fruits and vegetables")
            lifestyle.append("Limit alcohol intake to 1 drink daily or avoid completely")
            lifestyle.append("Perform monthly breast self-examinations")
            lifestyle.append("Get adequate sleep (7-9 hours nightly) and manage stress")
            
            monitoring = []
            monitoring.append("Report any new breast changes immediately (lumps, pain, discharge, skin changes)")
            monitoring.append("Watch for changes in breast tissue or nipple appearance")
            monitoring.append("Monitor for any new symptoms in either breast")
            monitoring.append("Keep records of all screenings and follow-up appointments")
            
            return {
                "immediate_actions": " | ".join(immediate_actions),
                "follow_up": " | ".join(follow_up),
                "lifestyle": " | ".join(lifestyle),
                "monitoring": " | ".join(monitoring)
            }
            
        else:  # Malignant
            # Enhanced stage-specific recommendations
            stage_recommendations = {
                "Stage I (Early)": "Early-stage invasive cancer (tumor size <2cm, no lymph node involvement). Treatment typically includes lumpectomy or mastectomy with sentinel lymph node biopsy, followed by radiation therapy (if lumpectomy) and possibly hormonal therapy or chemotherapy based on tumor characteristics.",
                
                "Stage II (Early)": "Early-stage cancer (tumor 2-5cm or limited lymph node involvement). Treatment involves surgery (lumpectomy or mastectomy) with lymph node evaluation, followed by radiation, chemotherapy, and/or hormonal therapy based on tumor markers and genetic testing.",
                
                "Stage II (Moderate)": "Moderate-stage cancer requiring comprehensive treatment approach. Multimodal therapy including surgery, chemotherapy, radiation, and targeted therapies based on tumor receptor status.",
                
                "Stage III (Advanced)": "Locally advanced cancer (larger tumor or extensive lymph node involvement). Requires neoadjuvant chemotherapy to shrink tumor before surgery, followed by surgery, radiation, and additional systemic therapies.",
                
                "Stage III (Moderate)": "Advanced local disease requiring aggressive treatment. Combination of chemotherapy, surgery, radiation, and targeted therapies based on comprehensive tumor profiling.",
                
                "Stage IV (Severe)": "Metastatic breast cancer. Focus on systemic therapy (chemotherapy, hormonal therapy, targeted agents, immunotherapy) to control disease and maintain quality of life. Palliative care integration recommended."
            }
            
            immediate_actions = []
            if confidence > 0.85:
                immediate_actions.append("URGENT: Consult with breast cancer specialist within 1 week")
            else:
                immediate_actions.append("Schedule breast cancer specialist consultation within 2 weeks")
            
            immediate_actions.append(f"Malignant findings detected ({stage})")
            immediate_actions.append("Request complete diagnostic workup including additional imaging if needed")
            immediate_actions.append("Consider second opinion for treatment planning")
            immediate_actions.append("Discuss genetic testing (BRCA1/2 and other relevant genes)")
            
            treatment_planning = []
            treatment_planning.append(stage_recommendations.get(stage, "Comprehensive treatment planning with multidisciplinary breast cancer team required."))
            treatment_planning.append("Request comprehensive tumor profiling (ER, PR, HER2, Ki-67, genomic assays)")
            treatment_planning.append("Discuss fertility preservation if applicable and desired")
            treatment_planning.append("Consider clinical trial eligibility for novel therapies")
            treatment_planning.append("Plan for rehabilitation services (physical therapy, lymphedema prevention)")
            
            support_services = []
            support_services.append("Connect with breast cancer navigator or patient coordinator")
            support_services.append("Access psychological counseling and emotional support services")
            support_services.append("Join breast cancer support groups (patient and caregiver support)")
            support_services.append("Contact social worker for financial and insurance assistance")
            support_services.append("Explore patient assistance programs for medications")
            support_services.append("Consider complementary therapies (nutrition counseling, acupuncture) with medical approval")
            
            follow_up = []
            follow_up.append("Establish long-term survivorship care plan with oncology team")
            follow_up.append("Schedule regular follow-up appointments (every 3-6 months initially)")
            follow_up.append("Plan for ongoing imaging surveillance as recommended")
            follow_up.append("Monitor and manage treatment side effects proactively")
            follow_up.append("Maintain comprehensive medical records and treatment summary")
            follow_up.append("Plan for transition to survivorship phase after active treatment")
            
            return {
                "immediate_actions": " | ".join(immediate_actions),
                "treatment_planning": " | ".join(treatment_planning),
                "support_services": " | ".join(support_services),
                "follow_up": " | ".join(follow_up)
            }
