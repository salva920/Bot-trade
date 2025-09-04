# 🤖 Bot Trading Pro - Configuración MongoDB

## 📊 Sistema de Base de Datos

El bot ahora utiliza **MongoDB Atlas** para almacenar todos los datos en lugar de generar logs en consola. Esto proporciona:

- ✅ **Almacenamiento persistente** de señales, trades y logs
- ✅ **Interfaz web completa** para monitorear el bot
- ✅ **Historial completo** de todas las operaciones
- ✅ **Estadísticas en tiempo real** del rendimiento
- ✅ **Sin consumo de disco duro** por logs de consola

## 🚀 Configuración de MongoDB Atlas

### 1. Crear Cuenta en MongoDB Atlas

1. Ve a [https://cloud.mongodb.com/](https://cloud.mongodb.com/)
2. Crea una cuenta gratuita
3. Selecciona el plan **M0 Sandbox** (gratuito)

### 2. Crear Cluster

1. Haz clic en **"Build a Database"**
2. Selecciona **"M0 Sandbox"** (gratuito)
3. Elige una región cercana a tu ubicación
4. Nombra tu cluster (ej: "bot-trading-cluster")
5. Haz clic en **"Create"**

### 3. Configurar Acceso a la Base de Datos

1. Ve a **"Database Access"** en el menú lateral
2. Haz clic en **"Add New Database User"**
3. Crea un usuario con:
   - **Username**: `bot_trading_user`
   - **Password**: Genera una contraseña segura
   - **Database User Privileges**: `Read and write to any database`
4. Haz clic en **"Add User"**

### 4. Configurar Acceso de Red

1. Ve a **"Network Access"** en el menú lateral
2. Haz clic en **"Add IP Address"**
3. Selecciona **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Haz clic en **"Confirm"**

### 5. Obtener URI de Conexión

1. Ve a **"Clusters"** en el menú lateral
2. Haz clic en **"Connect"** en tu cluster
3. Selecciona **"Connect your application"**
4. Copia la URI de conexión

### 6. Configurar el Bot

1. Crea un archivo `.env` en la raíz del proyecto:
```bash
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://bot_trading_user:TU_PASSWORD@cluster0.abc123.mongodb.net/bot_trading?retryWrites=true&w=majority
DATABASE_NAME=bot_trading
```

2. Reemplaza `TU_PASSWORD` con la contraseña que creaste
3. Reemplaza `cluster0.abc123.mongodb.net` con tu URI real

## 📱 Nuevas Funcionalidades Web

### Dashboard Principal (`/`)
- Estado del bot en tiempo real
- Tendencias de mercado
- Última señal detectada
- Balance actual

### Logs (`/logs`)
- Historial completo de logs del sistema
- Filtros por nivel (INFO, WARNING, ERROR)
- Actualización automática cada 30 segundos
- Sin consumo de disco duro

### Señales (`/signals`)
- Todas las señales detectadas por el bot
- Filtros por tipo (BUY/SELL)
- Detalles de tendencias por timeframe
- Estado de cada señal

### Trades (`/trades`)
- Historial de operaciones ejecutadas
- Estadísticas de rendimiento
- Filtros por estado (abierto/cerrado/cancelado)
- Cálculo de P&L en tiempo real

## 🔧 Instalación y Uso

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Copia el archivo de ejemplo
cp mongodb_config.py .env

# Edita .env con tu configuración de MongoDB
```

### 3. Ejecutar la Aplicación Web
```bash
python web_app.py
```

### 4. Acceder al Dashboard
Abre tu navegador en: `http://localhost:5000`

## 📊 Estructura de la Base de Datos

### Colección: `signals`
```json
{
  "_id": "ObjectId",
  "timestamp": "2024-01-01T12:00:00Z",
  "type": "BUY|SELL",
  "price": 1.2345,
  "factor_riesgo": 1.0,
  "timeframe": "M5",
  "tendencies": {
    "D1": "BULLISH",
    "H4": "BULLISH",
    "H1": "NEUTRAL",
    "M15": "BULLISH",
    "M5": "NEUTRAL"
  },
  "status": "pending|executed|cancelled"
}
```

### Colección: `trades`
```json
{
  "_id": "ObjectId",
  "timestamp": "2024-01-01T12:00:00Z",
  "signal_id": "ObjectId",
  "type": "BUY|SELL",
  "symbol": "EURUSD",
  "lot": 0.1,
  "entry_price": 1.2345,
  "sl_price": 1.2325,
  "tp_price": 1.2385,
  "status": "open|closed|cancelled",
  "profit_loss": 0.0,
  "mt5_ticket": 123456
}
```

### Colección: `logs`
```json
{
  "_id": "ObjectId",
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO|WARNING|ERROR|DEBUG",
  "message": "Mensaje del log",
  "data": {},
  "source": "bot_trading"
}
```

## 🎯 Beneficios

- **Sin logs en consola**: Todo se almacena en la base de datos
- **Interfaz web completa**: Monitoreo desde cualquier dispositivo
- **Historial persistente**: No se pierden datos al reiniciar
- **Escalabilidad**: MongoDB Atlas maneja el crecimiento de datos
- **Acceso remoto**: Monitorea tu bot desde cualquier lugar
- **Análisis avanzado**: Estadísticas detalladas de rendimiento

## 🔒 Seguridad

- Usa contraseñas seguras para MongoDB
- Limita el acceso de red si es necesario
- Las credenciales se almacenan en variables de entorno
- MongoDB Atlas incluye encriptación en tránsito y en reposo

## 📞 Soporte

Si tienes problemas con la configuración:

1. Verifica que tu URI de MongoDB sea correcta
2. Asegúrate de que tu IP esté en la lista blanca
3. Confirma que el usuario tenga permisos de lectura/escritura
4. Revisa los logs de la aplicación web en `/logs`

¡Disfruta de tu bot de trading con base de datos! 🚀
