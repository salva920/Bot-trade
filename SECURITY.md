# Política de Seguridad

## Versiones Soportadas

Usa esta sección para decirle a las personas qué versiones de tu proyecto están actualmente siendo soportadas con actualizaciones de seguridad.

| Versión | Soportada          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad en este proyecto, por favor sigue estos pasos:

### 1. **NO** reportes la vulnerabilidad públicamente
- No crees un issue público en GitHub
- No publiques en foros o redes sociales
- No envíes emails a listas de distribución públicas

### 2. Reporta la vulnerabilidad de forma privada
Envía un email a [tu-email@ejemplo.com] con:
- Descripción detallada de la vulnerabilidad
- Pasos para reproducir el problema
- Impacto potencial de la vulnerabilidad
- Sugerencias de mitigación (si las tienes)

### 3. Proceso de respuesta
- Recibirás confirmación en 48 horas
- Evaluaremos la vulnerabilidad en 7 días
- Te mantendremos informado del progreso
- Coordinaremos la divulgación pública

## Tipos de Vulnerabilidades

### Críticas
- Exposición de credenciales de trading
- Ejecución de código remoto
- Acceso no autorizado a cuentas MT5
- Manipulación de órdenes de trading

### Altas
- Exposición de datos sensibles
- Vulnerabilidades de autenticación
- Ataques de inyección
- Cross-site scripting (XSS)

### Medias
- Vulnerabilidades de información
- Problemas de configuración
- Logs que exponen información sensible

## Mejores Prácticas de Seguridad

### Para Desarrolladores
- Nunca subas credenciales reales al repositorio
- Usa variables de entorno para configuraciones sensibles
- Valida todas las entradas de usuario
- Mantén las dependencias actualizadas
- Revisa el código regularmente

### Para Usuarios
- Usa siempre cuentas demo para pruebas
- No compartas credenciales de trading
- Mantén el software actualizado
- Usa contraseñas fuertes
- Monitorea las actividades de trading

## Actualizaciones de Seguridad

- Las vulnerabilidades críticas se parchean en 24-48 horas
- Las vulnerabilidades altas se parchean en 1 semana
- Las vulnerabilidades medias se parchean en 2 semanas
- Todas las actualizaciones se anuncian en el changelog

## Agradecimientos

Agradecemos a todos los investigadores de seguridad que reportan vulnerabilidades de forma responsable. Sus contribuciones ayudan a mantener este proyecto seguro para todos los usuarios.

---

**Nota**: Este proyecto es para fines educativos. Siempre prueba en cuenta demo antes de usar dinero real.
