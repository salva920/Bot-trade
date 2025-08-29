# Contribuyendo a Bot Trading Pro

¡Gracias por tu interés en contribuir a Bot Trading Pro! Este documento proporciona las pautas para contribuir al proyecto.

## 🚀 Cómo Contribuir

### Reportar Bugs
- Usa el template de "Bug Report" al crear un issue
- Incluye información detallada sobre el entorno
- Proporciona logs de error si es posible

### Solicitar Características
- Usa el template de "Feature Request" al crear un issue
- Describe claramente la funcionalidad deseada
- Explica por qué sería útil

### Contribuir Código
1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

## 📋 Pautas de Código

### Estilo de Código
- Sigue las convenciones de PEP 8 para Python
- Usa nombres descriptivos para variables y funciones
- Comenta el código complejo
- Mantén las funciones pequeñas y enfocadas

### Estructura del Proyecto
```
bot trading/
├── web_app.py              # Aplicación Flask principal
├── main.py                 # Script principal del bot
├── config.py              # Configuración MT5
├── broker/                # Conexión con brokers
├── strategy/              # Estrategias de trading
├── utils/                 # Utilidades
└── templates/             # Templates HTML
```

### Testing
- Escribe tests para nuevas funcionalidades
- Asegúrate de que todos los tests pasen
- Incluye tests para casos edge

## 🔒 Seguridad

### Datos Sensibles
- **NUNCA** subas credenciales reales
- Usa variables de entorno para configuraciones sensibles
- Si encuentras credenciales expuestas, repórtalas inmediatamente

### Trading
- Este proyecto es para fines educativos
- Siempre prueba en cuenta demo primero
- No garantizamos ganancias

## 📝 Documentación

### Comentarios
- Comenta funciones complejas
- Explica la lógica de trading
- Documenta parámetros importantes

### README
- Mantén el README actualizado
- Incluye ejemplos de uso
- Documenta cambios importantes

## 🎯 Áreas de Contribución

### Prioridad Alta
- [ ] Mejoras en la estrategia de trading
- [ ] Optimización de rendimiento
- [ ] Corrección de bugs críticos
- [ ] Mejoras en la interfaz web

### Prioridad Media
- [ ] Nuevas características de análisis
- [ ] Mejoras en la documentación
- [ ] Tests adicionales
- [ ] Optimización de código

### Prioridad Baja
- [ ] Mejoras cosméticas
- [ ] Características experimentales
- [ ] Integraciones adicionales

## 🤝 Proceso de Review

1. **Revisión de Código**: Todos los PRs serán revisados
2. **Tests**: Asegúrate de que los tests pasen
3. **Documentación**: Actualiza la documentación si es necesario
4. **Aprobación**: Se requiere aprobación antes del merge

## 📞 Contacto

Si tienes preguntas sobre cómo contribuir:
- Abre un issue en GitHub
- Revisa la documentación existente
- Consulta los issues cerrados para ejemplos

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la Licencia MIT.

---

¡Gracias por contribuir a hacer Bot Trading Pro mejor! 🚀
