from flask import Flask
from flask_mysqldb import MySQL
from app.instance.config import Config


mysql = MySQL()

def create_app():
    from setup_db import setup_database

    app = Flask(__name__)
    
    app.config.from_object(Config)
    mysql.init_app(app)

    with app.app_context():
        setup_database()


    # Import and register routes
    from app.routes.auth_route import auth_bp
    from app.routes.user_route import user_bp
    from app.routes.task_route import task_bp
    from app.routes.trash_route import trash_bp
    from app.routes.feedback_route import feedback_bp

    app.register_blueprint(feedback_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(trash_bp)

    return app
