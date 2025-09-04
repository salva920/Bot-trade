"""
Configuración de MongoDB para el bot de trading
Copia este archivo como .env y configura tu URI de MongoDB Atlas
"""

# MongoDB Atlas Configuration
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/bot_trading?retryWrites=true&w=majority"
DATABASE_NAME = "bot_trading"

# Instrucciones para configurar MongoDB Atlas:
# 1. Ve a https://cloud.mongodb.com/
# 2. Crea una cuenta gratuita
# 3. Crea un nuevo cluster
# 4. Ve a "Database Access" y crea un usuario
# 5. Ve a "Network Access" y agrega tu IP (0.0.0.0/0 para permitir todas)
# 6. Ve a "Clusters" y haz clic en "Connect"
# 7. Selecciona "Connect your application"
# 8. Copia la URI y reemplaza <username> y <password> con tus credenciales
# 9. Actualiza la variable MONGODB_URI en este archivo

# Ejemplo de URI:
# MONGODB_URI = "mongodb+srv://mi_usuario:mi_password@cluster0.abc123.mongodb.net/bot_trading?retryWrites=true&w=majority"
