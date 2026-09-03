import os

def pytest_configure(config):
    """
    تُنفذ هذه الدالة تلقائياً قبل بدء جمع الاختبارات (Collection).
    نضبط فيها متغيرات البيئة الخاصة بالاختبارات لتتجاوز أي ملف .env.
    """
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "True"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["SECRET_KEY"] = "pytest-secret-key-for-testing-only-12345"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["BASE_URL"] = "http://testserver"
