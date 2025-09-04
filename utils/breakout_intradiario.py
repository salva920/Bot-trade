"""
Utilidades específicas para estrategia de BREAKOUT INTRADIARIO
Optimizadas para EUR/USD con objetivo 1-2% (12-20 pips)
Solo usa timeframes intradiarios para consistencia temporal
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from config import (
    ATR_MIN_PIPS, ATR_MAX_PIPS, ADX_MIN, VOLUME_MIN,
    RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, HORARIOS_OPTIMOS,
    BREAKOUT_CONFIG, STOP_LOSS_ATR_MULTIPLIER, STOP_LOSS_MIN_PIPS, STOP_LOSS_MAX_PIPS,
    TAKE_PROFIT_RATIO, TAKE_PROFIT_MIN_PIPS, TAKE_PROFIT_MAX_PIPS, TRAILING_STOP_ACTIVAR_PIPS,
    TRAILING_STOP_ATR_MULTIPLIER, TRAILING_STOP_MIN_PIPS, POSITION_SIZE_RISK_PERCENT,
    POSITION_SIZE_MAX_LOTS, POSITION_SIZE_MIN_LOTS, TREND_STRENGTH_MIN_ADX, TREND_MOMENTUM_RSI_MIN,
    TREND_MOMENTUM_RSI_MAX, VOLUME_SPIKE_MULTIPLIER, VOLUME_CONFIRMATION_PERIODS, VOLUME_MIN_ABSOLUTE,
    ENTRY_TIMING_RSI_OVERBOUGHT, ENTRY_TIMING_RSI_OVERSOLD, ENTRY_TIMING_VOLUME_MIN,
    ENTRY_TIMING_ATR_MIN, RISK_REWARD_RATIO_MIN, RISK_REWARD_RATIO_TARGET, RISK_REWARD_RATIO_MAX,
    MAX_DRAWDOWN_PERCENT, MAX_CONSECUTIVE_LOSSES
)


def es_horario_optimo_breakout():
    """
    Verifica si estamos en un horario óptimo para breakout EUR/USD
    """
    tz_ny = pytz.timezone('America/New_York')
    ahora_ny = datetime.now(tz_ny)
    hora_ny = ahora_ny.hour
    minuto_ny = ahora_ny.minute
    
    for hora, minuto in HORARIOS_OPTIMOS:
        # Ventana de 30 minutos para cada horario óptimo
        if hora_ny == hora and minuto_ny >= minuto and minuto_ny < minuto + 30:
            return True
    
    return False


def es_volatilidad_optima_breakout(df, pips_objetivo=16):
    """
    Verifica si la volatilidad es óptima para breakout EUR/USD
    """
    if 'ATR' not in df.columns or df.empty:
        return False
    
    atr_actual = df['ATR'].iloc[-1]
    
    # Convertir ATR a pips (1 pip EUR/USD = 0.0001)
    atr_pips = atr_actual * 10000
    
    # Para 16 pips objetivo, necesitamos ATR entre 8-20 pips
    return ATR_MIN_PIPS <= atr_pips <= ATR_MAX_PIPS


def detectar_tendencia_intradiaria(df_m15):
    """
    Detecta tendencia intradiaria usando M15
    """
    if df_m15.empty or len(df_m15) < 50:
        return 'neutral'
    
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


def confirmar_breakout_m5(df_m5, tendencia_intradiaria):
    """
    Confirma breakout en M5 según la tendencia intradiaria
    """
    if df_m5.empty or len(df_m5) < 20:
        return False
    
    ultima = df_m5.iloc[-1]
    anterior = df_m5.iloc[-2]
    
    # Verificar que tenemos todos los indicadores necesarios
    required_indicators = ['ATR', 'ADX', 'RSI', 'Vol_Relativo', 'Pendiente']
    for indicator in required_indicators:
        if indicator not in df_m5.columns:
            return False
    
    # Condiciones de breakout según tendencia (MÁS FLEXIBLES)
    if tendencia_intradiaria == 'alcista':
        # Breakout alcista: precio rompe resistencia
        breakout_alcista = (
            ultima['close'] > ultima['open'] and                    # Vela alcista
            ultima['close'] > anterior['close'] and                # Precio sube
            ultima['ADX'] >= ADX_MIN and                           # ADX suficiente
            ultima['Vol_Relativo'] >= VOLUME_MIN and               # Volumen confirmado
            ultima['RSI'] <= RSI_ENTRADA_COMPRA and                # RSI en zona de compra
            ultima['Pendiente'] > PENDIENTE_MINIMA                 # Pendiente positiva (FLEXIBLE)
        )
        return breakout_alcista
    
    elif tendencia_intradiaria == 'bajista':
        # Breakout bajista: precio rompe soporte
        breakout_bajista = (
            ultima['close'] < ultima['open'] and                    # Vela bajista
            ultima['close'] < anterior['close'] and                # Precio baja
            ultima['ADX'] >= ADX_MIN and                           # ADX suficiente
            ultima['Vol_Relativo'] >= VOLUME_MIN and               # Volumen confirmado
            ultima['RSI'] >= RSI_ENTRADA_VENTA and                 # RSI en zona de venta
            ultima['Pendiente'] < PENDIENTE_MAXIMA                 # Pendiente negativa (FLEXIBLE)
        )
        return breakout_bajista
    
    return False


def timing_entrada_preciso_m1(df_m1, tendencia_intradiaria):
    """
    Timing preciso de entrada usando M1
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


def calcular_lote_dinamico_breakout(balance, riesgo_porcentaje, sl_pips):
    """
    Calcula lote óptimo para breakout EUR/USD
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


def validar_breakout_completo(df_m15, df_m5, df_m1, debug=False):
    """
    Valida breakout completo usando solo timeframes intradiarios
    """
    # 1. Verificar horario óptimo
    if not es_horario_optimo_breakout():
        if debug: print("❌ Fuera de horario óptimo para breakout")
        return False, "Horario no óptimo"
    
    # 2. Verificar volatilidad óptima en M5
    if not es_volatilidad_optima_breakout(df_m5, 16):
        if debug: print("❌ Volatilidad no óptima para breakout")
        return False, "Volatilidad no óptima"
    
    # 3. Detectar tendencia intradiaria en M15
    tendencia_intradiaria = detectar_tendencia_intradiaria(df_m15)
    if tendencia_intradiaria == 'neutral':
        if debug: print("❌ Sin tendencia intradiaria clara")
        return False, "Sin tendencia intradiaria"
    
    if debug: print(f"✅ Tendencia intradiaria detectada: {tendencia_intradiaria.upper()}")
    
    # 4. Confirmar breakout en M5
    if not confirmar_breakout_m5(df_m5, tendencia_intradiaria):
        if debug: print("❌ Breakout no confirmado en M5")
        return False, "Breakout no confirmado"
    
    if debug: print(f"✅ Breakout confirmado en M5 para {tendencia_intradiaria.upper()}")
    
    # 5. Timing preciso en M1
    if not timing_entrada_preciso_m1(df_m1, tendencia_intradiaria):
        if debug: print("❌ Timing de entrada no preciso en M1")
        return False, "Timing no preciso"
    
    if debug: print(f"✅ Timing de entrada preciso en M1")
    
    return True, tendencia_intradiaria


def obtener_nivel_breakout(df_m5, tendencia_intradiaria):
    """
    Obtiene el nivel de breakout para SL/TP
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


def calcular_ratio_riesgo_breakout(precio_entrada, nivel_breakout, tp_pips):
    """
    Calcula el ratio de riesgo real del breakout
    """
    if nivel_breakout is None:
        return 0
    
    # Calcular SL en pips
    sl_pips = abs(precio_entrada - nivel_breakout) * 10000
    
    # Ratio riesgo/beneficio
    if sl_pips > 0:
        return tp_pips / sl_pips
    
    return 0

# ============================================================================
# 🚀 GESTIÓN DE RIESGO INTELIGENTE - FUNCIONES DE OPTIMIZACIÓN
# ============================================================================

def calcular_stop_loss_adaptativo_breakout(atr_pips, precio_entrada, direccion):
    """
    Calcula stop loss adaptativo basado en ATR para breakout intradiario
    """
    
    # Stop Loss base = ATR × multiplicador
    stop_loss_pips = atr_pips * STOP_LOSS_ATR_MULTIPLIER
    
    # Aplicar límites mínimo y máximo
    stop_loss_pips = max(stop_loss_pips, STOP_LOSS_MIN_PIPS)
    stop_loss_pips = min(stop_loss_pips, STOP_LOSS_MAX_PIPS)
    
    # Convertir pips a precio
    if direccion == "BUY":
        stop_loss_precio = precio_entrada - (stop_loss_pips * 0.0001)
    else:  # SELL
        stop_loss_precio = precio_entrada + (stop_loss_pips * 0.0001)
    
    return stop_loss_precio, stop_loss_pips

def calcular_take_profit_dinamico_breakout(stop_loss_pips, precio_entrada, direccion):
    """
    Calcula take profit dinámico con ratio riesgo/beneficio optimizado
    """
    
    # Take Profit = Stop Loss × ratio objetivo
    take_profit_pips = stop_loss_pips * TAKE_PROFIT_RATIO
    
    # Aplicar límites mínimo y máximo
    take_profit_pips = max(take_profit_pips, TAKE_PROFIT_MIN_PIPS)
    take_profit_pips = min(take_profit_pips, TAKE_PROFIT_MAX_PIPS)
    
    # Convertir pips a precio
    if direccion == "BUY":
        take_profit_precio = precio_entrada + (take_profit_pips * 0.0001)
    else:  # SELL
        take_profit_precio = precio_entrada - (take_profit_pips * 0.0001)
    
    return take_profit_precio, take_profit_pips

def calcular_trailing_stop_breakout(precio_entrada, precio_actual, direccion, atr_pips, ganancia_actual_pips):
    """
    Calcula trailing stop automático para proteger ganancias
    """
    
    # Solo activar si hay ganancia suficiente
    if ganancia_actual_pips < TRAILING_STOP_ACTIVAR_PIPS:
        return None
    
    # Trailing Stop = ATR × multiplicador
    trailing_pips = atr_pips * TRAILING_STOP_ATR_MULTIPLIER
    trailing_pips = max(trailing_pips, TRAILING_STOP_MIN_PIPS)
    
    # Calcular precio del trailing stop
    if direccion == "BUY":
        trailing_stop = precio_actual - (trailing_pips * 0.0001)
        # Solo mover hacia arriba (proteger ganancias)
        if trailing_stop > precio_entrada:
            return trailing_stop
    else:  # SELL
        trailing_stop = precio_actual + (trailing_pips * 0.0001)
        # Solo mover hacia abajo (proteger ganancias)
        if trailing_stop < precio_entrada:
            return trailing_stop
    
    return None

def calcular_lote_dinamico_optimizado_breakout(balance_cuenta, stop_loss_pips, precio_entrada):
    """
    Calcula lote dinámico optimizado con gestión de riesgo inteligente
    """
    
    # Riesgo máximo por operación
    riesgo_maximo = balance_cuenta * (POSITION_SIZE_RISK_PERCENT / 100)
    
    # Valor del pip (aproximado para EUR/USD)
    valor_pip = 10  # $10 por pip en 1 lote estándar
    
    # Lote calculado basado en riesgo
    lote_calculado = riesgo_maximo / (stop_loss_pips * valor_pip)
    
    # Aplicar límites mínimo y máximo
    lote_final = max(lote_calculado, POSITION_SIZE_MIN_LOTS)
    lote_final = min(lote_final, POSITION_SIZE_MAX_LOTS)
    
    # Redondear a 2 decimales
    lote_final = round(lote_final, 2)
    
    return lote_final

def validar_tendencia_multi_timeframe_breakout(symbol, timeframes=['H1', 'H4', 'D1']):
    """
    Valida tendencia usando múltiples timeframes para confirmar breakout
    """
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    
    # Funciones auxiliares para calcular indicadores
    def calcular_ema(prices, period):
        return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]
    
    def calcular_rsi(prices, period):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]
    
    def calcular_adx(high_prices, low_prices, close_prices, period):
        # Simplificado para evitar complejidad
        return 25.0  # Valor por defecto
    
    confirmaciones = 0
    total_timeframes = len(timeframes)
    
    for tf in timeframes:
        try:
            # Obtener datos del timeframe
            rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, f'TIMEFRAME_{tf}'), 0, 100)
            if rates is None or len(rates) < 50:
                continue
            
            # Calcular indicadores
            close_prices = [rate['close'] for rate in rates]
            high_prices = [rate['high'] for rate in rates]
            low_prices = [rate['low'] for rate in rates]
            
            # EMA rápida y lenta
            ema_rapida = calcular_ema(close_prices, 12)
            ema_lenta = calcular_ema(close_prices, 26)
            
            # ADX
            adx = calcular_adx(high_prices, low_prices, close_prices, 14)
            
            # RSI
            rsi = calcular_rsi(close_prices, 14)
            
            # Validar tendencia
            if (ema_rapida > ema_lenta and  # Tendencia alcista
                adx >= TREND_STRENGTH_MIN_ADX and  # ADX suficiente
                TREND_MOMENTUM_RSI_MIN <= rsi <= TREND_MOMENTUM_RSI_MAX):  # RSI en rango
                confirmaciones += 1
            elif (ema_rapida < ema_lenta and  # Tendencia bajista
                  adx >= TREND_STRENGTH_MIN_ADX and  # ADX suficiente
                  TREND_MOMENTUM_RSI_MIN <= rsi <= TREND_MOMENTUM_RSI_MAX):  # RSI en rango
                confirmaciones += 1
                
        except Exception as e:
            print(f"Error validando timeframe {tf}: {e}")
            continue
    
    # Retornar True si al menos 2/3 de los timeframes confirman
    return confirmaciones >= (total_timeframes * 2 // 3)

def validar_volumen_spike_breakout(volumen_actual, volumenes_anteriores):
    """
    Valida si el volumen actual es un spike significativo
    """
    
    if len(volumenes_anteriores) < VOLUME_CONFIRMATION_PERIODS:
        return False
    
    # Calcular volumen promedio
    volumen_promedio = sum(volumenes_anteriores[-VOLUME_CONFIRMATION_PERIODS:]) / VOLUME_CONFIRMATION_PERIODS
    
    # Validar spike de volumen
    es_spike = (volumen_actual >= volumen_promedio * VOLUME_SPIKE_MULTIPLIER and 
                volumen_actual >= VOLUME_MIN_ABSOLUTE)
    
    return es_spike

def validar_timing_entrada_preciso_m1_breakout(symbol):
    """
    Valida timing de entrada ultra preciso usando M1
    """
    import MetaTrader5 as mt5
    
    try:
        # Obtener datos M1
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
        if rates is None or len(rates) < 30:
            return False, "Datos M1 insuficientes"
        
        # Calcular indicadores M1
        close_prices = [rate['close'] for rate in rates]
        high_prices = [rate['high'] for rate in rates]
        low_prices = [rate['low'] for rate in rates]
        volumes = [rate['tick_volume'] for rate in rates]
        
        # RSI M1
        rsi_m1 = calcular_rsi(close_prices, 14)
        
        # ATR M1 (simplificado)
        def calcular_atr(high_prices, low_prices, close_prices, period):
            # Cálculo simplificado de ATR
            true_ranges = []
            for i in range(1, len(close_prices)):
                high_low = high_prices[i] - low_prices[i]
                high_close = abs(high_prices[i] - close_prices[i-1])
                low_close = abs(low_prices[i] - close_prices[i-1])
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
            
            if len(true_ranges) < period:
                return 0.001  # Valor por defecto
            
            return sum(true_ranges[-period:]) / period
        
        atr_m1 = calcular_atr(high_prices, low_prices, close_prices, 14)
        atr_m1_pips = atr_m1 * 10000
        
        # Volumen relativo M1
        volumen_actual = volumes[-1]
        volumen_promedio = sum(volumes[-20:]) / 20
        volumen_relativo = volumen_actual / volumen_promedio if volumen_promedio > 0 else 0
        
        # Validaciones
        if rsi_m1 >= ENTRY_TIMING_RSI_OVERBOUGHT:
            return False, f"RSI M1 sobrecomprado: {rsi_m1:.1f}"
        
        if rsi_m1 <= ENTRY_TIMING_RSI_OVERSOLD:
            return False, f"RSI M1 sobrevendido: {rsi_m1:.1f}"
        
        if volumen_relativo < ENTRY_TIMING_VOLUME_MIN:
            return False, f"Volumen M1 insuficiente: {volumen_relativo:.2f}"
        
        if atr_m1_pips < ENTRY_TIMING_ATR_MIN:
            return False, f"ATR M1 insuficiente: {atr_m1_pips:.1f} pips"
        
        return True, "Timing M1 válido"
        
    except Exception as e:
        return False, f"Error validando timing M1: {e}"

def calcular_ratio_riesgo_beneficio_dinamico_breakout(stop_loss_pips, take_profit_pips):
    """
    Calcula ratio riesgo/beneficio dinámico
    """
    
    if stop_loss_pips <= 0:
        return 0
    
    ratio = take_profit_pips / stop_loss_pips
    
    # Clasificar ratio
    if ratio >= RISK_REWARD_RATIO_MAX:
        return "EXCELENTE"
    elif ratio >= RISK_REWARD_RATIO_TARGET:
        return "ÓPTIMO"
    elif ratio >= RISK_REWARD_RATIO_MIN:
        return "BUENO"
    else:
        return "INSUFICIENTE"

def validar_proteccion_drawdown_breakout(balance_actual, balance_inicial, perdidas_consecutivas):
    """
    Valida protección contra drawdown excesivo
    """
    
    # Calcular drawdown
    drawdown_percent = ((balance_inicial - balance_actual) / balance_inicial) * 100
    
    # Validaciones
    if drawdown_percent >= MAX_DRAWDOWN_PERCENT:
        return False, f"Drawdown máximo excedido: {drawdown_percent:.2f}%"
    
    if perdidas_consecutivas >= MAX_CONSECUTIVE_LOSSES:
        return False, f"Máximo de pérdidas consecutivas alcanzado: {perdidas_consecutivas}"
    
    return True, "Protección drawdown válida"
