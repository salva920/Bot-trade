# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentación completa del proyecto
- Configuración para GitHub
- Templates de issues y pull requests
- Políticas de seguridad y contribución

## [1.0.0] - 2024-08-29

### Added
- Bot de trading con estrategia de confluencia de 4 timeframes
- Aplicación web con dashboard en tiempo real
- Integración completa con MetaTrader 5
- Estrategia avanzada con múltiples indicadores técnicos
- Gestión de riesgo dinámica
- Filtros adaptativos según condiciones de mercado
- Sistema de configuración web
- Socket.IO para actualizaciones en tiempo real
- Interfaz moderna con Bootstrap
- Documentación completa de la estrategia

### Features
- **Estrategia de Trading**:
  - Confluencia D1, H4, M15, M5
  - Indicadores: EMA, ADX, RSI, ATR, Volumen, Pendiente
  - Filtros dinámicos según volatilidad
  - Gestión de posiciones abiertas

- **Aplicación Web**:
  - Dashboard en tiempo real
  - Configuración dinámica
  - Monitoreo de tendencias
  - Estadísticas de trading
  - Alertas de señales

- **Integración MT5**:
  - Conexión automática
  - Ejecución de órdenes
  - Obtención de datos multi-timeframe
  - Gestión de sesiones

### Technical
- Python 3.11+
- Flask + Socket.IO
- MetaTrader5 API
- Pandas + NumPy + SciPy
- Bootstrap 5.3
- Vercel deployment ready

### Security
- Variables de entorno para credenciales
- Validación de entradas
- Protección contra inyección
- Logs seguros

## [0.9.0] - 2024-08-28

### Added
- Estrategia básica de trading
- Conexión MT5
- Indicadores técnicos básicos
- Sistema de backtesting

### Changed
- Mejoras en la lógica de entrada
- Optimización de filtros
- Refinamiento de parámetros

## [0.8.0] - 2024-08-27

### Added
- Estructura inicial del proyecto
- Configuración básica MT5
- Indicadores técnicos fundamentales
- Sistema de logging

### Fixed
- Errores de conexión MT5
- Problemas de importación
- Configuración de timeframes

---

## Notas de Versión

### Versionado
- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de bugs compatibles

### Compatibilidad
- Python 3.11+
- MetaTrader 5 (Windows)
- Navegadores modernos (Chrome, Firefox, Safari, Edge)

### Breaking Changes
- Versión 1.0.0: Primera versión estable
- No hay breaking changes documentados hasta ahora

---

**Nota**: Este proyecto es para fines educativos. Siempre prueba en cuenta demo antes de usar dinero real.
