import os  # <--- ضروري لقراءة متغيرات Docker
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics # <--- متطلب الديف أوبس

# 1. Create a global mongo instance
mongo = PyMongo()

def create_app():
    """Application factory function."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates'
    )

    # 2. --- MongoDB Configuration (FIXED) ---
    # نستخدم os.getenv لقراءة الرابط من Docker.
    # إذا لم نجده (مثل التشغيل المحلي)، نستخدم localhost كاحتياط.
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart_office")

    # 3. Initialize PyMongo
    mongo.init_app(app)

    # --- DevOps Challenge Requirements ---
    metrics = PrometheusMetrics(app) # تفعيل المراقبة

    @app.route('/health') # نقطة فحص الصحة
    def health_check():
        # نفحص الاتصال بقاعدة البيانات للتأكد أن التطبيق "جاهز" تماماً
        try:
            mongo.db.command('ping')
            return jsonify(status="healthy", db="connected"), 200
        except Exception as e:
            return jsonify(status="unhealthy", error=str(e)), 500
    # -------------------------------------

    # --- Import & Register Blueprints ---
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