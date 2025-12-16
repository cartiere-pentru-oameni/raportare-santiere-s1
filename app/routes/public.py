from flask import Blueprint, render_template, jsonify, request, session
import uuid
from app.db import supabase, supabase_admin
from app.helpers import strip_exif, format_report

bp = Blueprint('public', __name__)


@bp.route('/')
def home():
    """Home page with overview"""
    return render_template('home.html')


@bp.route('/report/new', methods=['GET'])
def new_report():
    """Report submission form"""
    return render_template('report_form.html')


@bp.route('/api/reports', methods=['POST'])
def create_report():
    """Submit a new report"""
    try:
        # Get form data
        report_type = request.form.get('type')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        address = request.form.get('address', '').strip() or None
        description = request.form.get('description', '').strip() or None

        # Validate required fields
        if not all([report_type, lat, lng]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Handle picture uploads
        files = request.files.getlist('pictures')

        # Validate file count
        if len(files) > 10:
            return jsonify({'error': 'Maximum 10 pictures allowed'}), 400

        # Validate files
        ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
        MAX_SIZE = 10 * 1024 * 1024  # 10MB

        for file in files:
            if file and file.filename:
                if file.content_type not in ALLOWED_TYPES:
                    return jsonify({'error': f'Invalid file type: {file.filename}. Only JPEG, PNG, WebP allowed.'}), 400

                # Check file size by reading
                file.seek(0, 2)  # Seek to end
                size = file.tell()
                file.seek(0)  # Reset to start

                if size > MAX_SIZE:
                    return jsonify({'error': f'File too large: {file.filename}. Max 10MB.'}), 400

        # Insert report
        report_data = {
            'type': report_type,
            'location_lat': float(lat),
            'location_lng': float(lng),
            'address': address,
            'description': description,
            'status': 'pending'
        }

        # Track if submitted by official user (validator/admin)
        if 'user_id' in session:
            report_data['submitted_by_user_id'] = session['user_id']
            report_data['submitted_by_username'] = session['username']

        response = supabase.table('reports').insert(report_data).execute()
        report_id = response.data[0]['id']

        # Upload pictures
        for file in files:
            if file and file.filename:
                # Read and strip EXIF
                image_data = file.read()
                clean_image_data = strip_exif(image_data)

                # Generate unique filename
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                filename = f"{report_id}/{uuid.uuid4()}.{ext}"

                # Upload to Supabase Storage
                supabase.storage.from_('report-pictures').upload(
                    filename,
                    clean_image_data,
                    {'content-type': file.content_type}
                )

                # Save picture record (use admin client to bypass RLS)
                supabase_admin.table('pictures').insert({
                    'report_id': report_id,
                    'storage_path': filename
                }).execute()

        return jsonify({'success': True, 'report_id': report_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports')
def reports_map():
    """Map view with all reports"""
    return render_template('reports_map.html')


@bp.route('/report/<report_id>')
def report_detail(report_id):
    """Individual report detail page"""
    response = supabase.table('reports').select('*').eq('id', report_id).execute()

    if not response.data:
        return "Report not found", 404

    report_data = response.data[0]
    report = format_report(report_data)

    # Fetch comments
    comments_response = supabase.table('comments').select('*').eq('report_id', report_id).execute()
    report['comments'] = comments_response.data or []

    # Fetch pictures with signed URLs (only for non-pending reports)
    report['pictures'] = []
    if report_data['status'] in ['in-review', 'validated', 'resolved']:
        pictures_response = supabase_admin.table('pictures').select('*').eq('report_id', report_id).execute()
        for pic in (pictures_response.data or []):
            url = supabase_admin.storage.from_('report-pictures').create_signed_url(pic['storage_path'], 3600)
            report['pictures'].append({'url': url['signedURL'], 'path': pic['storage_path']})

    return render_template('report_detail.html', report=report)


@bp.route('/statistics')
def statistics():
    """Statistics dashboard"""
    return render_template('statistics.html')


@bp.route('/tutorial')
def tutorial():
    """Tutorial on checking paperwork"""
    return render_template('tutorial.html')


@bp.route('/info')
def info():
    """Information page"""
    return render_template('info.html')


@bp.route('/contact')
def contact():
    """Anonymous contact form"""
    return render_template('contact.html')
