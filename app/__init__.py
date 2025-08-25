from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object('config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'routes.login'
    
    with app.app_context():
        # Import parts of our application
        from . import routes
        from . import models
        
        # Register blueprints
        app.register_blueprint(routes.bp)
        
        # Create database tables for our models
        db.create_all()

    return app
