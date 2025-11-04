"""Configuration de l'application."""

import os


class Config:
    """Configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    LOAD_SAMPLE_DATA = True
    DB_AUTO_CREATE = True  # crée les tables si nécessaire quand la DB est active


class DevelopmentConfig(Config):
    """Configuration de développement."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuration de production."""
    DEBUG = False
    # Ne pas charger de données de démo en production
    LOAD_SAMPLE_DATA = False
    DB_AUTO_CREATE = True  # Render sans predeploy: créer les tables au démarrage


class TestingConfig(Config):
    """Configuration de test."""
    TESTING = True
    LOAD_SAMPLE_DATA = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
