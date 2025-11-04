"""
Tests for questions module
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from questions import get_all_questions, get_questions_by_section, get_question_by_id


def test_get_all_questions():
    """Test getting all questions"""
    questions = get_all_questions()
    assert len(questions) > 0
    assert questions[0]['id'] == 'consent'


def test_get_questions_by_section():
    """Test getting questions by section"""
    hpi_questions = get_questions_by_section('hpi')
    assert len(hpi_questions) > 0
    
    ample_questions = get_questions_by_section('ample')
    assert len(ample_questions) > 0
    
    family_questions = get_questions_by_section('family_history')
    assert len(family_questions) > 0


def test_get_question_by_id():
    """Test getting question by ID"""
    consent = get_question_by_id('consent')
    assert consent is not None
    assert consent['id'] == 'consent'
    
    chief_complaint = get_question_by_id('chief_complaint')
    assert chief_complaint is not None
    assert chief_complaint['type'] == 'voice'
    
    # Test non-existent question
    non_existent = get_question_by_id('non_existent_id')
    assert non_existent is None
