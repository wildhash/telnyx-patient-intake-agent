"""
Standalone questions module for patient intake
Defines all questions in a structured JSON-compatible format
"""

QUESTIONS = {
    "consent": {
        "id": "consent",
        "prompt": "Hello, this is an automated health intake call. Before we begin, I need your consent to record this conversation and collect your health information. Press 1 to provide consent, or press 2 to decline.",
        "type": "dtmf",
        "valid_digits": "12",
        "max_digits": 1,
        "section": "consent"
    },
    "initial_assessment": [
        {
            "id": "chief_complaint",
            "prompt": "What is the main health concern that brings you in today? After the beep, please describe your symptoms.",
            "type": "voice",
            "section": "hpi"
        },
        {
            "id": "symptom_duration",
            "prompt": "How long have you been experiencing these symptoms? Press 1 for less than a day, 2 for 1-3 days, 3 for 4-7 days, or 4 for more than a week.",
            "type": "dtmf",
            "valid_digits": "1234",
            "max_digits": 1,
            "section": "hpi"
        },
        {
            "id": "pain_level",
            "prompt": "On a scale of 1 to 10, with 10 being the worst pain, how would you rate your pain level? Please press a number from 0 to 10.",
            "type": "dtmf",
            "valid_digits": "012345678910",
            "max_digits": 2,
            "section": "hpi"
        }
    ],
    "ample_history": [
        {
            "id": "allergies",
            "prompt": "Do you have any known allergies to medications? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "ample",
            "followup": {
                "1": {
                    "id": "allergies_detail",
                    "prompt": "Please describe your medication allergies after the beep.",
                    "type": "voice"
                }
            }
        },
        {
            "id": "medications",
            "prompt": "Are you currently taking any medications? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "ample",
            "followup": {
                "1": {
                    "id": "medications_detail",
                    "prompt": "Please list your current medications after the beep.",
                    "type": "voice"
                }
            }
        },
        {
            "id": "past_medical_history",
            "prompt": "Do you have any significant past medical conditions? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "ample",
            "followup": {
                "1": {
                    "id": "past_medical_history_detail",
                    "prompt": "Please describe your past medical conditions after the beep.",
                    "type": "voice"
                }
            }
        },
        {
            "id": "last_meal",
            "prompt": "When was your last meal? Press 1 for within the last hour, 2 for 1-3 hours ago, 3 for 3-6 hours ago, or 4 for more than 6 hours ago.",
            "type": "dtmf",
            "valid_digits": "1234",
            "max_digits": 1,
            "section": "ample"
        }
    ],
    "family_history": [
        {
            "id": "heart_disease",
            "prompt": "Does anyone in your immediate family have a history of heart disease? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "family_history"
        },
        {
            "id": "diabetes",
            "prompt": "Does anyone in your immediate family have diabetes? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "family_history"
        },
        {
            "id": "cancer",
            "prompt": "Is there a history of cancer in your immediate family? Press 1 for yes, 2 for no.",
            "type": "dtmf",
            "valid_digits": "12",
            "max_digits": 1,
            "section": "family_history"
        }
    ],
    "closing": {
        "id": "closing",
        "prompt": "Thank you for completing the health intake questionnaire. Your information has been recorded and will be reviewed by a healthcare provider. You will be contacted soon. Goodbye.",
        "type": "statement",
        "section": "closing"
    }
}


def get_all_questions():
    """
    Get all questions in a flat list
    
    Returns:
        list: All questions
    """
    questions = []
    questions.append(QUESTIONS["consent"])
    questions.extend(QUESTIONS["initial_assessment"])
    questions.extend(QUESTIONS["ample_history"])
    questions.extend(QUESTIONS["family_history"])
    questions.append(QUESTIONS["closing"])
    return questions


def get_questions_by_section(section):
    """
    Get questions for a specific section
    
    Args:
        section (str): Section name (hpi, ample, family_history)
        
    Returns:
        list: Questions for that section
    """
    if section == "consent":
        return [QUESTIONS["consent"]]
    elif section == "hpi":
        return [q for q in QUESTIONS["initial_assessment"] if q.get("section") == "hpi"]
    elif section == "ample":
        return QUESTIONS["ample_history"]
    elif section == "family_history":
        return QUESTIONS["family_history"]
    elif section == "closing":
        return [QUESTIONS["closing"]]
    return []


def get_question_by_id(question_id):
    """
    Get a specific question by ID
    
    Args:
        question_id (str): Question ID
        
    Returns:
        dict: Question object or None
    """
    all_questions = get_all_questions()
    for q in all_questions:
        if q.get("id") == question_id:
            return q
    return None
