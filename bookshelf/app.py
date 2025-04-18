from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///bookshelf.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from bookshelf.routes.auth import auth_bp
    from bookshelf.routes.main import main_bp
    from bookshelf.routes.books import books_bp
    from bookshelf.routes.shelves import shelves_bp
    from bookshelf.routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(shelves_bp)
    app.register_blueprint(users_bp)
    
    # Register CLI commands
    from bookshelf.utils.cli import register_commands
    register_commands(app)
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 