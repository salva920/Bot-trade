# 🤖 Bot Trading Pro - Confluencia de 4 Timeframes

## 📋 Descripción

Bot de trading automatizado para MetaTrader 5 que utiliza una estrategia avanzada de **confluencia de 4 timeframes** para identificar oportunidades de trading de alta probabilidad. Incluye una aplicación web completa para monitoreo y configuración en tiempo real.

## 🚀 Características Principales

### ✅ Estrategia Avanzada
- **Confluencia de 4 Timeframes**: D1, H4, M15, M5
- **Indicadores Técnicos**: EMA, ADX, RSI, ATR, Volumen, Pendiente
- **Filtros Dinámicos**: Adaptación automática según condiciones de mercado
- **Gestión de Riesgo**: Factor de riesgo dinámico y stop loss automático

### ✅ Aplicación Web
- **Dashboard en Tiempo Real**: Socket.IO para actualizaciones instantáneas
- **Configuración Dinámica**: Ajuste de parámetros desde la web
- **Monitoreo Completo**: Estado del bot, tendencias, señales y estadísticas
- **Interfaz Moderna**: Diseño responsive con Bootstrap

### ✅ Integración MT5
- **Conexión Automática**: Login y gestión de sesiones
- **Ejecución de Órdenes**: Compra/venta automática
- **Gestión de Posiciones**: Control de posiciones abiertas
- **Datos en Tiempo Real**: Obtención de datos de múltiples timeframes

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, Flask, Socket.IO
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Trading**: MetaTrader 5 API
- **Análisis**: Pandas, NumPy, SciPy
- **Despliegue**: Vercel (web), VPS (bot)

## 📁 Estructura del Proyecto

```
bot trading/
├── web_app.py              # Aplicación Flask principal
├── main.py                 # Script principal del bot
├── config.py              # Configuración MT5
├── requirements.txt       # Dependencias Python
├── vercel.json           # Configuración Vercel
├── .gitignore            # Archivos a ignorar
├── README.md             # Este archivo
├── README_WEB.md         # Documentación web
├── templates/
│   ├── dashboard.html    # Dashboard principal
│   └── config.html       # Página de configuración
├── broker/
│   └── mt5_connector.py  # Conexión y órdenes MT5
├── strategy/
│   └── interbank.py      # Estrategia de trading
└── utils/
    └── time_utils.py     # Utilidades de tiempo
```

## 🚀 Instalación Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/bot-trading-pro.git
cd bot-trading-pro
```

### 2. Crear Entorno Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar MetaTrader 5
- Instalar MetaTrader 5
- Configurar credenciales en `config.py`:
```python
MT5_LOGIN = tu_login
MT5_PASSWORD = "tu_password"
MT5_INVESTOR = "tu_investor"
MT5_SERVER = "tu_servidor"
```

### 5. Ejecutar la Aplicación
```bash
# Para el bot principal
python main.py

# Para la aplicación web
python web_app.py
```

### 6. Acceder al Dashboard
Abre tu navegador en: `http://localhost:5000`

## 🌐 Despliegue en Vercel

### 1. Preparar el Proyecto
```bash
# Asegúrate de tener todos los archivos necesarios
git add .
git commit -m "Preparar para despliegue"
git push origin main
```

### 2. Conectar con Vercel
```bash
npm install -g vercel
vercel login
vercel
```

### 3. Configurar Variables de Entorno
En el dashboard de Vercel, agrega:
- `MT5_LOGIN`: Tu número de cuenta
- `MT5_PASSWORD`: Tu contraseña
- `MT5_SERVER`: Tu servidor de broker

## 📊 Estrategia de Trading

### Concepto Principal
El bot utiliza una estrategia de **confluencia de 4 timeframes** para identificar oportunidades de alta probabilidad:

- **D1 (Diario)**: Tendencia principal del mercado
- **H4 (4 Horas)**: Confirmación de tendencia intermedia
- **M15 (15 Minutos)**: Confirmación de entrada
- **M5 (5 Minutos)**: Timing preciso de ejecución

### Indicadores Utilizados
- **EMA (20, 50)**: Tendencias de corto y largo plazo
- **ADX (14)**: Fuerza de la tendencia
- **RSI (14)**: Condiciones de sobrecompra/sobreventa
- **ATR (20)**: Volatilidad del mercado
- **Volumen**: Confirmación de movimientos
- **Pendiente**: Dirección del momentum

### Filtros de Entrada
- **ADX > 25**: Mercado en tendencia clara
- **Volumen > 1.2x**: Confirmación de participación real
- **RSI (30-70)**: Rebotes desde niveles extremos
- **Confluencia 4TF**: Alineación de todos los timeframes

## ⚠️ Consideraciones Importantes

### Seguridad
- **Nunca** subas credenciales reales a GitHub
- Usa variables de entorno para datos sensibles
- Considera usar HTTPS en producción

### Limitaciones de Vercel
- **No puede ejecutar MT5** directamente (servidor sin GUI)
- Considera usar un servidor VPS para el bot real
- Esta web es para **monitoreo y configuración**

### Gestión de Riesgo
- El bot incluye stop loss automático
- Factor de riesgo dinámico según volatilidad
- Cooldown de 15 minutos entre operaciones
- Una orden por vela para evitar spam

## 🎯 Próximas Mejoras

- [ ] Gráficos en tiempo real con TradingView
- [ ] Historial de operaciones detallado
- [ ] Notificaciones por email/Telegram
- [ ] Backtesting desde la web
- [ ] Múltiples estrategias configurables
- [ ] Gestión de portafolio avanzada
- [ ] Análisis de correlación entre pares

## 📞 Soporte

Para problemas o mejoras:
1. Revisa los logs en la consola
2. Verifica la conexión a MT5
3. Comprueba las variables de entorno
4. Abre un issue en GitHub

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

**ADVERTENCIA**: Este software es solo para fines educativos. El trading de forex conlleva riesgos significativos y puede resultar en pérdidas. No garantizamos ganancias y recomendamos probar en cuenta demo antes de usar dinero real.

---

**¡Disfruta usando tu bot de trading profesional! 🚀** # Bot-trade
