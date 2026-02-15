from flask import Blueprint, render_template, jsonify, request
import bcrypt
import uuid
from app.db import supabase_admin
from app.storage import storage
from app.helpers import login_required, strip_exif

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('')
@login_required(role='admin')
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')


@bp.route('/users')
@login_required(role='admin')
def users():
    """User management"""
    response = supabase_admin.table('official_users').select('*').execute()
    users = response.data or []
    return render_template('admin/users.html', users=users)


@bp.route('/users/create', methods=['POST'])
@login_required(role='admin')
def create_user():
    """Create new user"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not all([username, password, role]):
            return jsonify({'error': 'All fields required'}), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert user
        supabase_admin.table('official_users').insert({
            'username': username,
            'password_hash': password_hash,
            'role': role
        }).execute()

        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_user(user_id):
    """Delete user"""
    try:
        supabase_admin.table('official_users').delete().eq('id', user_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports')
@login_required(role='admin')
def reports():
    """Admin reports management"""
    response = supabase_admin.table('reports').select('*').order('created_at', desc=True).execute()
    reports = response.data or []
    return render_template('admin/reports.html', reports=reports)


@bp.route('/report/<report_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_report(report_id):
    """Delete report and associated pictures"""
    try:
        # Fetch pictures to delete from storage
        pictures_response = supabase_admin.table('pictures').select('*').eq('report_id', report_id).execute()

        # Delete pictures from storage
        for pic in (pictures_response.data or []):
            try:
                storage.delete(pic['storage_path'])
            except:
                pass  # Continue even if storage deletion fails

        # Delete report (cascade will delete pictures and comments from DB)
        supabase_admin.table('reports').delete().eq('id', report_id).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/report/<report_id>/update', methods=['POST'])
@login_required(role='admin')
def update_report(report_id):
    """Update report type and/or description"""
    try:
        data = request.get_json()
        updates = {}

        if 'type' in data:
            valid_types = ['no-paperwork', 'noise-violation', 'pollution-violation', 'others']
            if data['type'] not in valid_types:
                return jsonify({'error': 'Tip invalid'}), 400
            updates['type'] = data['type']

        if 'description' in data:
            updates['description'] = data['description']

        if not updates:
            return jsonify({'error': 'Nicio modificare specificată'}), 400

        supabase_admin.table('reports').update(updates).eq('id', report_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/report/<report_id>/picture/<path:storage_path>/delete', methods=['POST'])
@login_required(role='admin')
def delete_picture(report_id, storage_path):
    """Delete a specific picture from a report"""
    try:
        # Delete from storage
        try:
            storage.delete(storage_path)
        except:
            pass  # Continue even if storage deletion fails

        # Delete from database
        supabase_admin.table('pictures').delete().eq('report_id', report_id).eq('storage_path', storage_path).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contact')
@login_required(role='admin')
def contact_messages():
    """Admin contact messages view"""
    response = supabase_admin.table('contact_messages').select('*').order('created_at', desc=True).execute()
    messages = response.data or []
    return render_template('admin/contact_messages.html', messages=messages)


@bp.route('/contact/<message_id>/read', methods=['POST'])
@login_required(role='admin')
def mark_message_read(message_id):
    """Mark contact message as read"""
    try:
        supabase_admin.table('contact_messages').update({'read': True}).eq('id', message_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contact/<message_id>/notes', methods=['POST'])
@login_required(role='admin')
def save_message_notes(message_id):
    """Save admin notes for contact message"""
    try:
        data = request.get_json()
        notes = data.get('notes', '')

        supabase_admin.table('contact_messages').update({'admin_notes': notes}).eq('id', message_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contact/<message_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_message(message_id):
    """Delete contact message"""
    try:
        supabase_admin.table('contact_messages').delete().eq('id', message_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Comment Management Endpoints

@bp.route('/comment/<comment_id>/update', methods=['PUT', 'POST'])
@login_required(role='admin')
def update_comment(comment_id):
    """Update comment text"""
    try:
        data = request.get_json() if request.is_json else request.form
        text = data.get('text')

        if not text or not text.strip():
            return jsonify({'error': 'Text required'}), 400

        supabase_admin.table('comments').update({
            'text': text.strip(),
            'updated_at': 'NOW()'
        }).eq('id', comment_id).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comment/<comment_id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_comment(comment_id):
    """Delete comment and all associated pictures"""
    try:
        # Fetch comment pictures to delete from storage
        pictures_response = supabase_admin.table('comment_pictures').select('*').eq('comment_id', comment_id).execute()

        # Delete pictures from S3
        for pic in (pictures_response.data or []):
            try:
                storage.delete(pic['storage_path'])
            except:
                pass  # Continue even if storage deletion fails

        # Delete comment (cascade will delete comment_pictures from DB)
        supabase_admin.table('comments').delete().eq('id', comment_id).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comment/<comment_id>/pictures', methods=['POST'])
@login_required(role='admin')
def add_comment_pictures(comment_id):
    """Add pictures to existing comment"""
    try:
        # Verify comment exists and get report_id
        comment_response = supabase_admin.table('comments').select('report_id').eq('id', comment_id).execute()
        if not comment_response.data:
            return jsonify({'error': 'Comment not found'}), 404

        report_id = comment_response.data[0]['report_id']
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
                    return jsonify({'error': f'Invalid file type: {file.filename}'}), 400

                file.seek(0, 2)
                size = file.tell()
                file.seek(0)

                if size > MAX_SIZE:
                    return jsonify({'error': f'File too large: {file.filename}'}), 400

        # Upload pictures
        uploaded_count = 0
        for file in files:
            if file and file.filename:
                # Read and strip EXIF
                image_data = file.read()
                clean_image_data = strip_exif(image_data)

                # Generate unique filename with path: {report_id}/comments/{comment_id}/{uuid}.{ext}
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                filename = f"{report_id}/comments/{comment_id}/{uuid.uuid4()}.{ext}"

                # Upload to S3
                storage.upload(filename, clean_image_data, file.content_type)

                # Save picture record
                supabase_admin.table('comment_pictures').insert({
                    'comment_id': comment_id,
                    'storage_path': filename
                }).execute()

                uploaded_count += 1

        return jsonify({'success': True, 'uploaded': uploaded_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comment/<comment_id>/picture/<path:storage_path>/delete', methods=['POST'])
@login_required(role='admin')
def delete_comment_picture(comment_id, storage_path):
    """Delete a specific picture from a comment"""
    try:
        # Delete from storage
        try:
            storage.delete(storage_path)
        except:
            pass  # Continue even if storage deletion fails

        # Delete from database
        supabase_admin.table('comment_pictures').delete()\
            .eq('comment_id', comment_id)\
            .eq('storage_path', storage_path).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
