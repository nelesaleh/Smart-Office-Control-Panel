import os
import random
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

# 1. تعريف الأدوات خارج الدالة (Global) لتجنب أخطاء التكرار في الاختبارات
mongo = PyMongo()
metrics = PrometheusMetrics(app=None) # نهيئها فارغة

# تعريف المقياس مرة واحدة فقط هنا
stock_gauge = metrics.info('stock_value', 'Simulated Stock Value')

def create_app():
    """Application factory function."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates'
    )

    # 2. الإعدادات
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart_office")
    app.config["SECRET_KEY"] = "dev"

    # 3. ربط الأدوات بالتطبيق
    mongo.init_app(app)
    CORS(app)
    metrics.init_app(app) # تفعيل المراقبة هنا

    # 4. نقطة النهاية الجديدة للأسهم (Stock Route)
    @app.route('/api/stock')
    def get_stock():
        val = random.randint(50, 150)
        stock_gauge.set(val) # تحديث القيمة في Prometheus
        return jsonify({"current_stock": val})

    # 5. نقطة فحص الصحة
    @app.route('/health')
    def health_check():
        try:
            mongo.db.command('ping')
            return jsonify(status="healthy", db="connected"), 200
        except Exception as e:
            return jsonify(status="unhealthy", error=str(e)), 500

    # تسجيل المخططات
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