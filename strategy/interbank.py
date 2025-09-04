import pandas as pd
import numpy as np
from scipy.stats import linregress
import MetaTrader5 as mt5
from utils.eurusd_intraday import (
    validar_entrada_eurusd_intraday,
    calcular_lote_dinamico_eurusd
)

# --- Utilidad para obtener tendencia de EMA en un dataframe ---
def tendencia_ema(df, ema_rapida=20, ema_lenta=50):
    df['EMA_rapida'] = df['close'].ewm(span=ema_rapida, adjust=False).mean()
    df['EMA_lenta'] = df['close'].ewm(span=ema_lenta, adjust=False).mean()
    if df['EMA_rapida'].iloc[-1] > df['EMA_lenta'].iloc[-1]:
        return 'alcista'
    elif df['EMA_rapida'].iloc[-1] < df['EMA_lenta'].iloc[-1]:
        return 'bajista'
    else:
        return 'neutral'

# --- Gestión de posiciones abiertas ---
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

# --- Análisis de mercado ---
def es_mercado_trending(df):
    """Determina si el mercado está en tendencia o lateral"""
    if len(df) < 20:
        return False
    adx_actual = df['ADX'].iloc[-1] if 'ADX' in df.columns else 0
    pendiente_actual = abs(df['Pendiente'].iloc[-1]) if 'Pendiente' in df.columns else 0
    return adx_actual > 25 and pendiente_actual > 0.1

def es_horario_volatil():
    """Verifica si estamos en horario de alta volatilidad (NY/London overlap)"""
    from datetime import datetime
    import pytz
    tz_ny = pytz.timezone('America/New_York')
    tz_london = pytz.timezone('Europe/London')
    
    ahora_ny = datetime.now(tz_ny)
    ahora_london = datetime.now(tz_london)
    
    # NY: 8-17, London: 8-17 (overlap 8-12 NY time)
    hora_ny = ahora_ny.hour
    hora_london = ahora_london.hour
    
    return (8 <= hora_ny <= 12) and (13 <= hora_london <= 17)

# --- Estrategia principal con confluencia de 4 timeframes ---
def detectar_entrada(df, df_m5=None, df_m15=None, df_h1=None, df_h4=None, df_d1=None, debug=False):
    """
    Estrategia intradía mejorada con confluencia de 4 timeframes:
    - D1 + H4: Tendencia principal (deben estar alineados)
    - M15: Confirmación de entrada
    - M5: Timing preciso de ejecución
    - Gestión de posiciones abiertas
    - Filtros dinámicos según condiciones de mercado
    """
    from config import SYMBOL
    
    # Configuración parámetros mejorados
    periodo_rsi = 14
    periodo_adx = 14
    periodo_ema_rapida = 20
    periodo_ema_lenta = 50
    periodo_volatilidad = 20
    
    # Calcular EMAs
    df['EMA_rapida'] = df['close'].ewm(span=periodo_ema_rapida, adjust=False).mean()
    df['EMA_lenta'] = df['close'].ewm(span=periodo_ema_lenta, adjust=False).mean()
    
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
    df['TR_smooth'] = df['TR'].rolling(window=periodo_adx).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=periodo_adx).mean() / df['TR_smooth'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=periodo_adx).mean() / df['TR_smooth'])
    df['DX'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['ADX'] = df['DX'].rolling(window=periodo_adx).mean()
    
    # RSI modificado
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/periodo_rsi, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/periodo_rsi, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Volatilidad (ATR porcentual)
    df['ATR'] = df['TR'].rolling(window=periodo_volatilidad).mean()
    df['Volatilidad'] = (df['ATR'] / df['close']) * 100
    
    # Volumen relativo
    df['Vol_MA'] = df['tick_volume'].rolling(window=20).mean()
    df['Vol_Relativo'] = df['tick_volume'] / df['Vol_MA']
    
    # Pendiente de tendencia
    def calcular_pendiente(serie):
        if len(serie) < 5:
            return 0
        x = np.arange(len(serie))
        slope, _, _, _, _ = linregress(x, serie)
        return slope * 100
    df['Pendiente'] = df['close'].rolling(window=20).apply(calcular_pendiente, raw=False)
    
    if len(df) < max(periodo_adx, periodo_volatilidad) + 5:
        return None
    
    ultima = df.iloc[-1]
    anterior = df.iloc[-2]
    
    # --- VALIDACIÓN EUR/USD INTRADAY OPTIMIZADA ---
    if all([df_m5 is not None, df_m15 is not None, df_h1 is not None, df_h4 is not None, df_d1 is not None]):
        # Usar las nuevas utilidades optimizadas para EUR/USD
        entrada_valida, tendencia = validar_entrada_eurusd_intraday(
            df_m5, df_m15, df_h1, df_h4, df_d1, debug=debug
        )
        
        if not entrada_valida:
            if debug: print(f"❌ Entrada no validada: {tendencia}")
            return None
        
        # Si la entrada es válida, proceder con la lógica de señales
        if debug: print(f"✅ Entrada validada para {tendencia.upper()}")
        
        # Aplicar filtros específicos según la tendencia
        if tendencia == 'alcista':
            # Condiciones de compra optimizadas para EUR/USD
            condiciones_compra = [
                ultima['EMA_rapida'] > ultima['EMA_lenta'],
                ultima['ADX'] >= 30,  # ADX mínimo más estricto
                ultima['Pendiente'] > 0.05,
                ultima['RSI'] <= 35,  # RSI más extremo para entrada
                ultima['Vol_Relativo'] >= 1.5,  # Volumen mínimo más alto
                not hay_posicion_abierta(SYMBOL, 'BUY')
            ]
            
            if sum(condiciones_compra) >= 5:  # Necesitamos más condiciones cumplidas
                if debug: print(f"🚀 Señal COMPRA EUR/USD: {condiciones_compra}")
                # Calcular lote dinámico
                try:
                    balance = mt5.account_info().balance
                    lote_optimo = calcular_lote_dinamico_eurusd(balance, 1.5, 16)  # 1.5% riesgo, 16 pips SL
                    if debug: print(f"💰 Lote óptimo: {lote_optimo}")
                except:
                    lote_optimo = 0.1  # Lote por defecto
                
                return ('BUY', ultima['close'], 1.0, lote_optimo)
        
        elif tendencia == 'bajista':
            # Condiciones de venta optimizadas para EUR/USD
            condiciones_venta = [
                ultima['EMA_rapida'] < ultima['EMA_lenta'],
                ultima['ADX'] >= 30,  # ADX mínimo más estricto
                ultima['Pendiente'] < -0.05,
                ultima['RSI'] >= 65,  # RSI más extremo para entrada
                ultima['Vol_Relativo'] >= 1.5,  # Volumen mínimo más alto
                not hay_posicion_abierta(SYMBOL, 'SELL')
            ]
            
            if sum(condiciones_venta) >= 5:  # Necesitamos más condiciones cumplidas
                if debug: print(f"📉 Señal VENTA EUR/USD: {condiciones_venta}")
                # Calcular lote dinámico
                try:
                    balance = mt5.account_info().balance
                    lote_optimo = calcular_lote_dinamico_eurusd(balance, 1.5, 16)  # 1.5% riesgo, 16 pips SL
                    if debug: print(f"💰 Lote óptimo: {lote_optimo}")
                except:
                    lote_optimo = 0.1  # Lote por defecto
                
                return ('SELL', ultima['close'], 1.0, lote_optimo)
    
    # --- LÓGICA LEGACY (mantener para compatibilidad) ---
    # ... existing code ...
    
    # Filtros mejorados
    mercado_trending = es_mercado_trending(df)
    horario_volatil = es_horario_volatil()
    
    # Ajustar filtros según condiciones de mercado
    adx_min = 25 if mercado_trending else 20
    volumen_min = 1.2 if horario_volatil else 1.1
    
    # Condiciones de compra mejoradas
    tendencia_alcista = (
        ultima['EMA_rapida'] > ultima['EMA_lenta'] and
        ultima['ADX'] > adx_min and
        ultima['Pendiente'] > 0.05
    )
    rsi_compra = (anterior['RSI'] < 40 and ultima['RSI'] > anterior['RSI'])
    volumen_compra = ultima['Vol_Relativo'] > volumen_min
    vela_compra = (
        (ultima['close'] > ultima['open'] and ultima['close'] > anterior['close']) or
        (ultima['close'] > ultima['EMA_rapida'])
    )
    condiciones_compra = [tendencia_alcista, rsi_compra, volumen_compra, vela_compra]
    
    # Condiciones de venta mejoradas
    tendencia_bajista = (
        ultima['EMA_rapida'] < ultima['EMA_lenta'] and
        ultima['ADX'] > adx_min and
        ultima['Pendiente'] < -0.05
    )
    rsi_venta = (anterior['RSI'] > 60 and ultima['RSI'] < anterior['RSI'])
    volumen_venta = ultima['Vol_Relativo'] > volumen_min
    vela_venta = (
        (ultima['close'] < ultima['open'] and ultima['close'] < anterior['close']) or
        (ultima['close'] < ultima['EMA_rapida'])
    )
    condiciones_venta = [tendencia_bajista, rsi_venta, volumen_venta, vela_venta]
    
    # Gestión de riesgo dinámica
    factor_riesgo = max(0.5, min(2.0, 1.0 / (ultima['Volatilidad'] / 0.5)))
    
    # --- CONFLUENCIA DE 4 TIMEFRAMES ---
    if all([df_m5 is not None, df_m15 is not None, df_h1 is not None, df_h4 is not None, df_d1 is not None]):
        # Obtener tendencias de todos los timeframes
        tendencia_d1 = tendencia_ema(df_d1)
        tendencia_h4 = tendencia_ema(df_h4)
        tendencia_h1 = tendencia_ema(df_h1)
        tendencia_m15 = tendencia_ema(df_m15)
        tendencia_m5 = tendencia_ema(df_m5)
        
        # Confluencia completa: D1 + H4 alineados, M15 confirma, M5 timing
        if (sum(condiciones_compra) >= 3 and 
            tendencia_d1 == 'alcista' and 
            tendencia_h4 == 'alcista' and
            tendencia_m15 == 'alcista' and
            not hay_posicion_abierta(SYMBOL, 'BUY')):
            
            if debug:
                print(f"Señal COMPRA con confluencia 4TF: {condiciones_compra}")
                print(f"Tendencias: D1={tendencia_d1}, H4={tendencia_h4}, H1={tendencia_h1}, M15={tendencia_m15}, M5={tendencia_m5}")
            return ('BUY', ultima['close'], factor_riesgo)
        
        if (sum(condiciones_venta) >= 3 and 
            tendencia_d1 == 'bajista' and 
            tendencia_h4 == 'bajista' and
            tendencia_m15 == 'bajista' and
            not hay_posicion_abierta(SYMBOL, 'SELL')):
            
            if debug:
                print(f"Señal VENTA con confluencia 4TF: {condiciones_venta}")
                print(f"Tendencias: D1={tendencia_d1}, H4={tendencia_h4}, H1={tendencia_h1}, M15={tendencia_m15}, M5={tendencia_m5}")
            return ('SELL', ultima['close'], factor_riesgo)
        
        if debug:
            print(f"No señal por confluencia 4TF. Compra: {condiciones_compra}, Venta: {condiciones_venta}")
            print(f"Tendencias: D1={tendencia_d1}, H4={tendencia_h4}, H1={tendencia_h1}, M15={tendencia_m15}, M5={tendencia_m5}")
        return None
    
    # --- CONFLUENCIA FLEXIBLE (3 timeframes) ---
    elif all([df_h1 is not None, df_h4 is not None, df_d1 is not None]):
        tendencia_h1 = tendencia_ema(df_h1)
        tendencia_h4 = tendencia_ema(df_h4)
        tendencia_d1 = tendencia_ema(df_d1)
        
        # Confluencia flexible: al menos 2 de 3 timeframes alineados
        tendencias_alcistas = sum([tendencia_h1 == 'alcista', tendencia_h4 == 'alcista', tendencia_d1 == 'alcista'])
        tendencias_bajistas = sum([tendencia_h1 == 'bajista', tendencia_h4 == 'bajista', tendencia_d1 == 'bajista'])
        
        # Señal de compra con confluencia flexible
        if (sum(condiciones_compra) >= 3 and 
            tendencias_alcistas >= 2 and 
            not hay_posicion_abierta(SYMBOL, 'BUY')):
            if debug:
                print(f"Señal COMPRA con confluencia flexible: {condiciones_compra}, H1/H4/D1: {tendencia_h1}/{tendencia_h4}/{tendencia_d1}")
            return ('BUY', ultima['close'], factor_riesgo)
        
        # Señal de venta con confluencia flexible
        if (sum(condiciones_venta) >= 3 and 
            tendencias_bajistas >= 2 and 
            not hay_posicion_abierta(SYMBOL, 'SELL')):
            if debug:
                print(f"Señal VENTA con confluencia flexible: {condiciones_venta}, H1/H4/D1: {tendencia_h1}/{tendencia_h4}/{tendencia_d1}")
            return ('SELL', ultima['close'], factor_riesgo)
        
        if debug:
            print(f"No señal por confluencia flexible. Compra: {condiciones_compra}, Venta: {condiciones_venta}, H1/H4/D1: {tendencia_h1}/{tendencia_h4}/{tendencia_d1}")
        return None
    
    # --- Lógica local sin confluencia ---
    # Señal de compra
    if (sum(condiciones_compra) >= 3 and 
        not hay_posicion_abierta(SYMBOL, 'BUY')):
        if debug:
            print(f"Señal COMPRA local: {condiciones_compra}")
        return ('BUY', ultima['close'], factor_riesgo)
    
    # Señal de venta
    if (sum(condiciones_venta) >= 3 and 
        not hay_posicion_abierta(SYMBOL, 'SELL')):
        if debug:
            print(f"Señal VENTA local: {condiciones_venta}")
        return ('SELL', ultima['close'], factor_riesgo)
    
    if debug:
        print(f"No señal. Compra: {condiciones_compra}, Venta: {condiciones_venta}")
    return None 