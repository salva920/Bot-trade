# 🚀 Despliegue en Vercel

## 📋 Descripción

Este proyecto está configurado para funcionar tanto en **desarrollo local** (con MetaTrader5) como en **producción web** (Vercel) sin dependencias de MT5.

## 🔧 Configuración para Vercel

### Archivos Específicos de Vercel

- **`web_app_vercel.py`**: Versión simplificada de la aplicación web sin MT5
- **`requirements.txt`**: Dependencias sin MetaTrader5 (para Vercel)
- **`requirements-local.txt`**: Dependencias con MT5 (para desarrollo local)
- **`.vercelignore`**: Archivos excluidos del despliegue
- **`vercel.json`**: Configuración de Vercel

### Modo Demo

Cuando se despliega en Vercel, la aplicación funciona en **modo demo**:

✅ **Funcionalidades disponibles:**
- Dashboard web completo
- Configuración de parámetros
- Simulación de señales de trading
- Interfaz responsive
- WebSocket en tiempo real

❌ **Funcionalidades no disponibles:**
- Conexión real a MetaTrader5
- Ejecución de órdenes reales
- Datos de mercado en tiempo real

## 🚀 Despliegue Automático

### 1. Conectar con GitHub

1. Ve a [vercel.com](https://vercel.com)
2. Conecta tu repositorio de GitHub
3. Selecciona el repositorio `Bot-trade`

### 2. Configuración del Proyecto

Vercel detectará automáticamente:
- **Framework**: Python/Flask
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: `/`
- **Install Command**: `pip install -r requirements.txt`

### 3. Variables de Entorno

```bash
FLASK_ENV=production
```

## 🔍 Estructura de Despliegue

```
vercel/
├── web_app_vercel.py          # App principal para Vercel
├── requirements.txt            # Dependencias sin MT5 (para Vercel)
├── vercel.json                # Configuración de Vercel
├── .vercelignore              # Archivos excluidos
└── templates/                 # Plantillas HTML
    ├── dashboard.html
    └── config.html
```

## 🧪 Testing del Despliegue

### Verificar Estructura

```bash
# Ejecutar tests de estructura
pytest tests/test_project_structure.py -v

# Verificar archivos de Vercel
ls -la web_app_vercel.py requirements-vercel.txt vercel.json .vercelignore
```

### Verificar Dependencias

```bash
# Verificar que requirements.txt no contiene MT5
grep -i "metatrader" requirements.txt

# Verificar dependencias web
cat requirements.txt
```

## 🚨 Solución de Problemas

### Error: MetaTrader5 no encontrado

**Causa**: Vercel intenta instalar MetaTrader5
**Solución**: Verificar que `requirements.txt` no contenga MetaTrader5

### Error: Módulo no encontrado

**Causa**: Importaciones de MT5 en el código
**Solución**: Usar `web_app_vercel.py` en lugar de `web_app.py`

### Error: Build fallido

**Causa**: Dependencias incompatibles
**Solución**: Verificar que `requirements-vercel.txt` solo contenga paquetes compatibles con Linux

## 📱 Acceso a la Aplicación

Una vez desplegada, la aplicación estará disponible en:
```
https://tu-proyecto.vercel.app
```

## 🔄 Actualizaciones

Para actualizar el despliegue:

1. **Push a main branch**: Despliegue automático
2. **Manual**: Desde el dashboard de Vercel
3. **Rollback**: Disponible en el historial de despliegues

## 📊 Monitoreo

- **Logs**: Disponibles en el dashboard de Vercel
- **Métricas**: Uptime y performance automáticos
- **Alertas**: Configurables para errores críticos

---

**Nota**: Esta configuración permite que el proyecto funcione tanto en desarrollo local (con MT5) como en producción web (sin MT5), manteniendo la funcionalidad completa en ambos entornos.
