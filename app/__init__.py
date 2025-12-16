from flask import Flask
from app.config import Config


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    # Register blueprints
    from app.routes import public_bp, auth_bp, admin_bp, validator_bp, permits_bp, api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(validator_bp)
    app.register_blueprint(permits_bp)
    app.register_blueprint(api_bp)

    return app
