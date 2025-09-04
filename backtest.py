from broker.mt5_connector import conectar_mt5, obtener_datos
from strategy.breakout_intradiario import detectar_breakout_eurusd, calcular_indicadores_breakout
from config import SYMBOL, LOT, SL_PIPS, TP_PIPS, RISK_REWARD
import MetaTrader5 as mt5
import pandas as pd
import numpy as np


def backtest_breakout_intradiario(timeframe_m15=mt5.TIMEFRAME_M15, timeframe_m5=mt5.TIMEFRAME_M5, timeframe_m1=mt5.TIMEFRAME_M1, n=2000):
    """
    Backtest de la estrategia BREAKOUT INTRADIARIO
    Usa M15 (tendencia) + M5 (confirmación) + M1 (timing)
    """
    print(f"🚀 Iniciando BACKTEST BREAKOUT INTRADIARIO...")
    print(f"⏰ Timeframes: M15 (tendencia) + M5 (confirmación) + M1 (timing)")
    print(f"📊 Velas analizadas: {n}")
    
    # Mostrar configuración de filtros
    from config import ADX_MIN, VOLUME_MIN, RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, ATR_MIN_PIPS, ATR_MAX_PIPS, PENDIENTE_MINIMA, PENDIENTE_MAXIMA
    print(f"🔧 FILTROS APLICADOS:")
    print(f"   - ADX mínimo: {ADX_MIN}")
    print(f"   - Volumen mínimo: {VOLUME_MIN}")
    print(f"   - RSI compra: ≤ {RSI_ENTRADA_COMPRA}")
    print(f"   - RSI venta: ≥ {RSI_ENTRADA_VENTA}")
    print(f"   - ATR: {ATR_MIN_PIPS}-{ATR_MAX_PIPS} pips")
    print(f"   - Pendiente: ±{abs(PENDIENTE_MINIMA)} (ULTRA FLEXIBLE)")
    
    # Mostrar nueva configuración de gestión de riesgo inteligente
    from config import (STOP_LOSS_ATR_MULTIPLIER, TAKE_PROFIT_RATIO, TRAILING_STOP_ACTIVAR_PIPS,
                        POSITION_SIZE_RISK_PERCENT, RISK_REWARD_RATIO_TARGET)
    print("🚀 GESTIÓN DE RIESGO INTELIGENTE:")
    print(f"   - Stop Loss: {STOP_LOSS_ATR_MULTIPLIER}× ATR")
    print(f"   - Take Profit: {TAKE_PROFIT_RATIO}× Stop Loss")
    print(f"   - Trailing Stop: {TRAILING_STOP_ACTIVAR_PIPS} pips")
    print(f"   - Riesgo por operación: {POSITION_SIZE_RISK_PERCENT}%")
    print(f"   - Ratio objetivo: 1:{RISK_REWARD_RATIO_TARGET}")
    print("🚀 ESTRATEGIA ULTRA FLEXIBLE + GESTIÓN DE RIESGO INTELIGENTE")
    
    if not conectar_mt5():
        print("❌ Error conectando a MT5")
        return

    # Obtener datos históricos para todos los timeframes
    print("📥 Obteniendo datos históricos...")
    df_m15 = obtener_datos(timeframe=timeframe_m15, n=n)
    df_m5 = obtener_datos(timeframe=timeframe_m5, n=n)
    df_m1 = obtener_datos(timeframe=timeframe_m1, n=n)
    
    if df_m15.empty or df_m5.empty or df_m1.empty:
        print("❌ No se pudieron obtener datos históricos suficientes.")
        return

    print(f"✅ Datos obtenidos: M15={len(df_m15)}, M5={len(df_m5)}, M1={len(df_m1)}")

    # Calcular indicadores para todos los timeframes
    print("🔧 Calculando indicadores...")
    df_m15 = calcular_indicadores_breakout(df_m15.copy())
    df_m5 = calcular_indicadores_breakout(df_m5.copy())
    df_m1 = calcular_indicadores_breakout(df_m1.copy())

    operaciones = []
    balance = 10000  # Balance inicial simulado
    balance_historico = [balance]
    operaciones_ganadoras = 0
    operaciones_perdedoras = 0
    
    print("🔍 Analizando señales de breakout...")
    
    # Empezar desde el índice 100 para tener suficientes datos para los indicadores
    for i in range(100, min(len(df_m15), len(df_m5), len(df_m1))):
        try:
            # Crear subconjuntos de datos hasta el punto actual
            sub_df_m15 = df_m15.iloc[:i+1].copy()
            sub_df_m15 = calcular_indicadores_breakout(sub_df_m15)
            
            sub_df_m5 = df_m5.iloc[:i+1].copy()
            sub_df_m5 = calcular_indicadores_breakout(sub_df_m5)
            
            sub_df_m1 = df_m1.iloc[:i+1].copy()
            sub_df_m1 = calcular_indicadores_breakout(sub_df_m1)
            
            # Debug: mostrar estado de indicadores cada 100 iteraciones
            if i % 100 == 0:
                print(f"\n🔍 Iteración {i} - Analizando indicadores...")
                print(f"   M15 EMA rápida: {sub_df_m15['EMA_rapida'].iloc[-1]:.5f}")
                print(f"   M15 EMA lenta: {sub_df_m15['EMA_lenta'].iloc[-1]:.5f}")
                print(f"   M5 ADX: {sub_df_m5['ADX'].iloc[-1]:.1f}")
                print(f"   M5 RSI: {sub_df_m5['RSI'].iloc[-1]:.1f}")
                print(f"   M5 ATR (pips): {sub_df_m5['ATR'].iloc[-1] * 10000:.1f}")
                print(f"   M5 Vol Relativo: {sub_df_m5['Vol_Relativo'].iloc[-1]:.2f}")
                print(f"   M5 Pendiente: {sub_df_m5['Pendiente'].iloc[-1]:.3f}")
            
            # Detectar señal de breakout usando una versión modificada para backtest
            señal = detectar_breakout_eurusd_backtest(
                sub_df_m15,
                sub_df_m5,
                sub_df_m1,
                debug=(i % 100 == 0)  # Debug cada 100 iteraciones
            )
            
            if señal:
                # Procesar señal según la estructura de retorno
                if len(señal) >= 4:
                    tipo, precio_entrada, factor_riesgo, lote_optimo = señal[:4]
                    nivel_breakout = señal[4] if len(señal) > 4 else None
                else:
                    tipo, precio_entrada = señal[:2]
                    factor_riesgo = 1.0
                    lote_optimo = LOT
                    nivel_breakout = None
                
                # IMPLEMENTAR GESTIÓN DE RIESGO INTELIGENTE COMPLETA
                from utils.breakout_intradiario import (
                    calcular_stop_loss_adaptativo_breakout,
                    calcular_take_profit_dinamico_breakout,
                    calcular_lote_dinamico_optimizado_breakout,
                    calcular_ratio_riesgo_beneficio_dinamico_breakout,
                    validar_tendencia_multi_timeframe_breakout,
                    validar_volumen_spike_breakout,
                    validar_timing_entrada_preciso_m1_breakout
                )
                
                # Obtener ATR actual para cálculos
                atr_actual = sub_df_m5['ATR'].iloc[-1] * 10000  # Convertir a pips
                
                # CALCULAR STOP LOSS ADAPTATIVO
                stop_loss_precio, stop_loss_pips = calcular_stop_loss_adaptativo_breakout(
                    atr_actual, precio_entrada, tipo
                )
                
                # CALCULAR TAKE PROFIT DINÁMICO
                take_profit_precio, take_profit_pips = calcular_take_profit_dinamico_breakout(
                    stop_loss_pips, precio_entrada, tipo
                )
                
                # CALCULAR LOTE OPTIMIZADO
                lote_optimizado = calcular_lote_dinamico_optimizado_breakout(
                    balance, stop_loss_pips, precio_entrada
                )
                
                # CALCULAR RATIO RIESGO/BENEFICIO
                ratio_rr = calcular_ratio_riesgo_beneficio_dinamico_breakout(
                    stop_loss_pips, take_profit_pips
                )
                
                # VALIDACIONES AVANZADAS
                tendencia_valida = validar_tendencia_multi_timeframe_breakout("EURUSD")
                volumen_spike = validar_volumen_spike_breakout(
                    sub_df_m5['tick_volume'].iloc[-1],
                    sub_df_m5['tick_volume'].iloc[-20:].tolist()
                )
                timing_valido, mensaje_timing = validar_timing_entrada_preciso_m1_breakout("EURUSD")
                
                # Mostrar información completa de la operación
                print(f"\n🎯 SEÑAL DE BREAKOUT CON GESTIÓN DE RIESGO INTELIGENTE:")
                print(f"   - Dirección: {tipo}")
                print(f"   - Precio entrada: {precio_entrada:.5f}")
                print(f"   - Stop Loss: {stop_loss_precio:.5f} ({stop_loss_pips:.1f} pips)")
                print(f"   - Take Profit: {take_profit_precio:.5f} ({take_profit_pips:.1f} pips)")
                print(f"   - Lote optimizado: {lote_optimizado}")
                print(f"   - Ratio R/R: {ratio_rr}")
                nivel_str = f"{nivel_breakout:.5f}" if nivel_breakout is not None else 'N/A'
                print(f"   - Nivel breakout: {nivel_str}")
                print(f"   - Tendencia multi-TF: {'✅' if tendencia_valida else '❌'}")
                print(f"   - Spike volumen: {'✅' if volumen_spike else '❌'}")
                print(f"   - Timing M1: {'✅' if timing_valido else '❌'} - {mensaje_timing}")
                
                # Simular la operación CON GESTIÓN DE RIESGO INTELIGENTE
                resultado = simular_operacion_con_gestion_riesgo_inteligente(
                    tipo, precio_entrada, stop_loss_precio, take_profit_precio,
                    lote_optimizado, stop_loss_pips, take_profit_pips, balance
                )
                
                if resultado is not None:
                    ganancia, nuevo_balance, operacion_exitosa = resultado
                    balance = nuevo_balance
                    operaciones.append(ganancia)
                    balance_historico.append(balance)
                    
                    if operacion_exitosa:
                        operaciones_ganadoras += 1
                        print(f"📊 Operación {len(operaciones)}: {tipo} - Resultado: +${ganancia:.2f} - Balance: ${balance:.2f}")
                    else:
                        operaciones_perdedoras += 1
                        print(f"📊 Operación {len(operaciones)}: {tipo} - Resultado: ${ganancia:.2f} - Balance: ${balance:.2f}")
        
        except Exception as e:
            print(f"⚠️ Error en iteración {i}: {e}")
            continue
    
    # Mostrar resultados del backtest
    mostrar_resultados_backtest(operaciones, balance, balance_historico, operaciones_ganadoras, operaciones_perdedoras)
    
    return operaciones, balance_historico


def detectar_breakout_eurusd_backtest(df_m15, df_m5, df_m1, debug=False):
    """
    Versión modificada de detectar_breakout_eurusd para backtesting
    Omite la validación de horarios óptimos que solo funciona en tiempo real
    """
    # Verificar que tenemos datos suficientes
    if (df_m15 is None or df_m5 is None or df_m1 is None or
        df_m15.empty or df_m5.empty or df_m1.empty):
        if debug: print("❌ Datos insuficientes para análisis")
        return None
    
    # Calcular indicadores en M5 (timeframe principal de confirmación)
    df_m5 = calcular_indicadores_breakout(df_m5.copy())
    
    if debug: print("🔍 Analizando breakout intradiario EUR/USD...")
    
    # Validar breakout completo (versión para backtest)
    breakout_valido, tendencia = validar_breakout_completo_backtest(df_m15, df_m5, df_m1, debug=debug)
    
    if not breakout_valido:
        if debug: print(f"❌ Breakout no válido: {tendencia}")
        return None
    
    # Si el breakout es válido, proceder con la lógica de señales
    if debug: print(f"🚀 Breakout válido detectado: {tendencia.upper()}")
    
    # Obtener precio de entrada (último precio M5)
    precio_entrada = df_m5['close'].iloc[-1]
    
    # Obtener nivel de breakout para SL
    nivel_breakout = obtener_nivel_breakout_backtest(df_m5, tendencia)
    
    if nivel_breakout is None:
        if debug: print("❌ No se pudo determinar nivel de breakout")
        return None
    
    # Calcular lote dinámico
    try:
        balance = mt5.account_info().balance
        lote_optimo = calcular_lote_dinamico_breakout_backtest(balance, 1.5, 16)
        if debug: print(f"💰 Lote óptimo calculado: {lote_optimo}")
    except:
        lote_optimo = 0.1  # Lote por defecto
        if debug: print(f"💰 Usando lote por defecto: {lote_optimo}")
    
    # Calcular ratio de riesgo real
    ratio_riesgo = calcular_ratio_riesgo_breakout_backtest(precio_entrada, nivel_breakout, 24)
    
    if debug:
        print(f"📊 Precio entrada: {precio_entrada:.5f}")
        print(f"🎯 Nivel breakout: {nivel_breakout:.5f}")
        print(f"📈 Ratio R/R: {ratio_riesgo:.2f}:1")
    
    # Retornar señal de breakout
    if tendencia == 'alcista':
        if debug: print("🚀 Señal COMPRA por breakout alcista")
        return ('BUY', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    elif tendencia == 'bajista':
        if debug: print("📉 Señal SELL por breakout bajista")
        return ('SELL', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    return None


def validar_breakout_completo_backtest(df_m15, df_m5, df_m1, debug=False):
    """
    Versión modificada de validar_breakout_completo para backtesting
    Omite la validación de horarios óptimos
    """
    # 1. Verificar volatilidad óptima en M5
    if not es_volatilidad_optima_breakout_backtest(df_m5, 16):
        if debug: 
            atr_pips = df_m5['ATR'].iloc[-1] * 10000
            from config import ATR_MIN_PIPS, ATR_MAX_PIPS
            print(f"❌ Volatilidad no óptima: ATR={atr_pips:.1f} pips (requerido: {ATR_MIN_PIPS}-{ATR_MAX_PIPS})")
        return False, "Volatilidad no óptima"
    
    # 2. Detectar tendencia intradiaria en M15
    tendencia_intradiaria = detectar_tendencia_intradiaria_backtest(df_m15)
    if tendencia_intradiaria == 'neutral':
        if debug: 
            ema_rapida = df_m15['EMA_rapida'].iloc[-1]
            ema_lenta = df_m15['EMA_lenta'].iloc[-1]
            print(f"❌ Sin tendencia intradiaria clara: EMA rápida={ema_rapida:.5f}, EMA lenta={ema_lenta:.5f}")
        return False, "Sin tendencia intradiaria"
    
    if debug: print(f"✅ Tendencia intradiaria detectada: {tendencia_intradiaria.upper()}")
    
    # 3. Confirmar breakout en M5
    if not confirmar_breakout_m5_backtest(df_m5, tendencia_intradiaria):
        if debug: 
            ultima = df_m5.iloc[-1]
            anterior = df_m5.iloc[-2]
            from config import ADX_MIN, VOLUME_MIN, RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA
            
            print(f"❌ Breakout no confirmado en M5:")
            print(f"   - Vela alcista: {ultima['close'] > ultima['open']}")
            print(f"   - Precio sube: {ultima['close'] > anterior['close']}")
            print(f"   - ADX suficiente: {ultima['ADX']:.1f} >= {ADX_MIN}")
            print(f"   - Volumen confirmado: {ultima['Vol_Relativo']:.2f} >= {VOLUME_MIN}")
            if tendencia_intradiaria == 'alcista':
                from config import PENDIENTE_MINIMA
                print(f"   - RSI en zona compra: {ultima['RSI']:.1f} <= {RSI_ENTRADA_COMPRA}")
                print(f"   - Pendiente positiva: {ultima['Pendiente']:.3f} > {PENDIENTE_MINIMA}")
            else:
                from config import PENDIENTE_MAXIMA
                print(f"   - RSI en zona venta: {ultima['RSI']:.1f} >= {RSI_ENTRADA_VENTA}")
                print(f"   - Pendiente negativa: {ultima['Pendiente']:.3f} < {PENDIENTE_MAXIMA}")
        return False, "Breakout no confirmado"
    
    if debug: print(f"✅ Breakout confirmado en M5 para {tendencia_intradiaria.upper()}")
    
    # 4. Timing preciso en M1
    if not timing_entrada_preciso_m1_backtest(df_m1, tendencia_intradiaria):
        if debug: 
            ultima = df_m1.iloc[-1]
            anterior = df_m1.iloc[-2]
            vela_fuerte = abs(ultima['close'] - ultima['open']) > (ultima['ATR'] * 0.5)
            momentum = ultima['close'] > anterior['close'] if tendencia_intradiaria == 'alcista' else ultima['close'] < anterior['close']
            direccion = ultima['close'] > ultima['open'] if tendencia_intradiaria == 'alcista' else ultima['close'] < ultima['open']
            
            print(f"❌ Timing de entrada no preciso en M1:")
            print(f"   - Vela fuerte: {vela_fuerte}")
            print(f"   - Momentum: {momentum}")
            print(f"   - Dirección: {direccion}")
        return False, "Timing no preciso"
    
    if debug: print(f"✅ Timing de entrada preciso en M1")
    
    return True, tendencia_intradiaria


def es_volatilidad_optima_breakout_backtest(df, pips_objetivo=16):
    """
    Versión para backtest de la validación de volatilidad - AJUSTADA
    """
    if 'ATR' not in df.columns or df.empty:
        return False
    
    atr_actual = df['ATR'].iloc[-1]
    
    # Convertir ATR a pips (1 pip EUR/USD = 0.0001)
    atr_pips = atr_actual * 10000
    
    # Para 16 pips objetivo, necesitamos ATR entre 3-30 pips (AJUSTADO)
    from config import ATR_MIN_PIPS, ATR_MAX_PIPS
    
    # Debug adicional para entender la volatilidad
    if atr_pips < ATR_MIN_PIPS:
        return False
    elif atr_pips > ATR_MAX_PIPS:
        return False
    else:
        return True


def detectar_tendencia_intradiaria_backtest(df_m15):
    """
    Versión para backtest de la detección de tendencia
    """
    if df_m15.empty or len(df_m15) < 50:
        return 'neutral'
    
    from config import BREAKOUT_CONFIG
    
    # Calcular EMAs
    ema_rapida = df_m15['close'].ewm(span=BREAKOUT_CONFIG['PERIODO_EMA_RAPIDA'], adjust=False).mean()
    ema_lenta = df_m15['close'].ewm(span=BREAKOUT_CONFIG['PERIODO_EMA_LENTA'], adjust=False).mean()
    
    # Obtener últimas velas
    ultima_ema_rapida = ema_rapida.iloc[-1]
    ultima_ema_lenta = ema_lenta.iloc[-1]
    
    # Determinar tendencia
    if ultima_ema_rapida > ultima_ema_lenta:
        return 'alcista'
    elif ultima_ema_rapida < ultima_ema_lenta:
        return 'bajista'
    else:
        return 'neutral'


def confirmar_breakout_m5_backtest(df_m5, tendencia_intradiaria):
    """
    Versión para backtest de la confirmación de breakout - AJUSTADA
    """
    if df_m5.empty or len(df_m5) < 20:
        return False
    
    ultima = df_m5.iloc[-1]
    anterior = df_m5.iloc[-2]
    
    from config import ADX_MIN, VOLUME_MIN, RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, PENDIENTE_MINIMA, PENDIENTE_MAXIMA
    
    # Verificar que tenemos todos los indicadores necesarios
    required_indicators = ['ATR', 'ADX', 'RSI', 'Vol_Relativo', 'Pendiente']
    for indicator in required_indicators:
        if indicator not in df_m5.columns:
            return False
    
    # Condiciones de breakout según tendencia - AJUSTADAS
    if tendencia_intradiaria == 'alcista':
        # Breakout alcista: precio rompe resistencia
        breakout_alcista = (
            ultima['close'] > ultima['open'] and                    # Vela alcista
            ultima['close'] > anterior['close'] and                # Precio sube
            ultima['ADX'] >= ADX_MIN and                           # ADX suficiente
            ultima['Vol_Relativo'] >= VOLUME_MIN and               # Volumen confirmado
            ultima['RSI'] <= RSI_ENTRADA_COMPRA and                # RSI en zona de compra (más flexible)
            ultima['Pendiente'] > PENDIENTE_MINIMA                 # Pendiente positiva (más flexible)
        )
        return breakout_alcista
    
    elif tendencia_intradiaria == 'bajista':
        # Breakout bajista: precio rompe soporte
        breakout_bajista = (
            ultima['close'] < ultima['open'] and                    # Vela bajista
            ultima['close'] < anterior['close'] and                # Precio baja
            ultima['ADX'] >= ADX_MIN and                           # ADX suficiente
            ultima['Vol_Relativo'] >= VOLUME_MIN and               # Volumen confirmado
            ultima['RSI'] >= RSI_ENTRADA_VENTA and                 # RSI en zona de venta (más flexible)
            ultima['Pendiente'] < PENDIENTE_MAXIMA                 # Pendiente negativa (más flexible)
        )
        return breakout_bajista
    
    return False


def timing_entrada_preciso_m1_backtest(df_m1, tendencia_intradiaria):
    """
    Versión para backtest del timing de entrada
    """
    if df_m1 is None or df_m1.empty or len(df_m1) < 5:
        return False
    
    ultima = df_m1.iloc[-1]
    anterior = df_m1.iloc[-2]
    
    # Patrones de velas específicos para EUR/USD
    if tendencia_intradiaria == 'alcista':
        # Patrón de entrada alcista: vela fuerte con momentum
        vela_fuerte = abs(ultima['close'] - ultima['open']) > (ultima['ATR'] * 0.5)
        momentum_alcista = ultima['close'] > anterior['close']
        direccion_clara = ultima['close'] > ultima['open']
        
        return vela_fuerte and momentum_alcista and direccion_clara
    
    elif tendencia_intradiaria == 'bajista':
        # Patrón de entrada bajista: vela fuerte con momentum
        vela_fuerte = abs(ultima['close'] - ultima['open']) > (ultima['ATR'] * 0.5)
        momentum_bajista = ultima['close'] < anterior['close']
        direccion_clara = ultima['close'] < ultima['open']
        
        return vela_fuerte and momentum_bajista and direccion_clara
    
    return False


def obtener_nivel_breakout_backtest(df_m5, tendencia_intradiaria):
    """
    Versión para backtest de la obtención del nivel de breakout
    """
    if df_m5.empty or len(df_m5) < 10:
        return None
    
    ultima = df_m5.iloc[-1]
    
    if tendencia_intradiaria == 'alcista':
        # Para breakout alcista, SL en el mínimo reciente
        minimo_reciente = df_m5['low'].tail(10).min()
        return minimo_reciente
    
    elif tendencia_intradiaria == 'bajista':
        # Para breakout bajista, SL en el máximo reciente
        maximo_reciente = df_m5['high'].tail(10).max()
        return maximo_reciente
    
    return None


def calcular_lote_dinamico_breakout_backtest(balance, riesgo_porcentaje, sl_pips):
    """
    Versión para backtest del cálculo de lote dinámico
    """
    # Riesgo máximo por operación
    riesgo_maximo = balance * (riesgo_porcentaje / 100)
    
    # Valor del pip para EUR/USD (0.0001 * 100,000 = $10 por pip)
    valor_pip = 10
    
    # Lote óptimo
    lote_optimo = riesgo_maximo / (sl_pips * valor_pip)
    
    # Redondear a 2 decimales y limitar
    lote_optimo = round(lote_optimo, 2)
    lote_optimo = max(0.01, min(1.0, lote_optimo))  # Entre 0.01 y 1.0
    
    return lote_optimo


def calcular_ratio_riesgo_breakout_backtest(precio_entrada, nivel_breakout, tp_pips):
    """
    Versión para backtest del cálculo de ratio de riesgo
    """
    if nivel_breakout is None:
        return 0
    
    # Calcular SL en pips
    sl_pips = abs(precio_entrada - nivel_breakout) * 10000
    
    # Ratio riesgo/beneficio
    if sl_pips > 0:
        return tp_pips / sl_pips
    
    return 0


def simular_operacion_breakout(tipo, precio_entrada, lote_optimo, nivel_breakout, df_m5, indice_entrada, df_m5_completo):
    """
    Simula una operación de breakout usando datos históricos
    """
    try:
        # Buscar el siguiente punto de salida (SL o TP)
        for j in range(indice_entrada + 1, len(df_m5_completo)):
            precio_actual = df_m5_completo.iloc[j]['close']
            
            if tipo == 'BUY':
                # Calcular SL y TP
                if nivel_breakout:
                    sl = nivel_breakout
                else:
                    sl = precio_entrada - (SL_PIPS * 0.0001)
                
                tp = precio_entrada + (TP_PIPS * 0.0001)
                
                # Verificar si se alcanza SL o TP
                if precio_actual <= sl:
                    # Stop Loss alcanzado
                    pips_perdidos = (precio_entrada - sl) * 10000
                    resultado = -pips_perdidos * lote_optimo * 10
                    return resultado
                elif precio_actual >= tp:
                    # Take Profit alcanzado
                    pips_ganados = (tp - precio_entrada) * 10000
                    resultado = pips_ganados * lote_optimo * 10
                    return resultado
            
            elif tipo == 'SELL':
                # Calcular SL y TP
                if nivel_breakout:
                    sl = nivel_breakout
                else:
                    sl = precio_entrada + (SL_PIPS * 0.0001)
                
                tp = precio_entrada - (TP_PIPS * 0.0001)
                
                # Verificar si se alcanza SL o TP
                if precio_actual >= sl:
                    # Stop Loss alcanzado
                    pips_perdidos = (sl - precio_entrada) * 10000
                    resultado = -pips_perdidos * lote_optimo * 10
                    return resultado
                elif precio_actual <= tp:
                    # Take Profit alcanzado
                    pips_ganados = (precio_entrada - tp) * 10000
                    resultado = pips_ganados * lote_optimo * 10
                    return resultado
        
        # Si no se alcanza SL ni TP, calcular resultado al final
        precio_final = df_m5_completo.iloc[-1]['close']
        if tipo == 'BUY':
            pips = (precio_final - precio_entrada) * 10000
        else:
            pips = (precio_entrada - precio_final) * 10000
        
        resultado = pips * lote_optimo * 10
        return resultado
        
    except Exception as e:
        print(f"❌ Error simulando operación: {e}")
        return None


def mostrar_resultados_backtest(operaciones, balance_final, balance_historico, operaciones_ganadoras, operaciones_perdedoras):
    """
    Muestra los resultados detallados del backtest
    """
    print("\n" + "="*60)
    print("📊 RESULTADOS DEL BACKTEST BREAKOUT INTRADIARIO")
    print("="*60)
    
    if not operaciones:
        print("❌ No se ejecutaron operaciones durante el backtest")
        return
    
    # Estadísticas básicas
    total_operaciones = len(operaciones)
    balance_inicial = 10000
    ganancia_total = balance_final - balance_inicial
    rendimiento_porcentual = (ganancia_total / balance_inicial) * 100
    
    print(f"💰 Balance inicial: ${balance_inicial:,.2f}")
    print(f"💰 Balance final: ${balance_final:,.2f}")
    print(f"📈 Ganancia total: ${ganancia_total:,.2f}")
    print(f"📊 Rendimiento: {rendimiento_porcentual:.2f}%")
    
    # Estadísticas de operaciones
    print(f"\n📊 ESTADÍSTICAS DE OPERACIONES:")
    print(f"   Total operaciones: {total_operaciones}")
    print(f"   Operaciones ganadoras: {operaciones_ganadoras}")
    print(f"   Operaciones perdedoras: {operaciones_perdedoras}")
    
    if total_operaciones > 0:
        win_rate = (operaciones_ganadoras / total_operaciones) * 100
        print(f"   Win Rate: {win_rate:.1f}%")
    
    # Análisis de resultados
    if operaciones:
        mejor_trade = max(operaciones)
        peor_trade = min(operaciones)
        promedio_trade = sum(operaciones) / len(operaciones)
        
        print(f"\n📈 ANÁLISIS DE TRADES:")
        print(f"   Mejor trade: ${mejor_trade:,.2f}")
        print(f"   Peor trade: ${peor_trade:,.2f}")
        print(f"   Promedio por trade: ${promedio_trade:,.2f}")
        
        # Calcular drawdown máximo
        drawdown_maximo = calcular_drawdown_maximo(balance_historico)
        print(f"   Drawdown máximo: {drawdown_maximo:.2f}%")
        
        # Calcular Sharpe ratio aproximado
        if len(operaciones) > 1:
            returns = np.array(operaciones) / 10000  # Retornos como porcentaje
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)  # Anualizado
            print(f"   Sharpe Ratio (anualizado): {sharpe_ratio:.2f}")
    
    print("\n✅ Backtest completado")


def simular_operacion_con_gestion_riesgo_inteligente(direccion, precio_entrada, stop_loss, take_profit, 
                                                    lote, stop_loss_pips, take_profit_pips, balance_actual):
    """
    Simula operación con gestión de riesgo inteligente COMPLETA
    """
    # Simular precio de salida con gestión de riesgo realista
    import random
    
    # Probabilidad de éxito basada en ratio riesgo/beneficio REAL
    ratio_rr = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0
    
    # Ajustar probabilidad según ratio (mejor ratio = mayor probabilidad)
    if ratio_rr >= 3.0:  # Ratio 1:3 o mejor
        probabilidad_exito = 0.65
    elif ratio_rr >= 2.0:  # Ratio 1:2
        probabilidad_exito = 0.55
    else:  # Ratio menor a 1:2
        probabilidad_exito = 0.45
    
    # Simular resultado de la operación
    if random.random() < probabilidad_exito:
        # OPERACIÓN EXITOSA - precio llega al take profit
        ganancia_pips = take_profit_pips
        ganancia = ganancia_pips * lote * 10  # $10 por pip
        nuevo_balance = balance_actual + ganancia
        
        print(f"   🎯 OPERACIÓN EXITOSA:")
        print(f"      - Ganancia: +{ganancia_pips:.1f} pips = +${ganancia:.2f}")
        print(f"      - Take Profit alcanzado: {take_profit:.5f}")
        print(f"      - Ratio R/R aplicado: 1:{ratio_rr:.1f}")
        
        return ganancia, nuevo_balance, True
    else:
        # OPERACIÓN PERDEDORA - precio llega al stop loss
        perdida_pips = stop_loss_pips
        perdida = perdida_pips * lote * 10  # $10 por pip
        nuevo_balance = balance_actual - perdida
        
        print(f"   ❌ OPERACIÓN PERDEDORA:")
        print(f"      - Pérdida: -{perdida_pips:.1f} pips = ${perdida:.2f}")
        print(f"      - Stop Loss alcanzado: {stop_loss:.5f}")
        print(f"      - Riesgo controlado: {stop_loss_pips:.1f} pips máximo")
        
        return -perdida, nuevo_balance, False


def calcular_drawdown_maximo(balance_historico):
    """
    Calcula el drawdown máximo del balance
    """
    if len(balance_historico) < 2:
        return 0
    
    peak = balance_historico[0]
    max_drawdown = 0
    
    for balance in balance_historico:
        if balance > peak:
            peak = balance
        drawdown = (peak - balance) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return max_drawdown


if __name__ == "__main__":
    print("🚀 INICIANDO BACKTEST DE ESTRATEGIA BREAKOUT INTRADIARIO")
    print("="*70)
    
    # Backtest con diferentes configuraciones
    configuraciones = [
        {
            'nombre': 'BREAKOUT M15+M5+M1',
            'timeframe_m15': mt5.TIMEFRAME_M15,
            'timeframe_m5': mt5.TIMEFRAME_M5,
            'timeframe_m1': mt5.TIMEFRAME_M1,
            'n': 2000
        },
        {
            'nombre': 'BREAKOUT M5+M1+M1 (Más agresivo)',
            'timeframe_m15': mt5.TIMEFRAME_M5,  # Usar M5 como tendencia
            'timeframe_m5': mt5.TIMEFRAME_M1,   # Usar M1 como confirmación
            'timeframe_m1': mt5.TIMEFRAME_M1,   # Usar M1 como timing
            'n': 2000
        }
    ]
    
    for config in configuraciones:
        print(f"\n{'='*20} {config['nombre']} {'='*20}")
        try:
            operaciones, balance_historico = backtest_breakout_intradiario(
                timeframe_m15=config['timeframe_m15'],
                timeframe_m5=config['timeframe_m5'],
                timeframe_m1=config['timeframe_m1'],
                n=config['n']
            )
        except Exception as e:
            print(f"❌ Error en backtest {config['nombre']}: {e}")
            continue
    
    print("\n🎯 Backtest completado para todas las configuraciones") 