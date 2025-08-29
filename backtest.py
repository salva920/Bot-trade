from broker.mt5_connector import conectar_mt5, obtener_datos
from strategy.interbank import detectar_entrada
from config import SYMBOL, LOT, SL_PIPS, TP_PIPS
import MetaTrader5 as mt5
import pandas as pd


def backtest(timeframe=mt5.TIMEFRAME_M30, n=2000):
    print(f"Iniciando backtesting... Timeframe: {timeframe}, Velas: {n}")
    if not conectar_mt5():
        print("Error conectando a MT5")
        return

    # Obtén más datos históricos para el backtest
    df = obtener_datos(timeframe=timeframe, n=n)
    if df.empty:
        print("No se pudieron obtener datos históricos.")
        return

    operaciones = []
    balance = 0
    for i in range(51, len(df)):
        sub_df = df.iloc[:i].copy()
        señal = detectar_entrada(sub_df)
        if señal:
            # Compatibilidad con factor_riesgo
            if len(señal) == 3:
                tipo, precio, _ = señal
            else:
                tipo, precio = señal
            # Simula la operación
            if tipo == 'BUY':
                sl = precio - SL_PIPS * 0.0001
                tp = precio + TP_PIPS * 0.0001
                precio_salida = df.iloc[i]['close']
                if precio_salida <= sl:
                    resultado = -SL_PIPS * LOT * 10
                elif precio_salida >= tp:
                    resultado = TP_PIPS * LOT * 10
                else:
                    resultado = (precio_salida - precio) * 10000 * LOT
            else:
                sl = precio + SL_PIPS * 0.0001
                tp = precio - TP_PIPS * 0.0001
                precio_salida = df.iloc[i]['close']
                if precio_salida >= sl:
                    resultado = -SL_PIPS * LOT * 10
                elif precio_salida <= tp:
                    resultado = TP_PIPS * LOT * 10
                else:
                    resultado = (precio - precio_salida) * 10000 * LOT
            balance += resultado
            operaciones.append(resultado)
    
    print(f"Total operaciones: {len(operaciones)}")
    print(f"Balance final: {balance:.2f} USD")
    if operaciones:
        print(f"Operaciones ganadoras: {sum(1 for x in operaciones if x > 0)}")
        print(f"Operaciones perdedoras: {sum(1 for x in operaciones if x < 0)}")
        print(f"Mejor trade: {max(operaciones):.2f} USD")
        print(f"Peor trade: {min(operaciones):.2f} USD")
        print(f"Promedio por trade: {sum(operaciones)/len(operaciones):.2f} USD")

if __name__ == "__main__":
    # Puedes probar diferentes timeframes aquí:
    for tf, nombre in [(mt5.TIMEFRAME_M30, 'M30'), (mt5.TIMEFRAME_H4, 'H4')]:
        print(f"\n--- Backtest en {nombre} ---")
        backtest(timeframe=tf, n=2000) 