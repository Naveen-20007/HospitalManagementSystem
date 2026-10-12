"""
CareSync Reports and Analytics Blueprint
Generates appointment volume summaries, doctor workload metrics, and date-range statistics.
"""
from datetime import date, timedelta
from flask import Blueprint, render_template, request, session
from app.routes.auth import role_required
from app.models import get_report_data, list_doctors

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@role_required('admin')
def index():
    """Render analytical report dashboard with date and doctor filters."""
    # Default to last 30 days
    today = date.today()
    default_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    default_end = today.strftime("%Y-%m-%d")

    start_date = request.args.get('start_date', default_start).strip()
    end_date = request.args.get('end_date', default_end).strip()
    doctor_id = request.args.get('doctor_id', type=int)

    report = get_report_data(start_date=start_date, end_date=end_date, doctor_id=doctor_id)
    doctors = list_doctors()

    return render_template(
        'reports/index.html',
        report=report,
        start_date=start_date,
        end_date=end_date,
        selected_doctor=doctor_id,
        doctors=doctors
    )
