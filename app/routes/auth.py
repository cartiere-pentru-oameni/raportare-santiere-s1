from flask import Blueprint, render_template, request, session, redirect, url_for
import bcrypt
from app.db import supabase_admin

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for officials"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error='Username and password required')

        # Fetch user from database
        response = supabase_admin.table('official_users').select('*').eq('username', username).execute()

        if not response.data:
            return render_template('login.html', error='Invalid credentials')

        user = response.data[0]

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'validator':
                return redirect(url_for('validator.dashboard'))
            else:
                return redirect(url_for('public.home'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('public.home'))
