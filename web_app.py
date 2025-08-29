from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
import pandas as pd

# Importaciones condicionales para MT5
try:
    import MetaTrader5 as mt5
    from broker.mt5_connector import conectar_mt5, obtener_datos, enviar_orden
    from strategy.interbank import detectar_entrada
    from utils.time_utils import es_horario_ny
    MT5_AVAILABLE = True
except ImportError:
    # Modo demo/web-only cuando MT5 no está disponible
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 no disponible - ejecutando en modo demo")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales para el estado del bot
bot_status = {
    'running': False,
    'connected': False,
    'last_signal': None,
    'last_check': None,
    'total_signals': 0,
    'successful_trades': 0,
    'failed_trades': 0,
    'current_balance': 0,
    'tendencies': {},
    'conditions': {}
}

# Configuración del bot
bot_config = {
    'MT5_LOGIN': 10006727030,
    'MT5_PASSWORD': 'X*J7QuIk',
    'MT5_INVESTOR': '*5NaLiNo',
    'MT5_SERVER': 'MetaQuotes-Demo',
    'SYMBOL': 'EURUSD',
    'LOT': 0.1,
    'RISK_REWARD': 2,
    'SL_PIPS': 20,
    'TP_PIPS': 40,
    'NY_START': (8, 0),
    'NY_END': (17, 0),
    'ADX_MIN': 25,
    'VOLUME_MIN': 1.2,
    'RSI_MIN': 30,
    'RSI_MAX': 70,
    'ATR_MIN': 0.001
}

def update_bot_status():
    """Actualiza el estado del bot y envía datos al frontend"""
    while bot_status['running']:
        try:
            if bot_status['connected'] and MT5_AVAILABLE:
                # Obtener datos de mercado
                df_m5 = obtener_datos(timeframe=mt5.TIMEFRAME_M5, n=100)
                df_m15 = obtener_datos(timeframe=mt5.TIMEFRAME_M15, n=100)
                df_h1 = obtener_datos(timeframe=mt5.TIMEFRAME_H1, n=100)
                df_h4 = obtener_datos(timeframe=mt5.TIMEFRAME_H4, n=100)
                df_d1 = obtener_datos(timeframe=mt5.TIMEFRAME_D1, n=100)
                
                if df_m5 is not None and not df_m5.empty:
                    # Analizar tendencias
                    from strategy.interbank import tendencia_ema
                    bot_status['tendencies'] = {
                        'D1': tendencia_ema(df_d1),
                        'H4': tendencia_ema(df_h4),
                        'H1': tendencia_ema(df_h1),
                        'M15': tendencia_ema(df_m15),
                        'M5': tendencia_ema(df_m5)
                    }
                    
                    # Detectar señal
                    señal = detectar_entrada(
                        df=df_m5,
                        df_m5=df_m5,
                        df_m15=df_m15,
                        df_h1=df_h1,
                        df_h4=df_h4,
                        df_d1=df_d1,
                        debug=False
                    )
                    
                    bot_status['last_check'] = datetime.now().strftime('%H:%M:%S')
                    
                    if señal:
                        bot_status['last_signal'] = {
                            'type': señal[0],
                            'price': señal[1],
                            'factor_riesgo': señal[2] if len(señal) > 2 else 1.0,
                            'time': datetime.now().strftime('%H:%M:%S')
                        }
                        bot_status['total_signals'] += 1
                        
                        # Enviar señal al frontend
                        socketio.emit('new_signal', bot_status['last_signal'])
                    
                    # Obtener balance actual
                    account_info = mt5.account_info()
                    if account_info:
                        bot_status['current_balance'] = account_info.balance
                
                # Enviar actualización al frontend
                socketio.emit('bot_update', bot_status)
            
            elif not MT5_AVAILABLE:
                # Modo demo - simular datos
                bot_status['last_check'] = datetime.now().strftime('%H:%M:%S')
                bot_status['tendencies'] = {
                    'D1': 'BULLISH',
                    'H4': 'BULLISH', 
                    'H1': 'NEUTRAL',
                    'M15': 'BULLISH',
                    'M5': 'NEUTRAL'
                }
                bot_status['current_balance'] = 10000.0
                
                # Enviar actualización al frontend
                socketio.emit('bot_update', bot_status)
            
            time.sleep(30)  # Actualizar cada 30 segundos
            
        except Exception as e:
            print(f"Error en actualización: {e}")
            time.sleep(60)

@app.route('/')
def dashboard():
    """Página principal del dashboard"""
    return render_template('dashboard.html', config=bot_config, status=bot_status)

@app.route('/config')
def config_page():
    """Página de configuración"""
    return render_template('config.html', config=bot_config)

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API para obtener/actualizar configuración"""
    
    if request.method == 'POST':
        data = request.json
        bot_config.update(data)
        return jsonify({'success': True, 'config': bot_config})
    
    return jsonify(bot_config)

@app.route('/api/update_config', methods=['POST'])
def update_config():
    """API para actualizar configuración desde el formulario"""
    
    try:
        data = request.json
        
        # Actualizar configuración MT5
        if 'mt5_login' in data:
            bot_config['MT5_LOGIN'] = int(data['mt5_login'])
        if 'mt5_password' in data:
            bot_config['MT5_PASSWORD'] = data['mt5_password']
        if 'mt5_investor' in data:
            bot_config['MT5_INVESTOR'] = data['mt5_investor']
        if 'mt5_server' in data:
            bot_config['MT5_SERVER'] = data['mt5_server']
        
        # Actualizar configuración de trading
        if 'symbol' in data:
            bot_config['SYMBOL'] = data['symbol']
        if 'lot' in data:
            bot_config['LOT'] = float(data['lot'])
        if 'risk_reward' in data:
            bot_config['RISK_REWARD'] = float(data['risk_reward'])
        if 'sl_pips' in data:
            bot_config['SL_PIPS'] = int(data['sl_pips'])
        if 'tp_pips' in data:
            bot_config['TP_PIPS'] = int(data['tp_pips'])
        
        # Actualizar filtros
        if 'adx_min' in data:
            bot_config['ADX_MIN'] = int(data['adx_min'])
        if 'volume_min' in data:
            bot_config['VOLUME_MIN'] = float(data['volume_min'])
        if 'rsi_min' in data:
            bot_config['RSI_MIN'] = int(data['rsi_min'])
        if 'rsi_max' in data:
            bot_config['RSI_MAX'] = int(data['rsi_max'])
        if 'atr_min' in data:
            bot_config['ATR_MIN'] = float(data['atr_min'])
        
        # Actualizar horarios
        if 'ny_start' in data:
            bot_config['NY_START'] = tuple(data['ny_start'])
        if 'ny_end' in data:
            bot_config['NY_END'] = tuple(data['ny_end'])
        
        return jsonify({'success': True, 'message': 'Configuración actualizada correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    """Iniciar el bot"""
    
    if not bot_status['running']:
        if MT5_AVAILABLE and conectar_mt5():
            bot_status['connected'] = True
            bot_status['running'] = True
            
            # Iniciar thread de actualización
            update_thread = threading.Thread(target=update_bot_status, daemon=True)
            update_thread.start()
            
            return jsonify({'success': True, 'message': 'Bot iniciado correctamente'})
        elif not MT5_AVAILABLE:
            # Modo demo
            bot_status['connected'] = True
            bot_status['running'] = True
            
            # Iniciar thread de actualización
            update_thread = threading.Thread(target=update_bot_status, daemon=True)
            update_thread.start()
            
            return jsonify({'success': True, 'message': 'Bot iniciado en modo demo'})
        else:
            return jsonify({'success': False, 'message': 'Error conectando a MT5'})
    
    return jsonify({'success': False, 'message': 'Bot ya está ejecutándose'})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    """Detener el bot"""
    
    bot_status['running'] = False
    bot_status['connected'] = False
    
    if MT5_AVAILABLE and mt5.initialize():
        mt5.shutdown()
    
    return jsonify({'success': True, 'message': 'Bot detenido'})

@app.route('/api/status')
def api_status():
    """Obtener estado actual del bot"""
    return jsonify(bot_status)

@app.route('/api/send_order', methods=['POST'])
def send_order():
    """Enviar orden manual"""
    data = request.json
    tipo = data.get('type')
    precio = data.get('price')
    
    if not MT5_AVAILABLE:
        return jsonify({'success': True, 'message': f'Orden {tipo} simulada (modo demo)'})
    
    if enviar_orden(tipo, precio):
        return jsonify({'success': True, 'message': f'Orden {tipo} enviada'})
    else:
        return jsonify({'success': False, 'message': 'Error enviando orden'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
