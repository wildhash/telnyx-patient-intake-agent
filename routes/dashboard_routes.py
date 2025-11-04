"""
Dashboard routes for web interface
"""

from flask import Blueprint, render_template, jsonify
from models import db, Patient, Call, Transcript
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@bp.route('/calls')
def calls():
    """Calls management page"""
    return render_template('calls.html')


@bp.route('/patients')
def patients():
    """Patients management page"""
    return render_template('patients.html')


@bp.route('/call/<int:call_id>')
def call_detail(call_id):
    """Call detail page"""
    return render_template('call_detail.html', call_id=call_id)
