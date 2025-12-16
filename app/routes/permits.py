from flask import Blueprint, render_template, jsonify, request, session
from app.db import supabase, supabase_admin
from app.helpers import login_required

bp = Blueprint('permits', __name__)


@bp.route('/permits')
def search():
    """Public search interface for building permits"""
    return render_template('permits/search.html')


@bp.route('/api/permits/search')
def api_search():
    """API endpoint for searching permits"""
    try:
        query = request.args.get('q', '').strip()
        issuer = request.args.get('issuer', 'all')  # all, ps1, pmb
        limit = min(int(request.args.get('limit', 50)), 100)

        if not query or len(query) < 3:
            return jsonify({'error': 'Query must be at least 3 characters'}), 400

        # Build query
        db_query = supabase.table('permits').select('*')

        # Filter by issuer
        if issuer in ['ps1', 'pmb']:
            db_query = db_query.eq('issuer', issuer)

        # Search in address (use ilike for case-insensitive partial match)
        db_query = db_query.ilike('address', f'%{query}%')

        # Order and limit
        db_query = db_query.order('created_at', desc=True).limit(limit)

        response = db_query.execute()
        permits = response.data or []

        return jsonify({
            'success': True,
            'total': len(permits),
            'permits': permits
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/permits/metadata')
def api_metadata():
    """Get metadata about permits data"""
    try:
        response = supabase.table('permits_metadata').select('*').execute()
        metadata = response.data or []
        return jsonify({'success': True, 'metadata': metadata})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/permits')
@login_required(role='admin')
def admin():
    """Admin interface for managing permits data"""
    # Fetch metadata
    response = supabase_admin.table('permits_metadata').select('*').execute()
    metadata = response.data or []

    return render_template('admin/permits.html', metadata=metadata)


@bp.route('/admin/permits/refresh/<issuer>', methods=['POST'])
@login_required(role='admin')
def admin_refresh(issuer):
    """Trigger refresh of permits data"""
    if issuer not in ['ps1', 'pmb']:
        return jsonify({'error': 'Invalid issuer'}), 400

    try:
        # Update status to running
        supabase_admin.table('permits_metadata').update({
            'status': 'running',
            'error_message': None,
            'scraped_by_username': session.get('username')
        }).eq('issuer', issuer).execute()

        # Import and run the appropriate scraper
        if issuer == 'ps1':
            from app.scrapers.ps1 import scrape_permits
        else:
            from app.scrapers.pmb import scrape_permits

        permits_data = scrape_permits()

        # Delete old permits for this issuer
        print(f"[{issuer.upper()}] Deleting old permits from database...")
        supabase_admin.table('permits').delete().eq('issuer', issuer).execute()

        # Insert new permits
        permits_to_insert = []
        for permit in permits_data:
            permits_to_insert.append({
                'issuer': issuer,
                'address': permit['address'],
                'data': permit['data'],
                'source_url': permit['source'].get('url', '')
            })

        # Insert in batches of 500
        print(f"[{issuer.upper()}] Inserting {len(permits_to_insert)} permits into database...")
        batch_size = 500
        for i in range(0, len(permits_to_insert), batch_size):
            batch = permits_to_insert[i:i+batch_size]
            supabase_admin.table('permits').insert(batch).execute()
            print(f"[{issuer.upper()}]   Inserted batch {i//batch_size + 1}/{(len(permits_to_insert)-1)//batch_size + 1}")

        # Update metadata
        supabase_admin.table('permits_metadata').update({
            'total_count': len(permits_to_insert),
            'last_scraped_at': 'now()',
            'status': 'idle',
            'error_message': None,
            'updated_at': 'now()'
        }).eq('issuer', issuer).execute()

        return jsonify({
            'success': True,
            'message': f'Successfully refreshed {len(permits_to_insert)} permits from {issuer.upper()}'
        })

    except Exception as e:
        supabase_admin.table('permits_metadata').update({
            'status': 'error',
            'error_message': str(e)
        }).eq('issuer', issuer).execute()
        return jsonify({'error': str(e)}), 500
