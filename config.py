"""Configuration de l'application."""

import os


class Config:
    """Configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration de développement."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration de production."""
    DEBUG = False


class TestingConfig(Config):
    """Configuration de test."""
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}