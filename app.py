from app import create_app
from app.config import Config

application = create_app()

if __name__ == '__main__':
    application.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
