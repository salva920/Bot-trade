"""
Aplicación web simplificada para Vercel (sin MetaTrader5)
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vercel_demo_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales para el estado del bot (modo demo)
bot_status = {
    'running': False,
    'connected': False,
    'last_signal': None,
    'last_check': None,
    'total_signals': 0,
    'successful_trades': 0,
    'failed_trades': 0,
    'current_balance': 10000.0,
    'tendencies': {},
    'conditions': {}
}

# Configuración del bot (modo demo)
bot_config = {
    'MT5_LOGIN': 10006727030,
    'MT5_PASSWORD': 'DEMO',
    'MT5_INVESTOR': 'DEMO',
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
    """Actualiza el estado del bot en modo demo"""
    while bot_status['running']:
        try:
            # Simular datos de mercado
            bot_status['last_check'] = datetime.now().strftime('%H:%M:%S')
            bot_status['tendencies'] = {
                'D1': 'BULLISH',
                'H4': 'BULLISH', 
                'H1': 'NEUTRAL',
                'M15': 'BULLISH',
                'M5': 'NEUTRAL'
            }
            
            # Simular señales ocasionales
            if time.time() % 300 < 30:  # Cada 5 minutos aproximadamente
                bot_status['last_signal'] = {
                    'type': 'BUY' if time.time() % 600 < 300 else 'SELL',
                    'price': 1.0850 + (time.time() % 100) / 10000,
                    'factor_riesgo': 1.0,
                    'time': datetime.now().strftime('%H:%M:%S')
                }
                bot_status['total_signals'] += 1
                
                # Enviar señal al frontend
                socketio.emit('new_signal', bot_status['last_signal'])
            
            # Enviar actualización al frontend
            socketio.emit('bot_update', bot_status)
            
            time.sleep(30)  # Actualizar cada 30 segundos
            
        except Exception as e:
            print(f"Error en actualización demo: {e}")
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
    """Iniciar el bot en modo demo"""
    
    if not bot_status['running']:
        bot_status['connected'] = True
        bot_status['running'] = True
        
        # Iniciar thread de actualización
        update_thread = threading.Thread(target=update_bot_status, daemon=True)
        update_thread.start()
        
        return jsonify({'success': True, 'message': 'Bot iniciado en modo demo'})
    
    return jsonify({'success': False, 'message': 'Bot ya está ejecutándose'})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    """Detener el bot"""
    
    bot_status['running'] = False
    bot_status['connected'] = False
    
    return jsonify({'success': True, 'message': 'Bot detenido'})

@app.route('/api/status')
def api_status():
    """Obtener estado actual del bot"""
    return jsonify(bot_status)

@app.route('/api/send_order', methods=['POST'])
def send_order():
    """Simular envío de orden en modo demo"""
    data = request.json
    tipo = data.get('type')
    precio = data.get('price')
    
    return jsonify({'success': True, 'message': f'Orden {tipo} simulada (modo demo)'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
