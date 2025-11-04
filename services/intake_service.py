"""
Patient intake service
Manages the scripted intake conversation flow (HPI, AMPLE, family history)
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IntakeScript:
    """Defines the patient intake script and question flow"""
    
    # Consent script
    CONSENT = {
        'intro': "Hello, this is an automated health intake call. Before we begin, I need your consent to record this conversation and collect your health information. Press 1 to provide consent, or press 2 to decline.",
        'valid_digits': '12',
        'max_digits': 1
    }
    
    # HPI (History of Present Illness) questions
    HPI_QUESTIONS = [
        {
            'key': 'chief_complaint',
            'question': "What is the main health concern that brings you in today? After the beep, please describe your symptoms.",
            'type': 'voice'
        },
        {
            'key': 'symptom_duration',
            'question': "How long have you been experiencing these symptoms? Press 1 for less than a day, 2 for 1-3 days, 3 for 4-7 days, or 4 for more than a week.",
            'type': 'dtmf',
            'valid_digits': '1234',
            'max_digits': 1
        },
        {
            'key': 'pain_level',
            'question': "On a scale of 1 to 10, with 10 being the worst pain, how would you rate your pain level? Please press a number from 0 to 10.",
            'type': 'dtmf',
            'valid_digits': '012345678910',
            'max_digits': 2
        }
    ]
    
    # AMPLE (Medical History) questions
    AMPLE_QUESTIONS = [
        {
            'key': 'allergies',
            'question': "Do you have any known allergies to medications? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1,
            'followup': {
                '1': {
                    'question': "Please describe your medication allergies after the beep.",
                    'type': 'voice'
                }
            }
        },
        {
            'key': 'medications',
            'question': "Are you currently taking any medications? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1,
            'followup': {
                '1': {
                    'question': "Please list your current medications after the beep.",
                    'type': 'voice'
                }
            }
        },
        {
            'key': 'past_medical_history',
            'question': "Do you have any significant past medical conditions? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1,
            'followup': {
                '1': {
                    'question': "Please describe your past medical conditions after the beep.",
                    'type': 'voice'
                }
            }
        },
        {
            'key': 'last_meal',
            'question': "When was your last meal? Press 1 for within the last hour, 2 for 1-3 hours ago, 3 for 3-6 hours ago, or 4 for more than 6 hours ago.",
            'type': 'dtmf',
            'valid_digits': '1234',
            'max_digits': 1
        }
    ]
    
    # Family History questions
    FAMILY_HISTORY_QUESTIONS = [
        {
            'key': 'heart_disease',
            'question': "Does anyone in your immediate family have a history of heart disease? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1
        },
        {
            'key': 'diabetes',
            'question': "Does anyone in your immediate family have diabetes? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1
        },
        {
            'key': 'cancer',
            'question': "Is there a history of cancer in your immediate family? Press 1 for yes, 2 for no.",
            'type': 'dtmf',
            'valid_digits': '12',
            'max_digits': 1
        }
    ]
    
    # Closing message
    CLOSING = "Thank you for completing the health intake questionnaire. Your information has been recorded and will be reviewed by a healthcare provider. You will be contacted soon. Goodbye."


class IntakeService:
    """Service for managing patient intake flow"""
    
    def __init__(self):
        self.script = IntakeScript()
    
    def get_consent_prompt(self):
        """Get the consent prompt"""
        return self.script.CONSENT
    
    def get_next_question(self, call_state):
        """
        Get the next question based on call state
        
        Args:
            call_state (dict): Current state of the call intake
            
        Returns:
            dict: Next question to ask, or None if complete
        """
        section = call_state.get('current_section', 'hpi')
        question_index = call_state.get('question_index', 0)
        
        if section == 'hpi':
            questions = self.script.HPI_QUESTIONS
        elif section == 'ample':
            questions = self.script.AMPLE_QUESTIONS
        elif section == 'family_history':
            questions = self.script.FAMILY_HISTORY_QUESTIONS
        else:
            return None
        
        if question_index < len(questions):
            return questions[question_index]
        else:
            # Move to next section
            if section == 'hpi':
                call_state['current_section'] = 'ample'
                call_state['question_index'] = 0
                return self.get_next_question(call_state)
            elif section == 'ample':
                call_state['current_section'] = 'family_history'
                call_state['question_index'] = 0
                return self.get_next_question(call_state)
            else:
                return None
    
    def process_response(self, call_state, question_key, response):
        """
        Process a response and update call state
        
        Args:
            call_state (dict): Current call state
            question_key (str): Key of the question being answered
            response (str): User's response
            
        Returns:
            dict: Updated call state with response recorded
        """
        if 'responses' not in call_state:
            call_state['responses'] = {}
        
        call_state['responses'][question_key] = {
            'value': response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Increment question index
        call_state['question_index'] = call_state.get('question_index', 0) + 1
        
        return call_state
    
    def is_intake_complete(self, call_state):
        """Check if intake is complete"""
        section = call_state.get('current_section', 'hpi')
        return section == 'complete' or self.get_next_question(call_state) is None
    
    def get_closing_message(self):
        """Get the closing message"""
        return self.script.CLOSING
    
    def format_intake_data(self, call_state):
        """
        Format the collected intake data into structured format
        
        Args:
            call_state (dict): Call state with responses
            
        Returns:
            dict: Structured intake data
        """
        responses = call_state.get('responses', {})
        
        # Map responses to categories
        hpi_keys = [q['key'] for q in self.script.HPI_QUESTIONS]
        ample_keys = [q['key'] for q in self.script.AMPLE_QUESTIONS]
        family_keys = [q['key'] for q in self.script.FAMILY_HISTORY_QUESTIONS]
        
        return {
            'consent_given': call_state.get('consent_given', False),
            'consent_timestamp': call_state.get('consent_timestamp'),
            'hpi': {key: responses.get(key) for key in hpi_keys if key in responses},
            'ample': {key: responses.get(key) for key in ample_keys if key in responses},
            'family_history': {key: responses.get(key) for key in family_keys if key in responses},
            'completed_at': datetime.utcnow().isoformat()
        }
