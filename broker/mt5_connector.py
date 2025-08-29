import MetaTrader5 as mt5
import pandas as pd
from config import SYMBOL, LOT, SL_PIPS, TP_PIPS

def conectar_mt5():
    return mt5.initialize()

def obtener_datos(timeframe=mt5.TIMEFRAME_H1, n=100):
    rates = mt5.copy_rates_from_pos(SYMBOL, timeframe, 0, n)
    return pd.DataFrame(rates)

def _trading_permitido():
    term = mt5.terminal_info()
    acc = mt5.account_info()
    if term is None or acc is None:
        print("No se pudo obtener info de terminal/cuenta.")
        return False
    if not term.trade_allowed:
        print("Trading algorítmico deshabilitado en el terminal (AutoTrading).")
        return False
    if not acc.trade_allowed:
        print("Trading deshabilitado para la cuenta actual.")
        return False
    return True

def _calcular_sl_tp_dinamico(tipo, precio_entrada, atr_multiplier=1.5, rr_ratio=2.0):
    """Calcula SL y TP dinámicos basados en ATR"""
    # Obtener ATR actual
    df = obtener_datos(n=20)
    if df.empty:
        # Fallback a valores fijos
        point = mt5.symbol_info(SYMBOL).point
        sl = precio_entrada - (SL_PIPS * point) if tipo == 'BUY' else precio_entrada + (SL_PIPS * point)
        tp = precio_entrada + (TP_PIPS * point) if tipo == 'BUY' else precio_entrada - (TP_PIPS * point)
        return sl, tp
    
    # Calcular ATR
    df['TR'] = pd.concat([
        df['high'] - df['low'],
        abs(df['high'] - df['close'].shift()),
        abs(df['low'] - df['close'].shift())
    ], axis=1).max(axis=1)
    atr = df['TR'].rolling(window=14).mean().iloc[-1]
    
    # SL basado en ATR
    sl_distance = atr * atr_multiplier
    if tipo == 'BUY':
        sl = precio_entrada - sl_distance
        tp = precio_entrada + (sl_distance * rr_ratio)
    else:
        sl = precio_entrada + sl_distance
        tp = precio_entrada - (sl_distance * rr_ratio)
    
    return sl, tp

def enviar_orden(tipo, precio_entrada, factor_riesgo=1.0):
    """
    Envía una orden al mercado con gestión de riesgo dinámica
    tipo: 'BUY' o 'SELL'
    precio_entrada: precio de entrada
    factor_riesgo: multiplicador de tamaño de posición (0.5-2.0)
    """
    if not _trading_permitido():
        return False

    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print(f"Error: No se encontró el símbolo {SYMBOL}")
        return False

    # Ajustar tamaño de posición según factor de riesgo
    lote_ajustado = LOT * factor_riesgo
    
    # Calcular SL y TP dinámicos
    sl, tp = _calcular_sl_tp_dinamico(tipo, precio_entrada)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lote_ajustado,
        "type": mt5.ORDER_TYPE_BUY if tipo == 'BUY' else mt5.ORDER_TYPE_SELL,
        "price": precio_entrada,
        "sl": sl,
        "tp": tp,
        "deviation": 40,
        "magic": 234000,
        "comment": f"python script - factor:{factor_riesgo:.2f}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK if symbol_info.trade_fill_mode == mt5.SYMBOL_FILLING_FOK else mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result is None:
        print("order_send devolvió None")
        return False
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Error al enviar orden: {result.comment}")
        return False
    
    print(f"Orden ejecutada: {tipo} {SYMBOL} a {precio_entrada}, Lote: {lote_ajustado:.2f}, SL: {sl:.5f}, TP: {tp:.5f}")
    return True 