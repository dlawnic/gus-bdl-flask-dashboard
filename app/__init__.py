from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager

def create_app(config_object=Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Create tables automatically (simplifies local run; migrations optional)
    with app.app_context():
        db.create_all()

    from .auth.routes import bp as auth_bp
    from .dashboard.routes import bp as dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
