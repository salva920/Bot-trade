"""
Configuración de base de datos MongoDB para el bot de trading
"""
import os
from pymongo import MongoClient
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # URI de MongoDB Atlas - CONFIGURADA CON TU CONEXIÓN
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://bermudezbastidass_db_user:lpgjvpGUtIVVe9sr@cluster0.0mw6nuy.mongodb.net/bot_trading?retryWrites=true&w=majority&appName=Cluster0')
        self.database_name = os.getenv('DATABASE_NAME', 'bot_trading')
        
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            # Test de conexión
            self.client.admin.command('ping')
            logger.info("✅ Conectado a MongoDB Atlas")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self):
        """Verificar si la conexión está activa"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
        except:
            pass
        return False
    
    def save_signal(self, signal_data):
        """Guardar señal de trading"""
        if self.db is None:
            return False
        
        try:
            signal_doc = {
                'timestamp': datetime.now(),
                'type': signal_data.get('type'),
                'price': signal_data.get('price'),
                'factor_riesgo': signal_data.get('factor_riesgo', 1.0),
                'timeframe': signal_data.get('timeframe', 'M5'),
                'tendencies': signal_data.get('tendencies', {}),
                'conditions': signal_data.get('conditions', {}),
                'status': 'pending'  # pending, executed, cancelled
            }
            
            result = self.db.signals.insert_one(signal_doc)
            logger.info(f"📊 Señal guardada: {signal_data.get('type')} a {signal_data.get('price')}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error guardando señal: {e}")
            return False
    
    def save_trade(self, trade_data):
        """Guardar trade ejecutado"""
        if self.db is None:
            return False
        
        try:
            trade_doc = {
                'timestamp': datetime.now(),
                'signal_id': trade_data.get('signal_id'),
                'type': trade_data.get('type'),  # BUY/SELL
                'symbol': trade_data.get('symbol', 'EURUSD'),
                'lot': trade_data.get('lot', 0.1),
                'entry_price': trade_data.get('entry_price'),
                'sl_price': trade_data.get('sl_price'),
                'tp_price': trade_data.get('tp_price'),
                'status': trade_data.get('status', 'open'),  # open, closed, cancelled
                'profit_loss': trade_data.get('profit_loss', 0),
                'mt5_ticket': trade_data.get('mt5_ticket')
            }
            
            result = self.db.trades.insert_one(trade_doc)
            logger.info(f"💰 Trade guardado: {trade_data.get('type')} {trade_data.get('symbol')}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error guardando trade: {e}")
            return False
    
    def save_log(self, level, message, data=None):
        """Guardar log en base de datos"""
        if self.db is None:
            return False
        
        try:
            log_doc = {
                'timestamp': datetime.now(),
                'level': level,  # INFO, WARNING, ERROR, DEBUG
                'message': message,
                'data': data or {},
                'source': 'bot_trading'
            }
            
            result = self.db.logs.insert_one(log_doc)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error guardando log: {e}")
            return False
    
    def get_recent_signals(self, limit=50):
        """Obtener señales recientes"""
        if self.db is None:
            return []
        
        try:
            signals = list(self.db.signals.find().sort('timestamp', -1).limit(limit))
            return signals
        except Exception as e:
            logger.error(f"Error obteniendo señales: {e}")
            return []
    
    def get_recent_trades(self, limit=50):
        """Obtener trades recientes"""
        if self.db is None:
            return []
        
        try:
            trades = list(self.db.trades.find().sort('timestamp', -1).limit(limit))
            return trades
        except Exception as e:
            logger.error(f"Error obteniendo trades: {e}")
            return []
    
    def get_recent_logs(self, limit=100):
        """Obtener logs recientes"""
        if self.db is None:
            return []
        
        try:
            logs = list(self.db.logs.find().sort('timestamp', -1).limit(limit))
            return logs
        except Exception as e:
            logger.error(f"Error obteniendo logs: {e}")
            return []
    
    def get_statistics(self):
        """Obtener estadísticas del bot"""
        if self.db is None:
            return {}
        
        try:
            stats = {
                'total_signals': self.db.signals.count_documents({}),
                'total_trades': self.db.trades.count_documents({}),
                'successful_trades': self.db.trades.count_documents({'status': 'closed', 'profit_loss': {'$gt': 0}}),
                'failed_trades': self.db.trades.count_documents({'status': 'closed', 'profit_loss': {'$lte': 0}}),
                'open_trades': self.db.trades.count_documents({'status': 'open'}),
                'total_profit': sum(trade.get('profit_loss', 0) for trade in self.db.trades.find({'status': 'closed'}))
            }
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()

# Instancia global de la base de datos
db_manager = DatabaseManager()
