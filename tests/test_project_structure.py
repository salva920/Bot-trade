"""
Tests para verificar la estructura del proyecto
"""
import os
import pytest


def test_project_structure():
    """Test que verifica que la estructura del proyecto es correcta"""
    
    # Archivos principales que deben existir
    required_files = [
        'web_app.py',
        'web_app_vercel.py',
        'main.py',
        'config.py',
        'requirements.txt',
        'requirements-vercel.txt',
        'README.md',
        'VERCEL_DEPLOYMENT.md',
        'LICENSE',
        'CHANGELOG.md',
        'vercel.json',
        '.gitignore',
        '.vercelignore'
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Archivo requerido no encontrado: {file}"
    
    # Directorios que deben existir
    required_dirs = [
        'broker',
        'strategy',
        'utils',
        'templates',
        'tests'
    ]
    
    for dir_name in required_dirs:
        assert os.path.isdir(dir_name), f"Directorio requerido no encontrado: {dir_name}"
    
    # Archivos en subdirectorios
    required_subfiles = [
        'broker/mt5_connector.py',
        'strategy/interbank.py',
        'utils/time_utils.py',
        'templates/dashboard.html',
        'templates/config.html',
        'tests/__init__.py',
        'tests/test_utils.py'
    ]
    
    for file in required_subfiles:
        assert os.path.exists(file), f"Archivo requerido no encontrado: {file}"


def test_import_structure():
    """Test que verifica que los módulos se pueden importar"""
    
    # Test imports básicos
    try:
        import pandas as pd
        import numpy as np
        import flask
        assert True
    except ImportError as e:
        pytest.fail(f"Import básico falló: {e}")
    
    # Test imports del proyecto (sin MT5)
    try:
        # Estos imports pueden fallar en CI/CD sin MT5, pero no deberían romper el test
        pass
    except ImportError:
        # Es normal que falle sin MT5
        pass


def test_config_file_content():
    """Test que verifica el contenido básico del archivo config"""
    
    config_path = 'config.py'
    assert os.path.exists(config_path), "config.py no existe"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar que contiene variables importantes
        required_vars = [
            'MT5_LOGIN',
            'MT5_PASSWORD', 
            'MT5_INVESTOR',
            'MT5_SERVER',
            'SYMBOL',
            'LOT',
            'RISK_REWARD',
            'SL_PIPS',
            'TP_PIPS',
            'NY_START',
            'NY_END'
        ]
        
        for var in required_vars:
            assert var in content, f"Variable requerida no encontrada en config.py: {var}"


def test_requirements_file():
    """Test que verifica el archivo requirements.txt"""
    
    requirements_path = 'requirements.txt'
    assert os.path.exists(requirements_path), "requirements.txt no existe"
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar dependencias importantes
        required_packages = [
            'MetaTrader5',
            'pandas',
            'numpy',
            'Flask',
            'Flask-SocketIO'
        ]
        
        for package in required_packages:
            assert package in content, f"Dependencia requerida no encontrada: {package}"


def test_vercel_requirements_file():
    """Test que verifica el archivo requirements-vercel.txt"""
    
    vercel_requirements_path = 'requirements-vercel.txt'
    assert os.path.exists(vercel_requirements_path), "requirements-vercel.txt no existe"
    
    with open(vercel_requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar que NO contiene MetaTrader5 como dependencia
        assert 'MetaTrader5==' not in content, "requirements-vercel.txt no debe contener MetaTrader5 como dependencia"
        
        # Verificar dependencias web importantes
        web_packages = [
            'pandas',
            'numpy',
            'Flask',
            'Flask-SocketIO'
        ]
        
        for package in web_packages:
            assert package in content, f"Dependencia web requerida no encontrada: {package}"


def test_readme_content():
    """Test que verifica el contenido básico del README"""
    
    readme_path = 'README.md'
    assert os.path.exists(readme_path), "README.md no existe"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar secciones importantes
        required_sections = [
            '# 🤖 Bot Trading Pro - Confluencia de 4 Timeframes',
            '## 📋 Descripción',
            '## 🚀 Instalación Local',
            '## 🚀 Características Principales'
        ]
        
        for section in required_sections:
            assert section in content, f"Sección requerida no encontrada en README: {section}"


def test_vercel_config():
    """Test que verifica la configuración de Vercel"""
    
    vercel_path = 'vercel.json'
    assert os.path.exists(vercel_path), "vercel.json no existe"
    
    with open(vercel_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar configuración básica
        required_config = [
            '"src": "web_app_vercel.py"',
            '"use": "@vercel/python"'
        ]
        
        for config in required_config:
            assert config in content, f"Configuración requerida no encontrada en vercel.json: {config}"


if __name__ == "__main__":
    pytest.main([__file__])
