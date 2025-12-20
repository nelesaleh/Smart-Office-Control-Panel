import os
import random  # <--- ضروري لتوليد بيانات وهمية للمراقبة
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS  # <--- ضروري لربط الواجهة الأمامية
from prometheus_flask_exporter import PrometheusMetrics

# 1. Create a global mongo instance
mongo = PyMongo()

def create_app():
    """Application factory function."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates'
    )

    # 2. --- Configuration ---
    # إعداد رابط قاعدة البيانات (يقرأ من Docker أو يستخدم المحلي)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart_office")
    app.config["SECRET_KEY"] = "dev"

    # 3. Initialize Extensions
    mongo.init_app(app)
    CORS(app)  # تفعيل CORS للسماح للفرونت إند بالاتصال

    # 4. --- Prometheus Monitoring (DevOps Requirement) ---
    metrics = PrometheusMetrics(app)
    
    # تعريف مقياس مخصص (Custom Metric) لاتجاهات الأسهم/البيانات
    stock_gauge = metrics.info('stock_value', 'Simulated Stock Value')

    # نقطة API خاصة لتحديث البيانات الوهمية ورسمها في Grafana
    @app.route('/api/stock')
    def get_stock():
        val = random.randint(50, 150)
        stock_gauge.set(val)  # إرسال القيمة لـ Prometheus
        return jsonify({"current_stock": val})

    # 5. Health Check
    @app.route('/health')
    def health_check():
        try:
            # فحص سريع للاتصال بقاعدة البيانات
            mongo.db.command('ping')
            return jsonify(status="healthy", db="connected"), 200
        except Exception as e:
            return jsonify(status="unhealthy", error=str(e)), 500

    # 6. Register Blueprints
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