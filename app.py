from flask import Flask
from models import db, User
from routes import main, admin
from config import Config
import os

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if User.query.count() == 0:
            admin_user = User(
                username=app.config['ADMIN_USERNAME'],
                email='admin@example.com'
            )
            admin_user.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin_user)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
