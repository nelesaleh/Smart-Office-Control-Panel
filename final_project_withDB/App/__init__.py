import os
import random
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

mongo = PyMongo()

def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')

    # الإعدادات
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart_office")
    app.config["SECRET_KEY"] = "dev"

    # تهيئة المكتبات
    mongo.init_app(app)
    CORS(app)
    metrics = PrometheusMetrics(app)

    # --- هذا هو الجزء المفقود غالباً ---
    stock_gauge = metrics.info('stock_value', 'Simulated Stock Value')

    @app.route('/api/stock')
    def get_stock():
        val = random.randint(50, 150)
        stock_gauge.set(val)
        return jsonify({"current_stock": val})
    # ----------------------------------

    @app.route('/health')
    def health_check():
        try:
            mongo.db.command('ping')
            return jsonify(status="healthy", db="connected"), 200
        except Exception as e:
            return jsonify(status="unhealthy", error=str(e)), 500

    # تسجيل المخططات (Blueprints)
    from .blueprints.main import main_bp
    from .blueprints.control import control_bp
    from .blueprints.energy import energy_bp
    from .blueprints.parking import parking_bp
    from .blueprints.meeting_rooms import meeting_bp
    from .blueprints.wellness import wellness_bp
    from .blueprints.automation_rules import automation_rules_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(control_bp)
    app.register_blueprint(energy_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(meeting_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(automation_rules_bp)

    return app