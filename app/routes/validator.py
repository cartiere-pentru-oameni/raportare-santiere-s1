from flask import Blueprint, render_template, jsonify, request, session
from app.db import supabase_admin
from app.helpers import login_required

bp = Blueprint('validator', __name__, url_prefix='/validator')


@bp.route('')
@login_required(role='validator')
def dashboard():
    """Validator dashboard"""
    # Fetch all reports
    response = supabase_admin.table('reports').select('*').order('created_at', desc=True).execute()
    reports = response.data or []

    # Calculate stats
    stats = {
        'pending': sum(1 for r in reports if r['status'] == 'pending'),
        'in_review': sum(1 for r in reports if r['status'] == 'in-review'),
        'validated': sum(1 for r in reports if r['status'] == 'validated'),
        'rejected': sum(1 for r in reports if r['status'] == 'rejected')
    }

    return render_template('validator/dashboard.html', reports=reports, stats=stats)


@bp.route('/report/<report_id>')
@login_required(role='validator')
def report_detail(report_id):
    """Validator report detail view"""
    # Fetch report
    response = supabase_admin.table('reports').select('*').eq('id', report_id).execute()
    if not response.data:
        return "Report not found", 404

    report = response.data[0]

    # Fetch pictures
    pictures_response = supabase_admin.table('pictures').select('*').eq('report_id', report_id).execute()
    pictures = []
    for pic in (pictures_response.data or []):
        # Generate signed URL (valid for 1 hour) using admin client
        url = supabase_admin.storage.from_('report-pictures').create_signed_url(pic['storage_path'], 3600)
        pictures.append({'url': url['signedURL'], 'path': pic['storage_path']})

    # Fetch comments
    comments_response = supabase_admin.table('comments').select('*').eq('report_id', report_id).order('created_at', desc=False).execute()
    comments = comments_response.data or []

    return render_template('validator/report_detail.html',
                         report=report,
                         pictures=pictures,
                         comments=comments)


@bp.route('/report/<report_id>/status', methods=['POST'])
@login_required(role='validator')
def update_status(report_id):
    """Update report status"""
    try:
        status = request.form.get('status')
        if status not in ['pending', 'in-review', 'validated', 'rejected', 'resolved']:
            return jsonify({'error': 'Invalid status'}), 400

        supabase_admin.table('reports').update({'status': status}).eq('id', report_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/report/<report_id>/comment', methods=['POST'])
@login_required(role='validator')
def add_comment(report_id):
    """Add comment to report"""
    try:
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Content required'}), 400

        supabase_admin.table('comments').insert({
            'report_id': report_id,
            'author_username': session['username'],
            'content': content
        }).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
