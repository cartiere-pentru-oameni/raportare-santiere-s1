from flask import Blueprint, render_template, jsonify, request
import bcrypt
from app.db import supabase_admin
from app.helpers import login_required

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
                supabase_admin.storage.from_('report-pictures').remove([pic['storage_path']])
            except:
                pass  # Continue even if storage deletion fails

        # Delete report (cascade will delete pictures and comments from DB)
        supabase_admin.table('reports').delete().eq('id', report_id).execute()

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
