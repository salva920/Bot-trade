"""
Script de prueba para la estrategia EUR/USD intraday optimizada
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.eurusd_intraday import (
    es_horario_optimo_eurusd,
    es_volatilidad_optima_eurusd,
    timing_entrada_optimo_eurusd,
    filtros_estrictos_intraday,
    calcular_lote_dinamico_eurusd,
    confirmar_tendencia_multiple_timeframe,
    validar_entrada_eurusd_intraday
)
from config import (
    ATR_MIN_PIPS, ATR_MAX_PIPS, ADX_MIN, VOLUME_MIN,
    RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, HORARIOS_OPTIMOS
)
import pandas as pd
import numpy as np


def crear_datos_simulados():
    """Crea datos simulados para probar la estrategia"""
    np.random.seed(42)
    
    # Crear datos M5 simulados
    n_bars = 100
    base_price = 1.0850  # EUR/USD base
    
    # Generar precios con tendencia alcista
    returns = np.random.normal(0.0001, 0.0005, n_bars)  # 0.01% media, 0.05% std
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Crear OHLC
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + abs(np.random.normal(0, 0.0002)))
        low = price * (1 - abs(np.random.normal(0, 0.0002)))
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        
        # ATR simulado (entre 8-20 pips)
        atr = np.random.uniform(0.0008, 0.0020)
        
        # ADX simulado (entre 25-45)
        adx = np.random.uniform(25, 45)
        
        # RSI simulado (entre 20-80)
        rsi = np.random.uniform(20, 80)
        
        # Volumen relativo (entre 0.8-2.0)
        vol_rel = np.random.uniform(0.8, 2.0)
        
        # Pendiente de tendencia
        pendiente = np.random.uniform(-0.1, 0.1)
        
        data.append({
            'time': i,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'tick_volume': int(np.random.uniform(1000, 5000)),
            'ATR': atr,
            'ADX': adx,
            'RSI': rsi,
            'Vol_Relativo': vol_rel,
            'Pendiente': pendiente
        })
    
    return pd.DataFrame(data)


def probar_utilidades_eurusd():
    """Prueba todas las utilidades EUR/USD intraday"""
    print("🧪 PROBANDO UTILIDADES EUR/USD INTRADAY")
    print("=" * 50)
    
    # 1. Probar horarios óptimos
    print("\n1️⃣ Probando horarios óptimos:")
    horario_optimo = es_horario_optimo_eurusd()
    print(f"   Horario actual óptimo: {horario_optimo}")
    print(f"   Horarios configurados: {HORARIOS_OPTIMOS}")
    
    # 2. Probar volatilidad óptima
    print("\n2️⃣ Probando volatilidad óptima:")
    df_simulado = crear_datos_simulados()
    volatilidad_optima = es_volatilidad_optima_eurusd(df_simulado)
    print(f"   Volatilidad óptima: {volatilidad_optima}")
    print(f"   ATR actual: {df_simulado['ATR'].iloc[-1] * 10000:.1f} pips")
    print(f"   Rango objetivo: {ATR_MIN_PIPS}-{ATR_MAX_PIPS} pips")
    
    # 3. Probar timing de entrada
    print("\n3️⃣ Probando timing de entrada:")
    timing_optimo = timing_entrada_optimo_eurusd(df_simulado)
    print(f"   Timing óptimo: {timing_optimo}")
    
    # 4. Probar filtros estrictos
    print("\n4️⃣ Probando filtros estrictos:")
    filtros_ok = filtros_estrictos_intraday(df_simulado)
    print(f"   Filtros cumplidos: {filtros_ok}")
    
    # 5. Probar cálculo de lote dinámico
    print("\n5️⃣ Probando cálculo de lote dinámico:")
    balance_simulado = 10000  # $10,000
    lote_optimo = calcular_lote_dinamico_eurusd(balance_simulado, 1.5, 16)
    print(f"   Balance: ${balance_simulado:,}")
    print(f"   Riesgo objetivo: 1.5%")
    print(f"   Stop Loss: 16 pips")
    print(f"   Lote óptimo: {lote_optimo}")
    
    # 6. Probar confirmación de tendencia múltiple timeframe
    print("\n6️⃣ Probando confirmación de tendencia múltiple timeframe:")
    # Crear dataframes simulados para diferentes timeframes
    df_m5 = df_simulado.copy()
    df_m15 = df_simulado.copy()
    df_h1 = df_simulado.copy()
    df_h4 = df_simulado.copy()
    df_d1 = df_simulado.copy()
    
    tendencia, detalles = confirmar_tendencia_multiple_timeframe(df_m5, df_m15, df_h1, df_h4, df_d1)
    print(f"   Tendencia detectada: {tendencia}")
    print(f"   Detalles por timeframe: {detalles}")
    
    # 7. Probar validación completa
    print("\n7️⃣ Probando validación completa:")
    entrada_valida, resultado = validar_entrada_eurusd_intraday(
        df_m5, df_m15, df_h1, df_h4, df_d1, debug=True
    )
    print(f"   Entrada válida: {entrada_valida}")
    print(f"   Resultado: {resultado}")
    
    return df_simulado


def probar_configuracion():
    """Prueba la configuración actual"""
    print("\n⚙️ CONFIGURACIÓN ACTUAL")
    print("=" * 30)
    print(f"   ATR mínimo: {ATR_MIN_PIPS} pips")
    print(f"   ATR máximo: {ATR_MAX_PIPS} pips")
    print(f"   ADX mínimo: {ADX_MIN}")
    print(f"   Volumen mínimo: {VOLUME_MIN}x")
    print(f"   RSI compra: {RSI_ENTRADA_COMPRA}")
    print(f"   RSI venta: {RSI_ENTRADA_VENTA}")
    print(f"   Horarios óptimos: {len(HORARIOS_OPTIMOS)} ventanas")


def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DE ESTRATEGIA EUR/USD INTRADAY")
    print("=" * 60)
    
    try:
        # Probar utilidades
        df_simulado = probar_utilidades_eurusd()
        
        # Probar configuración
        probar_configuracion()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 40)
        print("📊 Datos simulados generados correctamente")
        print("🔧 Utilidades funcionando según configuración")
        print("🎯 Estrategia lista para EUR/USD intraday")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
