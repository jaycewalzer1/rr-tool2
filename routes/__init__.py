from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .subscription_routes import subscription_bp
from .misc_routes import misc_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(misc_bp)