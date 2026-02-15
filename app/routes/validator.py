from flask import Blueprint, render_template, jsonify, request, session
import uuid
from app.db import supabase_admin
from app.storage import storage
from app.helpers import login_required, strip_exif

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
        # Generate signed URL (valid for 1 hour)
        url = storage.create_signed_url(pic['storage_path'], 3600)
        pictures.append({'url': url, 'path': pic['storage_path']})

    # Fetch comments with pictures
    comments_response = supabase_admin.table('comments').select('*').eq('report_id', report_id).order('created_at', desc=False).execute()
    comments = []

    for comment in (comments_response.data or []):
        # Fetch pictures for this comment
        pictures_response = supabase_admin.table('comment_pictures').select('*').eq('comment_id', comment['id']).execute()

        comment_pictures = []
        for pic in (pictures_response.data or []):
            url = storage.create_signed_url(pic['storage_path'], 3600)
            comment_pictures.append({'url': url, 'path': pic['storage_path'], 'id': pic['id']})

        comment['pictures'] = comment_pictures
        comments.append(comment)

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
    """Add comment to report with optional pictures"""
    try:
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Content required'}), 400

        # Insert comment
        comment_response = supabase_admin.table('comments').insert({
            'report_id': report_id,
            'user_id': session['user_id'],
            'text': content
        }).execute()

        comment_id = comment_response.data[0]['id']

        # Handle picture uploads (optional)
        files = request.files.getlist('pictures')

        if files and files[0].filename:  # Check if any files were actually uploaded
            # Validate file count
            if len(files) > 10:
                return jsonify({'error': 'Maximum 10 pictures allowed'}), 400

            ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
            MAX_SIZE = 10 * 1024 * 1024  # 10MB

            for file in files:
                if file and file.filename:
                    if file.content_type not in ALLOWED_TYPES:
                        return jsonify({'error': f'Invalid file type: {file.filename}'}), 400

                    file.seek(0, 2)
                    size = file.tell()
                    file.seek(0)

                    if size > MAX_SIZE:
                        return jsonify({'error': f'File too large: {file.filename}'}), 400

            # Upload pictures
            for file in files:
                if file and file.filename:
                    image_data = file.read()
                    clean_image_data = strip_exif(image_data)

                    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                    filename = f"{report_id}/comments/{comment_id}/{uuid.uuid4()}.{ext}"

                    storage.upload(filename, clean_image_data, file.content_type)

                    supabase_admin.table('comment_pictures').insert({
                        'comment_id': comment_id,
                        'storage_path': filename
                    }).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
