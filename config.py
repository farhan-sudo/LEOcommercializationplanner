"""
Configuration file for Flask application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # File paths
    DEBRIS_FILE = 'FENGYUN debris.txt'
    
    # API settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Matplotlib settings
    MATPLOTLIB_BACKEND = 'Agg'  # Non-interactive backend
    
    # Cache settings (for future use)
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Add production-specific settings
    # DATABASE_URI = os.environ.get('DATABASE_URI')
    # REDIS_URL = os.environ.get('REDIS_URL')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
