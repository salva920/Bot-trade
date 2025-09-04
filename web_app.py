from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar el gestor de base de datos
from database import db_manager

# Importaciones condicionales para MT5
try:
    import MetaTrader5 as mt5
    from broker.mt5_connector import conectar_mt5, obtener_datos, enviar_orden
    from strategy.interbank import detectar_entrada
    from strategy.breakout_intradiario import detectar_breakout_eurusd, analizar_mercado_breakout
    from utils.time_utils import es_horario_ny
    from utils.breakout_intradiario import es_horario_optimo_breakout
    from utils.multitimeframe_analysis import analizar_multitimeframe_completo, obtener_resumen_tendencia_principal
    MT5_AVAILABLE = True
except ImportError:
    # Modo demo/web-only cuando MT5 no está disponible
    MT5_AVAILABLE = False
    db_manager.save_log('WARNING', 'MetaTrader5 no disponible - ejecutando en modo demo')

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

# Variables para el bot de breakout
last_bar_time = None
last_trade_time = 0
last_trade_side = None
COOLDOWN_SECONDS = 15 * 60  # 15 minutos entre operaciones

def log_message(level, message, data=None):
    """Función para enviar logs a MongoDB y mostrar en consola"""
    print(message)  # Mantener en consola para debugging
    if db_manager.is_connected():
        db_manager.save_log(level, message, data)

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
    """Actualiza el estado del bot usando la lógica del main.py"""
    global last_bar_time, last_trade_time, last_trade_side
    
    # Configuración del bot de breakout
    modo_horario = "ALL_HOURS"  # Todos los horarios
    
    log_message("INFO", "🚀 Iniciando bot de trading EUR/USD con ESTRATEGIA BREAKOUT INTRADIARIO")
    log_message("INFO", "🎯 CONFIGURACIÓN GANADORA: M5+M1+M1 (Más agresiva)")
    log_message("INFO", "📊 Win Rate: 84.6% | Rendimiento: 15.56% | Sharpe: 26.25")
    log_message("INFO", "⏰ Timeframes: M15 (tendencia) + M5 (confirmación) + M1 (timing)")
    log_message("INFO", "✅ Modo: Todos los horarios (24/7)")
    
    while bot_status['running']:
        try:
            if bot_status['connected'] and MT5_AVAILABLE:
                # Verificar horario según configuración seleccionada
                horario_valido = False
                
                if modo_horario == "NY_ONLY":
                    horario_valido = es_horario_ny()
                    if horario_valido:
                        log_message("INFO", "⏰ Horario NY (8:00-17:00 EST) - Verificando señales...")
                elif modo_horario == "ALL_HOURS":
                    horario_valido = True
                    log_message("INFO", "⏰ Todos los horarios - Verificando señales...")
                elif modo_horario == "NY_OPTIMAL":
                    horario_valido = es_horario_ny() and es_horario_optimo_breakout()
                    if horario_valido:
                        log_message("INFO", "⏰ Horario NY + óptimo BREAKOUT - Verificando señales...")
                
                if horario_valido:
                    # Obtener hora actual para logging
                    hora_actual = datetime.now()
                    horario_key = f"{hora_actual.hour:02d}:00"
                    
                    # Análisis multi-timeframe cada 10 minutos
                    if hora_actual.minute % 10 == 0 and hora_actual.second < 30:
                        log_message("INFO", "\n" + "="*60)
                        analisis_multitimeframe = analizar_multitimeframe_completo()
                        tendencia_principal, fuerza_principal = obtener_resumen_tendencia_principal(analisis_multitimeframe)
                        log_message("INFO", f"🎯 TENDENCIA PRINCIPAL: {tendencia_principal.upper()} ({fuerza_principal.upper()})", {
                            'tendencia_principal': tendencia_principal,
                            'fuerza_principal': fuerza_principal,
                            'analisis_multitimeframe': analisis_multitimeframe
                        })
                        log_message("INFO", "="*60)
                    
                    # Obtener datos de TODOS los timeframes para mostrar tendencias
                    df_d1 = obtener_datos(timeframe=mt5.TIMEFRAME_D1, n=100)
                    df_h4 = obtener_datos(timeframe=mt5.TIMEFRAME_H4, n=100)
                    df_h1 = obtener_datos(timeframe=mt5.TIMEFRAME_H1, n=100)
                    df_m15 = obtener_datos(timeframe=mt5.TIMEFRAME_M15, n=100)  # Tendencia intradiaria
                    df_m5 = obtener_datos(timeframe=mt5.TIMEFRAME_M5, n=100)    # Confirmación de breakout
                    df_m1 = obtener_datos(timeframe=mt5.TIMEFRAME_M1, n=100)    # Timing preciso de entrada
                    
                    if df_m5 is None or df_m5.empty:
                        log_message("ERROR", "❌ Error obteniendo datos M5")
                        time.sleep(30)
                        continue
                    
                    # Calcular tendencias para mostrar en el dashboard
                    from strategy.interbank import tendencia_ema
                    tendencies = {
                        'D1': tendencia_ema(df_d1) if df_d1 is not None and not df_d1.empty else 'neutral',
                        'H4': tendencia_ema(df_h4) if df_h4 is not None and not df_h4.empty else 'neutral',
                        'H1': tendencia_ema(df_h1) if df_h1 is not None and not df_h1.empty else 'neutral',
                        'M15': tendencia_ema(df_m15) if df_m15 is not None and not df_m15.empty else 'neutral',
                        'M5': tendencia_ema(df_m5) if df_m5 is not None and not df_m5.empty else 'neutral'
                    }
                    bot_status['tendencies'] = tendencies
                    
                    # Log de tendencias actualizadas
                    log_message("INFO", "📊 Tendencias actualizadas", {
                        'tendencies': tendencies,
                        'timeframes': ['D1', 'H4', 'H1', 'M15', 'M5']
                    })
                    
                    # Log detallado de cada timeframe
                    log_message("INFO", f"🎯 D1: {tendencies['D1']} | H4: {tendencies['H4']} | H1: {tendencies['H1']} | M15: {tendencies['M15']} | M5: {tendencies['M5']}")

                    # Detectar cambio de vela (usando M5 como referencia)
                    current_bar_time = int(df_m5.iloc[-1]['time']) if 'time' in df_m5.columns else None
                    is_new_bar = (current_bar_time is not None and current_bar_time != last_bar_time)

                    # Análisis de mercado para debugging
                    analizar_mercado_breakout(df_m15, df_m5, df_m1, debug=True)
                    
                    # Usar estrategia de BREAKOUT INTRADIARIO (versión sin validación de horario para todos los horarios)
                    from strategy.breakout_intradiario import detectar_breakout_eurusd_backtest
                    señal = detectar_breakout_eurusd_backtest(
                        df_m15=df_m15,  # Tendencia intradiaria
                        df_m5=df_m5,    # Confirmación de breakout
                        df_m1=df_m1,    # Timing preciso de entrada
                        debug=True       # Activar debug para ver el proceso
                    )
                    
                    if señal:
                        # Mostrar contexto multi-timeframe para la señal
                        try:
                            analisis_actual = analizar_multitimeframe_completo()
                            tendencia_principal, fuerza_principal = obtener_resumen_tendencia_principal(analisis_actual)
                            log_message("INFO", f"\n🎯 CONTEXTO MULTI-TIMEFRAME:")
                            log_message("INFO", f"   📊 D1: {analisis_actual.get('D1', {}).get('tendencia', 'N/A')} | H4: {analisis_actual.get('H4', {}).get('tendencia', 'N/A')} | H1: {analisis_actual.get('H1', {}).get('tendencia', 'N/A')}")
                            log_message("INFO", f"   🎯 Tendencia principal: {tendencia_principal.upper()} ({fuerza_principal.upper()})", {
                                'analisis_actual': analisis_actual,
                                'tendencia_principal': tendencia_principal,
                                'fuerza_principal': fuerza_principal
                            })
                        except:
                            log_message("WARNING", "⚠️ No se pudo obtener contexto multi-timeframe")
                        
                        # Nueva estructura de retorno: (tipo, precio, factor_riesgo, lote_optimo, nivel_breakout)
                        if len(señal) == 5:
                            tipo, precio, factor_riesgo, lote_optimo, nivel_breakout = señal
                            log_message("INFO", f"💰 Lote calculado dinámicamente: {lote_optimo}")
                            log_message("INFO", f"🛑 Nivel de breakout: {nivel_breakout:.5f}")
                        elif len(señal) == 4:
                            tipo, precio, factor_riesgo, lote_optimo = señal
                            nivel_breakout = None
                            log_message("INFO", f"💰 Lote calculado dinámicamente: {lote_optimo}")
                        else:
                            tipo, precio = señal
                            factor_riesgo = 1.0
                            lote_optimo = 0.1
                            nivel_breakout = None

                        now = int(time.time())
                        in_cooldown = (now - last_trade_time) < COOLDOWN_SECONDS

                        if not is_new_bar:
                            log_message("INFO", "🔄 Misma vela: se omite envío de orden.")
                        elif in_cooldown and last_trade_side == tipo:
                            log_message("INFO", "⏳ En cooldown para la misma dirección; no se envía orden.")
                        else:
                            log_message("INFO", f"🎯 SEÑAL BREAKOUT detectada: {tipo} a {precio}")
                            log_message("INFO", f"📊 Factor riesgo: {factor_riesgo:.2f}")
                            log_message("INFO", f"💰 Lote: {lote_optimo}")
                            if nivel_breakout:
                                log_message("INFO", f"🛑 Nivel breakout: {nivel_breakout:.5f}")
                            
                            # Enviar orden con lote optimizado
                            if enviar_orden(tipo, precio, factor_riesgo, lote_optimo):
                                log_message("INFO", "✅ Orden de BREAKOUT ejecutada exitosamente", {
                                    'tipo': tipo,
                                    'precio': precio,
                                    'factor_riesgo': factor_riesgo,
                                    'lote_optimo': lote_optimo,
                                    'nivel_breakout': nivel_breakout
                                })
                                
                                # Actualizar estado del bot
                                bot_status['last_signal'] = {
                                    'type': tipo,
                                    'price': precio,
                                    'factor_riesgo': factor_riesgo,
                                    'time': datetime.now().strftime('%H:%M:%S')
                                }
                                bot_status['total_signals'] += 1
                                
                                # Enviar señal al frontend
                                socketio.emit('new_signal', bot_status['last_signal'])
                                
                                last_trade_time = now
                                last_trade_side = tipo
                                last_bar_time = current_bar_time
                            else:
                                log_message("ERROR", "❌ Error al ejecutar la orden de BREAKOUT", {
                                    'tipo': tipo,
                                    'precio': precio,
                                    'factor_riesgo': factor_riesgo,
                                    'lote_optimo': lote_optimo
                                })
                                
                                # Aun así actualizamos la vela para no spamear durante la misma barra
                                last_bar_time = current_bar_time
                    else:
                        log_message("INFO", "🔍 Sin señal de BREAKOUT válida.")
                    
                    # Obtener balance actual
                    account_info = mt5.account_info()
                    if account_info:
                        bot_status['current_balance'] = account_info.balance
                    
                    bot_status['last_check'] = datetime.now().strftime('%H:%M:%S')
                
                # Enviar actualización al frontend
                socketio.emit('bot_update', bot_status)
            
            elif not MT5_AVAILABLE:
                # Modo demo - simular datos
                bot_status['last_check'] = datetime.now().strftime('%H:%M:%S')
                bot_status['tendencies'] = {
                    'D1': 'alcista',
                    'H4': 'alcista', 
                    'H1': 'bajista',
                    'M15': 'bajista',
                    'M5': 'bajista'
                }
                bot_status['current_balance'] = 10000.0
                
                # Log de modo demo
                log_message("INFO", "Modo demo activo - Datos simulados", {
                    'tendencies': bot_status['tendencies'],
                    'balance': bot_status['current_balance']
                })
                
                # Enviar actualización al frontend
                socketio.emit('bot_update', bot_status)
            
            time.sleep(30)  # Actualizar cada 30 segundos
            
        except Exception as e:
            log_message("ERROR", f"❌ Error en estrategia BREAKOUT: {e}", {'error': str(e)})
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
        db_manager.save_log('INFO', f'Orden {tipo} simulada (modo demo)', {'type': tipo, 'price': precio})
        return jsonify({'success': True, 'message': f'Orden {tipo} simulada (modo demo)'})
    
    if enviar_orden(tipo, precio):
        db_manager.save_log('INFO', f'Orden {tipo} enviada exitosamente', {'type': tipo, 'price': precio})
        return jsonify({'success': True, 'message': f'Orden {tipo} enviada'})
    else:
        db_manager.save_log('ERROR', f'Error enviando orden {tipo}', {'type': tipo, 'price': precio})
        return jsonify({'success': False, 'message': 'Error enviando orden'})

@app.route('/api/logs')
def api_logs():
    """Obtener logs recientes"""
    limit = request.args.get('limit', 100, type=int)
    logs = db_manager.get_recent_logs(limit)
    
    # Convertir ObjectId a string para JSON
    for log in logs:
        if '_id' in log:
            log['_id'] = str(log['_id'])
        if 'timestamp' in log:
            log['timestamp'] = log['timestamp'].isoformat()
    
    return jsonify(logs)

@app.route('/api/signals')
def api_signals():
    """Obtener señales recientes"""
    limit = request.args.get('limit', 50, type=int)
    signals = db_manager.get_recent_signals(limit)
    
    # Convertir ObjectId a string para JSON
    for signal in signals:
        if '_id' in signal:
            signal['_id'] = str(signal['_id'])
        if 'timestamp' in signal:
            signal['timestamp'] = signal['timestamp'].isoformat()
    
    return jsonify(signals)

@app.route('/api/trades')
def api_trades():
    """Obtener trades recientes"""
    limit = request.args.get('limit', 50, type=int)
    trades = db_manager.get_recent_trades(limit)
    
    # Convertir ObjectId a string para JSON
    for trade in trades:
        if '_id' in trade:
            trade['_id'] = str(trade['_id'])
        if 'timestamp' in trade:
            trade['timestamp'] = trade['timestamp'].isoformat()
    
    return jsonify(trades)

@app.route('/api/statistics')
def api_statistics():
    """Obtener estadísticas del bot"""
    stats = db_manager.get_statistics()
    return jsonify(stats)

@app.route('/logs')
def logs_page():
    """Página de logs"""
    return render_template('logs.html')

@app.route('/signals')
def signals_page():
    """Página de señales"""
    return render_template('signals.html')

@app.route('/trades')
def trades_page():
    """Página de trades"""
    return render_template('trades.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
