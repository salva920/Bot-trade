import MetaTrader5 as mt5
import pandas as pd
from config import SYMBOL, LOT, SL_PIPS, TP_PIPS, RISK_REWARD

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

def _calcular_sl_tp_eurusd_intraday(tipo, precio_entrada):
    """
    Calcula SL y TP optimizados para EUR/USD intraday
    Usando la nueva configuración: SL=16 pips, TP=24 pips (1.5:1)
    """
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print(f"Error: No se encontró el símbolo {SYMBOL}")
        return None, None
    
    point = symbol_info.point
    
    # SL y TP fijos según configuración optimizada
    if tipo == 'BUY':
        sl = precio_entrada - (SL_PIPS * point)
        tp = precio_entrada + (TP_PIPS * point)
    else:  # SELL
        sl = precio_entrada + (SL_PIPS * point)
        tp = precio_entrada - (TP_PIPS * point)
    
    return sl, tp

def enviar_orden(tipo, precio_entrada, factor_riesgo=1.0, lote_personalizado=None):
    """
    Envía una orden al mercado optimizada para EUR/USD intraday
    tipo: 'BUY' o 'SELL'
    precio_entrada: precio de entrada
    factor_riesgo: multiplicador de tamaño de posición (0.5-2.0)
    lote_personalizado: lote calculado dinámicamente (opcional)
    """
    if not _trading_permitido():
        return False

    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print(f"Error: No se encontró el símbolo {SYMBOL}")
        return False

    # Usar lote personalizado si está disponible, sino calcular
    if lote_personalizado is not None:
        lote_final = lote_personalizado
        print(f"💰 Usando lote calculado dinámicamente: {lote_final}")
    else:
        # Ajustar tamaño de posición según factor de riesgo
        lote_final = LOT * factor_riesgo
        print(f"💰 Usando lote por defecto ajustado: {lote_final}")
    
    # Calcular SL y TP optimizados para EUR/USD intraday
    sl, tp = _calcular_sl_tp_eurusd_intraday(tipo, precio_entrada)
    
    if sl is None or tp is None:
        print("❌ Error calculando SL/TP")
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lote_final,
        "type": mt5.ORDER_TYPE_BUY if tipo == 'BUY' else mt5.ORDER_TYPE_SELL,
        "price": precio_entrada,
        "sl": sl,
        "tp": tp,
        "deviation": 40,
        "magic": 234000,
        "comment": f"EUR/USD Intraday - Lote:{lote_final:.2f}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  # Usar FOK para mejor compatibilidad
    }

    result = mt5.order_send(request)
    if result is None:
        print("❌ order_send devolvió None")
        return False
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Error al enviar orden: {result.comment}")
        return False
    
    print(f"✅ Orden ejecutada: {tipo} {SYMBOL} a {precio_entrada}")
    print(f"💰 Lote: {lote_final:.2f}")
    print(f"🛑 Stop Loss: {sl:.5f} ({SL_PIPS} pips)")
    print(f"🎯 Take Profit: {tp:.5f} ({TP_PIPS} pips)")
    print(f"📊 Ratio R/R: {RISK_REWARD}:1")
    
    return True 