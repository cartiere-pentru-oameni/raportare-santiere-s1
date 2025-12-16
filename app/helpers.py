from functools import wraps
from flask import session, redirect, url_for
from PIL import Image
import io


def login_required(role=None):
    """Decorator to require login and optionally a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if role:
                user_role = session.get('role')
                # Admin has access to everything
                if user_role == 'admin':
                    return f(*args, **kwargs)
                # Otherwise check exact role match
                if user_role != role:
                    return "Forbidden", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def strip_exif(image_data):
    """Remove EXIF data from image for privacy"""
    image = Image.open(io.BytesIO(image_data))

    # Create new image without EXIF
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    # Save to bytes
    output = io.BytesIO()
    image_without_exif.save(output, format=image.format or 'JPEG')
    output.seek(0)
    return output.getvalue()


def format_report(report_data):
    """Format report from DB to match frontend expectations"""
    return {
        'id': report_data['id'],
        'type': report_data['type'],
        'status': report_data['status'],
        'created_at': report_data['created_at'],
        'description': report_data.get('description'),
        'location': {
            'lat': float(report_data['location_lat']),
            'lng': float(report_data['location_lng']),
            'address': report_data.get('address')
        },
        'pictures': report_data.get('pictures', []),
        'comments': report_data.get('comments', [])
    }
