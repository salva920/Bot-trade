from broker.mt5_connector import conectar_mt5, obtener_datos, enviar_orden
from strategy.breakout_intradiario import detectar_breakout_eurusd, analizar_mercado_breakout
from utils.time_utils import es_horario_ny
from utils.breakout_intradiario import es_horario_optimo_breakout
from utils.multitimeframe_analysis import analizar_multitimeframe_completo, obtener_resumen_tendencia_principal
from database import db_manager
import MetaTrader5 as mt5
import time
import datetime


def log_message(level, message, data=None):
    """Función para enviar logs a MongoDB y mostrar en consola"""
    print(message)  # Mantener en consola para debugging
    if db_manager.is_connected():
        db_manager.save_log(level, message, data)

def main():
    log_message("INFO", "🚀 Iniciando bot de trading EUR/USD con ESTRATEGIA BREAKOUT INTRADIARIO")
    log_message("INFO", "🎯 CONFIGURACIÓN GANADORA: M5+M1+M1 (Más agresiva)")
    log_message("INFO", "📊 Win Rate: 84.6% | Rendimiento: 15.56% | Sharpe: 26.25")
    log_message("INFO", "⏰ Timeframes: M15 (tendencia) + M5 (confirmación) + M1 (timing)")
    
    # Configuración de horario - PRUEBA TODOS LOS HORARIOS
    log_message("INFO", "\n🎯 CONFIGURACIÓN SELECCIONADA:")
    log_message("INFO", "🚀 TODOS LOS HORARIOS - PRUEBA COMPLETA")
    log_message("INFO", "📊 Objetivo: Analizar rendimiento en diferentes horarios")
    log_message("INFO", "⏰ Duración recomendada: 1-2 semanas")
    log_message("INFO", "📈 Configuración ganadora: Win Rate 84.6% | Rendimiento 15.56%")
    
    modo_horario = "ALL_HOURS"  # Forzar todos los horarios para la prueba
    log_message("INFO", "✅ Modo: Todos los horarios (24/7)")
    
    if not conectar_mt5():
        log_message("ERROR", "❌ Error conectando a MT5")
        return
        
    log_message("INFO", "✅ Conectado a MetaTrader 5")

    last_bar_time = None
    last_trade_time = 0
    last_trade_side = None
    COOLDOWN_SECONDS = 15 * 60  # 15 minutos entre operaciones
    
    # Sistema de logging para análisis por horarios
    from collections import defaultdict
    
    # Estadísticas por horario
    stats_por_horario = defaultdict(lambda: {
        'señales': 0,
        'operaciones': 0,
        'ganancias': 0,
        'pérdidas': 0,
        'balance': 0
    })
    
    log_message("INFO", "\n📊 SISTEMA DE LOGGING ACTIVADO")
    log_message("INFO", "📈 Se registrarán estadísticas por horario")
    log_message("INFO", "📝 Archivo: trading_log.txt")
    
    while True:
        try:
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
                
                # Obtener hora actual para logging (mover antes de usar)
                hora_actual = datetime.datetime.now()
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
                
                # Obtener datos SOLO de timeframes intradiarios
                df_m15 = obtener_datos(timeframe=mt5.TIMEFRAME_M15, n=100)  # Tendencia intradiaria
                df_m5 = obtener_datos(timeframe=mt5.TIMEFRAME_M5, n=100)    # Confirmación de breakout
                df_m1 = obtener_datos(timeframe=mt5.TIMEFRAME_M1, n=100)    # Timing preciso de entrada
                
                if df_m5 is None or df_m5.empty:
                    log_message("ERROR", "❌ Error obteniendo datos M5")
                    time.sleep(30)
                    continue

                # Detectar cambio de vela (usando M5 como referencia)
                current_bar_time = int(df_m5.iloc[-1]['time']) if 'time' in df_m5.columns else None
                is_new_bar = (current_bar_time is not None and current_bar_time != last_bar_time)

                # Análisis de mercado para debugging
                analizar_mercado_breakout(df_m15, df_m5, df_m1, debug=True)
                
                # Usar estrategia de BREAKOUT INTRADIARIO (versión sin validación de horario para todos los horarios)
                if modo_horario == "ALL_HOURS":
                    # Importar función de backtest que no valida horarios
                    from strategy.breakout_intradiario import detectar_breakout_eurusd_backtest
                    señal = detectar_breakout_eurusd_backtest(
                        df_m15=df_m15,  # Tendencia intradiaria
                        df_m5=df_m5,    # Confirmación de breakout
                        df_m1=df_m1,    # Timing preciso de entrada
                        debug=True       # Activar debug para ver el proceso
                    )
                else:
                    # Usar función normal con validación de horario
                    señal = detectar_breakout_eurusd(
                        df_m15=df_m15,  # Tendencia intradiaria
                        df_m5=df_m5,    # Confirmación de breakout
                        df_m1=df_m1,    # Timing preciso de entrada
                        debug=True       # Activar debug para ver el proceso
                    )
                
                # Registrar señal detectada
                if señal:
                    stats_por_horario[horario_key]['señales'] += 1
                
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
                            
                            # Registrar operación exitosa
                            stats_por_horario[horario_key]['operaciones'] += 1
                            
                            # Logging detallado
                            with open('trading_log.txt', 'a', encoding='utf-8') as f:
                                f.write(f"{hora_actual.strftime('%Y-%m-%d %H:%M:%S')} | {horario_key} | {tipo} | {precio} | {lote_optimo} | EJECUTADA\n")
                            
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
                            
                            # Logging de error
                            with open('trading_log.txt', 'a', encoding='utf-8') as f:
                                f.write(f"{hora_actual.strftime('%Y-%m-%d %H:%M:%S')} | {horario_key} | {tipo} | {precio} | {lote_optimo} | ERROR\n")
                            
                            # Aun así actualizamos la vela para no spamear durante la misma barra
                            last_bar_time = current_bar_time
                else:
                    log_message("INFO", "🔍 Sin señal de BREAKOUT válida.")
            else:
                if modo_horario == "NY_ONLY":
                    log_message("INFO", "🌙 Fuera del horario de trading de NY (8:00-17:00 EST)")
                elif modo_horario == "NY_OPTIMAL":
                    if es_horario_ny():
                        log_message("INFO", "⏰ Horario NY pero no óptimo para BREAKOUT EUR/USD")
                    else:
                        log_message("INFO", "🌙 Fuera del horario de trading de NY")
                else:
                    log_message("INFO", "⏰ Esperando siguiente verificación...")
            
            # Reporte periódico de estadísticas por horario (cada 10 minutos)
            if hora_actual.minute % 10 == 0 and hora_actual.second < 30:
                log_message("INFO", "\n📊 REPORTE DE ESTADÍSTICAS POR HORARIO:")
                log_message("INFO", "=" * 50)
                for horario, stats in sorted(stats_por_horario.items()):
                    if stats['señales'] > 0:
                        win_rate = (stats['ganancias'] / stats['operaciones'] * 100) if stats['operaciones'] > 0 else 0
                        log_message("INFO", f"🕐 {horario}: {stats['señales']} señales, {stats['operaciones']} operaciones, Win Rate: {win_rate:.1f}%", {
                            'horario': horario,
                            'señales': stats['señales'],
                            'operaciones': stats['operaciones'],
                            'win_rate': win_rate
                        })
                log_message("INFO", "=" * 50)
                
            # Esperar 30s para respuesta más ágil intradía
            time.sleep(30)
            
        except Exception as e:
            log_message("ERROR", f"❌ Error en estrategia BREAKOUT: {e}", {'error': str(e)})
            time.sleep(60)

if __name__ == "__main__":
    main() 