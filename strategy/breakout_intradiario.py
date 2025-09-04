"""
Estrategia de BREAKOUT INTRADIARIO para EUR/USD
Optimizada para objetivo 1-2% (12-20 pips)
Solo usa timeframes intradiarios para consistencia temporal
"""
import pandas as pd
import numpy as np
from scipy.stats import linregress
import MetaTrader5 as mt5
from utils.breakout_intradiario import (
    validar_breakout_completo,
    calcular_lote_dinamico_breakout,
    obtener_nivel_breakout,
    calcular_ratio_riesgo_breakout
)
from config import SYMBOL, BREAKOUT_CONFIG


def hay_posicion_abierta(symbol, tipo):
    """Verifica si ya existe una posición abierta en la dirección especificada"""
    try:
        posiciones = mt5.positions_get(symbol=symbol)
        if posiciones is None:
            return False
        tipo_mt5 = 0 if tipo == 'BUY' else 1  # 0=compra, 1=venta
        return any(pos.type == tipo_mt5 for pos in posiciones)
    except:
        return False


def calcular_indicadores_breakout(df):
    """
    Calcula todos los indicadores necesarios para la estrategia de breakout
    """
    if df.empty or len(df) < max(BREAKOUT_CONFIG.values()):
        return df
    
    # Calcular EMAs
    df['EMA_rapida'] = df['close'].ewm(span=BREAKOUT_CONFIG['PERIODO_EMA_RAPIDA'], adjust=False).mean()
    df['EMA_lenta'] = df['close'].ewm(span=BREAKOUT_CONFIG['PERIODO_EMA_LENTA'], adjust=False).mean()
    
    # Calcular ADX
    df['TR'] = pd.concat([
        df['high'] - df['low'],
        abs(df['high'] - df['close'].shift()),
        abs(df['low'] - df['close'].shift())
    ], axis=1).max(axis=1)
    
    df['plus_dm'] = np.where(
        (df['high'] - df['high'].shift() > df['low'].shift() - df['low']) &
        (df['high'] - df['high'].shift() > 0),
        df['high'] - df['high'].shift(), 0
    )
    
    df['minus_dm'] = np.where(
        (df['low'].shift() - df['low'] > df['high'] - df['high'].shift()) &
        (df['low'].shift() - df['low'] > 0),
        df['low'].shift() - df['low'], 0
    )
    
    df['TR_smooth'] = df['TR'].rolling(window=BREAKOUT_CONFIG['PERIODO_ADX']).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=BREAKOUT_CONFIG['PERIODO_ADX']).mean() / df['TR_smooth'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=BREAKOUT_CONFIG['PERIODO_ADX']).mean() / df['TR_smooth'])
    df['DX'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['ADX'] = df['DX'].rolling(window=BREAKOUT_CONFIG['PERIODO_ADX']).mean()
    
    # Calcular RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/BREAKOUT_CONFIG['PERIODO_RSI'], adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/BREAKOUT_CONFIG['PERIODO_RSI'], adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Calcular ATR
    df['ATR'] = df['TR'].rolling(window=BREAKOUT_CONFIG['PERIODO_ATR']).mean()
    
    # Calcular volumen relativo
    df['Vol_MA'] = df['tick_volume'].rolling(window=BREAKOUT_CONFIG['PERIODO_VOLUMEN']).mean()
    df['Vol_Relativo'] = df['tick_volume'] / df['Vol_MA']
    
    # Calcular pendiente de tendencia
    def calcular_pendiente(serie):
        if len(serie) < 5:
            return 0
        x = np.arange(len(serie))
        slope, _, _, _, _ = linregress(x, serie)
        return slope * 100
    
    df['Pendiente'] = df['close'].rolling(window=BREAKOUT_CONFIG['PERIODO_PENDIENTE']).apply(calcular_pendiente, raw=False)
    
    return df


def detectar_breakout_eurusd(df_m15, df_m5, df_m1, debug=False):
    """
    Estrategia principal de breakout intradiario para EUR/USD
    """
    # Verificar que tenemos datos suficientes
    if (df_m15 is None or df_m5 is None or df_m1 is None or
        df_m15.empty or df_m5.empty or df_m1.empty):
        if debug: print("❌ Datos insuficientes para análisis")
        return None
    
    # Calcular indicadores en M5 (timeframe principal de confirmación)
    df_m5 = calcular_indicadores_breakout(df_m5.copy())
    
    if debug: print("🔍 Analizando breakout intradiario EUR/USD...")
    
    # Validar breakout completo
    breakout_valido, tendencia = validar_breakout_completo(df_m15, df_m5, df_m1, debug=debug)
    
    if not breakout_valido:
        if debug: print(f"❌ Breakout no válido: {tendencia}")
        return None
    
    # Si el breakout es válido, proceder con la lógica de señales
    if debug: print(f"🚀 Breakout válido detectado: {tendencia.upper()}")
    
    # Obtener precio de entrada (último precio M5)
    precio_entrada = df_m5['close'].iloc[-1]
    
    # Obtener nivel de breakout para SL
    nivel_breakout = obtener_nivel_breakout(df_m5, tendencia)
    
    if nivel_breakout is None:
        if debug: print("❌ No se pudo determinar nivel de breakout")
        return None
    
    # Calcular lote dinámico
    try:
        balance = mt5.account_info().balance
        lote_optimo = calcular_lote_dinamico_breakout(balance, 1.5, 16)  # 1.5% riesgo, 16 pips SL
        if debug: print(f"💰 Lote óptimo calculado: {lote_optimo}")
    except:
        lote_optimo = 0.1  # Lote por defecto
        if debug: print(f"💰 Usando lote por defecto: {lote_optimo}")
    
    # Calcular ratio de riesgo real
    ratio_riesgo = calcular_ratio_riesgo_breakout(precio_entrada, nivel_breakout, 24)
    
    if debug:
        print(f"📊 Precio entrada: {precio_entrada:.5f}")
        print(f"🛑 Nivel breakout: {nivel_breakout:.5f}")
        print(f"📈 Ratio R/R: {ratio_riesgo:.2f}:1")
    
    # Verificar que no hay posición abierta en la misma dirección
    if hay_posicion_abierta(SYMBOL, tendencia.upper()):
        if debug: print(f"❌ Ya existe posición abierta en dirección {tendencia}")
        return None
    
    # Retornar señal de breakout
    if tendencia == 'alcista':
        if debug: print("🚀 Señal COMPRA por breakout alcista")
        return ('BUY', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    elif tendencia == 'bajista':
        if debug: print("📉 Señal SELL por breakout bajista")
        return ('SELL', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    return None


def analizar_mercado_breakout(df_m15, df_m5, df_m1, debug=False):
    """
    Análisis completo del mercado para estrategia de breakout
    """
    if debug: print("🔍 ANÁLISIS COMPLETO DE MERCADO BREAKOUT")
    
    # 1. Análisis de tendencia intradiaria (M15)
    if df_m15 is not None and not df_m15.empty:
        df_m15 = calcular_indicadores_breakout(df_m15.copy())
        tendencia_m15 = 'alcista' if df_m15['EMA_rapida'].iloc[-1] > df_m15['EMA_lenta'].iloc[-1] else 'bajista'
        if debug: print(f"📊 M15 - Tendencia: {tendencia_m15.upper()}")
    
    # 2. Análisis de confirmación (M5)
    if df_m5 is not None and not df_m5.empty:
        df_m5 = calcular_indicadores_breakout(df_m5.copy())
        adx_m5 = df_m5['ADX'].iloc[-1] if 'ADX' in df_m5.columns else 0
        rsi_m5 = df_m5['RSI'].iloc[-1] if 'RSI' in df_m5.columns else 50
        if debug: print(f"📊 M5 - ADX: {adx_m5:.1f}, RSI: {rsi_m5:.1f}")
    
    # 3. Análisis de timing (M1)
    if df_m1 is not None and not df_m1.empty:
        ultima_m1 = df_m1.iloc[-1]
        if debug: print(f"📊 M1 - Última vela: {'alcista' if ultima_m1['close'] > ultima_m1['open'] else 'bajista'}")
    
    if debug: print("✅ Análisis de mercado completado")


def obtener_estadisticas_breakout(df_m15, df_m5, df_m1):
    """
    Obtiene estadísticas para análisis de rendimiento
    """
    stats = {
        'tendencia_m15': 'neutral',
        'adx_m5': 0,
        'rsi_m5': 50,
        'volatilidad_m5': 0,
        'volumen_relativo': 1.0
    }
    
    if df_m15 is not None and not df_m15.empty:
        df_m15 = calcular_indicadores_breakout(df_m15.copy())
        stats['tendencia_m15'] = 'alcista' if df_m15['EMA_rapida'].iloc[-1] > df_m15['EMA_lenta'].iloc[-1] else 'bajista'
    
    if df_m5 is not None and not df_m5.empty:
        df_m5 = calcular_indicadores_breakout(df_m5.copy())
        stats['adx_m5'] = df_m5['ADX'].iloc[-1] if 'ADX' in df_m5.columns else 0
        stats['rsi_m5'] = df_m5['RSI'].iloc[-1] if 'RSI' in df_m5.columns else 50
        stats['volatilidad_m5'] = df_m5['ATR'].iloc[-1] * 10000 if 'ATR' in df_m5.columns else 0
        stats['volumen_relativo'] = df_m5['Vol_Relativo'].iloc[-1] if 'Vol_Relativo' in df_m5.columns else 1.0
    
    return stats


def detectar_breakout_eurusd_backtest(df_m15, df_m5, df_m1, debug=False):
    """
    Estrategia principal de breakout intradiario para EUR/USD (versión backtest - sin validación de horario)
    """
    # Verificar que tenemos datos suficientes
    if df_m5 is None or df_m5.empty or len(df_m5) < 50:
        if debug: print("❌ Datos M5 insuficientes")
        return None
    
    if debug: print("🔍 Analizando breakout intradiario EUR/USD (BACKTEST)...")
    
    # Calcular indicadores en M5 (timeframe principal)
    df_m5 = calcular_indicadores_breakout(df_m5.copy())
    
    # Detectar tendencia intradiaria usando M15
    tendencia_intradiaria = None
    if df_m15 is not None and not df_m15.empty and len(df_m15) >= 20:
        df_m15 = calcular_indicadores_breakout(df_m15.copy())
        ema_rapida_m15 = df_m15['EMA_rapida'].iloc[-1]
        ema_lenta_m15 = df_m15['EMA_lenta'].iloc[-1]
        tendencia_intradiaria = 'alcista' if ema_rapida_m15 > ema_lenta_m15 else 'bajista'
        if debug: print(f"📊 Tendencia intradiaria M15: {tendencia_intradiaria}")
    
    # Validación simplificada para backtest (sin validación de horario)
    if not validar_breakout_simplificado(df_m5, tendencia_intradiaria, debug):
        if debug: print("❌ Breakout no válido: Filtros no cumplidos")
        return None
    
    # Si el breakout es válido, proceder con la lógica de señales
    if debug: print(f"🚀 Breakout válido detectado: {tendencia_intradiaria.upper()}")
    
    # Obtener precio de entrada (último precio M5)
    precio_entrada = df_m5['close'].iloc[-1]
    
    # Obtener nivel de breakout para SL
    nivel_breakout = obtener_nivel_breakout(df_m5, tendencia_intradiaria)
    
    if nivel_breakout is None:
        if debug: print("❌ No se pudo determinar nivel de breakout")
        return None
    
    # Calcular lote dinámico
    try:
        balance = mt5.account_info().balance
        lote_optimo = calcular_lote_dinamico_breakout(balance, 1.5, 16)  # 1.5% riesgo, 16 pips SL
        if debug: print(f"💰 Lote óptimo calculado: {lote_optimo}")
    except:
        lote_optimo = 0.1  # Lote por defecto
        if debug: print(f"💰 Usando lote por defecto: {lote_optimo}")
    
    # Calcular ratio de riesgo real
    ratio_riesgo = calcular_ratio_riesgo_breakout(precio_entrada, nivel_breakout, 24)
    
    if debug:
        print(f"📊 Precio entrada: {precio_entrada:.5f}")
        print(f"🛑 Nivel breakout: {nivel_breakout:.5f}")
        print(f"📈 Ratio R/R: {ratio_riesgo:.2f}:1")
    
    # Verificar que no hay posición abierta en la misma dirección
    if hay_posicion_abierta(SYMBOL, tendencia_intradiaria.upper()):
        if debug: print(f"❌ Ya existe posición abierta en dirección {tendencia_intradiaria}")
        return None
    
    # Retornar señal de breakout
    if tendencia_intradiaria == 'alcista':
        if debug: print("🚀 Señal COMPRA por breakout alcista")
        return ('BUY', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    elif tendencia_intradiaria == 'bajista':
        if debug: print("📉 Señal SELL por breakout bajista")
        return ('SELL', precio_entrada, 1.0, lote_optimo, nivel_breakout)
    
    return None


def validar_breakout_simplificado(df_m5, tendencia_intradiaria, debug=False):
    """
    Validación simplificada de breakout para backtest (sin validación de horario)
    """
    if df_m5 is None or df_m5.empty:
        return False
    
    # Obtener últimos valores
    ultima = df_m5.iloc[-1]
    anterior = df_m5.iloc[-2] if len(df_m5) > 1 else ultima
    
    # Validar que tenemos todos los indicadores necesarios
    if 'ADX' not in ultima or 'RSI' not in ultima or 'Vol_Relativo' not in ultima or 'ATR' not in ultima or 'Pendiente' not in ultima:
        if debug: print("❌ Indicadores incompletos")
        return False
    
    # Condiciones ULTRA FLEXIBLES de breakout (sin validación de horario)
    if tendencia_intradiaria == 'alcista':
        # Breakout alcista: precio rompe resistencia
        vela_alcista = ultima['close'] > ultima['open']
        precio_sube = ultima['close'] > anterior['close']
        adx_ok = ultima['ADX'] >= 12  # Optimizado para mayor precisión
        volumen_ok = ultima['Vol_Relativo'] >= 0.5  # Optimizado para confirmación
        rsi_ok = ultima['RSI'] <= 45  # Optimizado para entradas
        pendiente_ok = ultima['Pendiente'] > 0.0001  # Optimizado para precisión
        
        if debug:
            print(f"🔍 VALIDACIÓN BREAKOUT ALCISTA:")
            print(f"   - Vela alcista: {vela_alcista} ({ultima['close']:.5f} > {ultima['open']:.5f})")
            print(f"   - Precio sube: {precio_sube} ({ultima['close']:.5f} > {anterior['close']:.5f})")
            print(f"   - ADX ≥ 12: {adx_ok} ({ultima['ADX']:.1f})")
            print(f"   - Volumen ≥ 0.5: {volumen_ok} ({ultima['Vol_Relativo']:.2f})")
            print(f"   - RSI ≤ 45: {rsi_ok} ({ultima['RSI']:.1f})")
            print(f"   - Pendiente > 0.0001: {pendiente_ok} ({ultima['Pendiente']:.6f})")
        
        breakout_alcista = vela_alcista and precio_sube and adx_ok and volumen_ok and rsi_ok and pendiente_ok
        return breakout_alcista
    
    elif tendencia_intradiaria == 'bajista':
        # Breakout bajista: precio rompe soporte
        breakout_bajista = (
            ultima['close'] < ultima['open'] and                    # Vela bajista
            ultima['close'] < anterior['close'] and                # Precio baja
            ultima['ADX'] >= 12 and                                # ADX optimizado
            ultima['Vol_Relativo'] >= 0.5 and                      # Volumen optimizado
            ultima['RSI'] >= 55 and                                # RSI optimizado
            ultima['Pendiente'] < -0.0001                          # Pendiente optimizada
        )
        return breakout_bajista
    
    return False