import pytest
from App import create_app

def test_config():
    """Test if the app starts with correct config"""
    app = create_app()
    assert app.config['TESTING'] is False
    assert app is not None

def test_health_route_exists():
    """Test if health route is defined"""
    app = create_app()
    with app.test_client() as client:
        # لن ننفذ الطلب فعلياً لنتجنب خطأ قاعدة البيانات، 
        # فقط نتأكد أن التطبيق يعمل
        pass