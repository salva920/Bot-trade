# 🤖 Bot Trading Web Dashboard

## 📋 Descripción

Aplicación web completa para monitorear y controlar tu bot de trading en tiempo real. Incluye:

- **Dashboard en tiempo real** con Socket.IO
- **Confluencia de 4 timeframes** (D1, H4, M15, M5)
- **Configuración dinámica** desde la web
- **Estadísticas y métricas** en vivo
- **Alertas de señales** automáticas
- **Gestión de órdenes** manual

## 🚀 Características

### ✅ Dashboard Principal
- Estado del bot en tiempo real
- Confluencia de tendencias por timeframe
- Última señal detectada
- Estadísticas de trading
- Balance actual de la cuenta

### ✅ Configuración Web
- Parámetros de la estrategia
- Tamaños de lote
- Stop Loss y Take Profit
- Filtros de ADX y volumen
- Horarios de trading

### ✅ Tiempo Real
- Actualización automática cada 30 segundos
- Notificaciones de señales
- Estado de conexión MT5
- Tendencias de mercado

## 🛠️ Instalación Local

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar MT5
Asegúrate de tener MetaTrader 5 instalado y configurado con tus credenciales en `config.py`.

### 3. Ejecutar Aplicación
```bash
python web_app.py
```

### 4. Acceder al Dashboard
Abre tu navegador en: `http://localhost:5000`

## 🌐 Despliegue en Vercel

### 1. Preparar el Proyecto
```bash
# Asegúrate de tener todos los archivos:
# - web_app.py
# - vercel.json
# - requirements.txt
# - templates/dashboard.html
# - broker/, strategy/, utils/ (carpetas)
```

### 2. Instalar Vercel CLI
```bash
npm install -g vercel
```

### 3. Desplegar
```bash
vercel
```

### 4. Configurar Variables de Entorno
En el dashboard de Vercel, agrega las variables de entorno:
- `MT5_LOGIN`: Tu número de cuenta
- `MT5_PASSWORD`: Tu contraseña
- `MT5_SERVER`: Tu servidor de broker

## 📱 Uso del Dashboard

### Iniciar Bot
1. Haz clic en "Iniciar Bot"
2. El bot se conectará a MT5
3. Comenzará a analizar el mercado

### Monitorear
- **Estado**: Verde = Conectado, Rojo = Desconectado
- **Tendencias**: Alcista (verde), Bajista (rojo), Neutral (gris)
- **Señales**: Aparecen automáticamente cuando se detectan

### Configurar
1. Ve a "Configuración"
2. Modifica los parámetros
3. Guarda los cambios

## 🔧 Estructura del Proyecto

```
bot trading/
├── web_app.py              # Aplicación Flask principal
├── vercel.json             # Configuración Vercel
├── requirements.txt        # Dependencias Python
├── templates/
│   └── dashboard.html      # Dashboard principal
├── broker/
│   └── mt5_connector.py    # Conexión MT5
├── strategy/
│   └── interbank.py        # Estrategia de trading
├── utils/
│   └── time_utils.py       # Utilidades de tiempo
└── config.py              # Configuración MT5
```

## ⚠️ Consideraciones Importantes

### Seguridad
- **Nunca** subas credenciales reales a GitHub
- Usa variables de entorno para datos sensibles
- Considera usar HTTPS en producción

### Limitaciones de Vercel
- **No puede ejecutar MT5** directamente (servidor sin GUI)
- Considera usar un servidor VPS para el bot real
- Esta web es para **monitoreo y configuración**

### Alternativas de Despliegue
1. **VPS con GUI**: Para ejecutar MT5
2. **Heroku**: Para la aplicación web
3. **AWS/GCP**: Para ambos componentes

## 🎯 Próximas Mejoras

- [ ] Gráficos en tiempo real
- [ ] Historial de operaciones
- [ ] Notificaciones por email/Telegram
- [ ] Backtesting desde la web
- [ ] Múltiples estrategias
- [ ] Gestión de portafolio

## 📞 Soporte

Para problemas o mejoras:
1. Revisa los logs en la consola
2. Verifica la conexión a MT5
3. Comprueba las variables de entorno

---

**¡Tu bot de trading ahora tiene una interfaz web profesional! 🚀**
