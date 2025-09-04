"""
Utilidades específicas para trading EUR/USD intraday
Optimizadas para objetivo 1-2% (12-20 pips)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from config import (
    ATR_MIN_PIPS, ATR_MAX_PIPS, ADX_MIN, VOLUME_MIN,
    RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, HORARIOS_OPTIMOS
)


def es_volatilidad_optima_eurusd(df, pips_objetivo=16):
    """
    Verifica si la volatilidad es óptima para el objetivo de pips EUR/USD
    """
    if 'ATR' not in df.columns or df.empty:
        return False
    
    atr_actual = df['ATR'].iloc[-1]
    precio_actual = df['close'].iloc[-1]
    
    # Convertir ATR a pips (1 pip EUR/USD = 0.0001)
    atr_pips = atr_actual * 10000
    
    # Para 16 pips objetivo, necesitamos ATR entre 8-20 pips
    return ATR_MIN_PIPS <= atr_pips <= ATR_MAX_PIPS


def es_horario_optimo_eurusd():
    """
    Verifica si estamos en un horario óptimo para EUR/USD intraday
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


def timing_entrada_optimo_eurusd(df_m5, df_m1=None):
    """
    Verifica timing óptimo para entrada EUR/USD intraday
    """
    if df_m5.empty or len(df_m5) < 2:
        return False
    
    ultima = df_m5.iloc[-1]
    anterior = df_m5.iloc[-2]
    
    # Verificar que tenemos ATR calculado
    if 'ATR' not in df_m5.columns:
        return False
    
    # Patrones de velas específicos para EUR/USD
    vela_fuerte = abs(ultima['close'] - ultima['open']) > (ultima['ATR'] * 0.6)
    momentum = abs(ultima['close'] - anterior['close']) > (ultima['ATR'] * 0.3)
    
    # Verificar que no estamos en el final de una tendencia
    rsi_no_sobrecompra = ultima['RSI'] < 75
    rsi_no_sobreventa = ultima['RSI'] > 25
    
    # Verificar que la vela actual tiene dirección clara
    direccion_clara = (
        (ultima['close'] > ultima['open'] and ultima['close'] > anterior['close']) or
        (ultima['close'] < ultima['open'] and ultima['close'] < anterior['close'])
    )
    
    return vela_fuerte and momentum and rsi_no_sobrecompra and rsi_no_sobreventa and direccion_clara


def filtros_estrictos_intraday(df):
    """
    Aplica filtros estrictos para trading intraday EUR/USD
    """
    if df.empty or len(df) < 20:
        return False
    
    ultima = df.iloc[-1]
    
    # Filtros básicos
    if 'ADX' not in df.columns or 'Vol_Relativo' not in df.columns:
        return False
    
    # ADX mínimo para tendencia clara
    adx_suficiente = ultima['ADX'] >= ADX_MIN
    
    # Volumen mínimo para confirmación
    volumen_suficiente = ultima['Vol_Relativo'] >= VOLUME_MIN
    
    # RSI en rango óptimo para entrada
    rsi_optimo = (
        (ultima['RSI'] <= RSI_ENTRADA_COMPRA) or  # Para compras
        (ultima['RSI'] >= RSI_ENTRADA_VENTA)      # Para ventas
    )
    
    # Pendiente de tendencia mínima
    pendiente_suficiente = abs(ultima.get('Pendiente', 0)) > 0.05
    
    return adx_suficiente and volumen_suficiente and rsi_optimo and pendiente_suficiente


def calcular_lote_dinamico_eurusd(balance, riesgo_porcentaje, sl_pips):
    """
    Calcula lote óptimo para riesgo objetivo en EUR/USD
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


def confirmar_tendencia_multiple_timeframe(df_m5, df_m15, df_h1, df_h4, df_d1):
    """
    Confirma tendencia en múltiples timeframes para EUR/USD
    """
    def tendencia_ema_simple(df):
        if df.empty or len(df) < 50:
            return 'neutral'
        
        ema_rapida = df['close'].ewm(span=20, adjust=False).mean()
        ema_lenta = df['close'].ewm(span=50, adjust=False).mean()
        
        if ema_rapida.iloc[-1] > ema_lenta.iloc[-1]:
            return 'alcista'
        elif ema_rapida.iloc[-1] < ema_lenta.iloc[-1]:
            return 'bajista'
        else:
            return 'neutral'
    
    # Obtener tendencias de todos los timeframes
    tendencias = {
        'D1': tendencia_ema_simple(df_d1),
        'H4': tendencia_ema_simple(df_h4),
        'H1': tendencia_ema_simple(df_h1),
        'M15': tendencia_ema_simple(df_m15),
        'M5': tendencia_ema_simple(df_m5)
    }
    
    # Contar tendencias alcistas y bajistas
    alcistas = sum(1 for t in tendencias.values() if t == 'alcista')
    bajistas = sum(1 for t in tendencias.values() if t == 'bajista')
    
    # Para confluencia fuerte, necesitamos al menos 4 de 5 timeframes alineados
    if alcistas >= 4:
        return 'alcista', tendencias
    elif bajistas >= 4:
        return 'bajista', tendencias
    else:
        return 'neutral', tendencias


def validar_entrada_eurusd_intraday(df_m5, df_m15, df_h1, df_h4, df_d1, debug=False):
    """
    Valida entrada completa para EUR/USD intraday
    """
    # 1. Verificar horario óptimo
    if not es_horario_optimo_eurusd():
        if debug: print("❌ Fuera de horario óptimo EUR/USD")
        return False, "Horario no óptimo"
    
    # 2. Verificar volatilidad óptima
    if not es_volatilidad_optima_eurusd(df_m5, 16):
        if debug: print("❌ Volatilidad no óptima para objetivo")
        return False, "Volatilidad no óptima"
    
    # 3. Verificar timing de entrada
    if not timing_entrada_optimo_eurusd(df_m5):
        if debug: print("❌ Timing de entrada no óptimo")
        return False, "Timing no óptimo"
    
    # 4. Aplicar filtros estrictos
    if not filtros_estrictos_intraday(df_m5):
        if debug: print("❌ Filtros estrictos no cumplidos")
        return False, "Filtros no cumplidos"
    
    # 5. Confirmar tendencia múltiple timeframe
    tendencia, detalles = confirmar_tendencia_multiple_timeframe(df_m5, df_m15, df_h1, df_h4, df_d1)
    
    if tendencia == 'neutral':
        if debug: print("❌ Sin tendencia clara en múltiples timeframes")
        return False, "Sin tendencia clara"
    
    if debug:
        print(f"✅ Entrada validada: {tendencia.upper()}")
        print(f"📊 Tendencias: {detalles}")
    
    return True, tendencia
