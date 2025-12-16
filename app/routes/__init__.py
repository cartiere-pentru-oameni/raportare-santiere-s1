from app.routes.public import bp as public_bp
from app.routes.auth import bp as auth_bp
from app.routes.admin import bp as admin_bp
from app.routes.validator import bp as validator_bp
from app.routes.permits import bp as permits_bp
from app.routes.api import bp as api_bp

__all__ = ['public_bp', 'auth_bp', 'admin_bp', 'validator_bp', 'permits_bp', 'api_bp']
