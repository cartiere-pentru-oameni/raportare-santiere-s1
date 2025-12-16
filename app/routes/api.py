from flask import Blueprint, jsonify, request
from app.db import supabase, supabase_admin
from app.helpers import format_report

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/reports', methods=['GET'])
def reports():
    """API endpoint for reports data"""
    response = supabase.table('reports').select('*').execute()

    formatted_reports = []
    for r in (response.data or []):
        report = format_report(r)

        # Hide user-generated content for pending reports
        if r['status'] == 'pending':
            report['description'] = None
            report['pictures'] = []
            report['location']['address'] = None
        else:
            # Fetch pictures for non-pending reports
            pictures_response = supabase.table('pictures').select('*').eq('report_id', r['id']).execute()
            report['pictures'] = [p['storage_path'] for p in pictures_response.data] if pictures_response.data else []

        formatted_reports.append(report)

    return jsonify(formatted_reports)


@bp.route('/statistics')
def statistics():
    """API endpoint for statistics"""
    response = supabase.table('reports').select('*').execute()
    reports = response.data or []

    stats = {
        'total': len(reports),
        'by_status': {},
        'by_type': {}
    }

    for report in reports:
        stats['by_status'][report['status']] = stats['by_status'].get(report['status'], 0) + 1
        stats['by_type'][report['type']] = stats['by_type'].get(report['type'], 0) + 1

    return jsonify(stats)


@bp.route('/contact', methods=['POST'])
def contact():
    """Submit anonymous contact message"""
    try:
        data = request.get_json()
        email = data.get('email')  # Optional
        message = data.get('message')

        if not message or not message.strip():
            return jsonify({'error': 'Message is required'}), 400

        supabase_admin.table('contact_messages').insert({
            'email': email.strip() if email else None,
            'message': message.strip()
        }).execute()

        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
