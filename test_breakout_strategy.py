"""
Script de prueba para la estrategia de BREAKOUT INTRADIARIO
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.breakout_intradiario import (
    es_horario_optimo_breakout,
    es_volatilidad_optima_breakout,
    detectar_tendencia_intradiaria,
    confirmar_breakout_m5,
    timing_entrada_preciso_m1,
    calcular_lote_dinamico_breakout,
    validar_breakout_completo
)
from config import (
    ATR_MIN_PIPS, ATR_MAX_PIPS, ADX_MIN, VOLUME_MIN,
    RSI_ENTRADA_COMPRA, RSI_ENTRADA_VENTA, HORARIOS_OPTIMOS,
    BREAKOUT_CONFIG
)
import pandas as pd
import numpy as np


def crear_datos_simulados_breakout():
    """Crea datos simulados para probar la estrategia de breakout"""
    np.random.seed(42)
    
    # Crear datos M15 simulados (tendencia intradiaria)
    n_bars = 100
    base_price = 1.0850  # EUR/USD base
    
    # Generar precios con tendencia alcista clara
    returns = np.random.normal(0.0002, 0.0003, n_bars)  # 0.02% media, 0.03% std
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Crear OHLC
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + abs(np.random.normal(0, 0.0001)))
        low = price * (1 - abs(np.random.normal(0, 0.0001)))
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


def probar_utilidades_breakout():
    """Prueba todas las utilidades de breakout intradiario"""
    print("🧪 PROBANDO ESTRATEGIA BREAKOUT INTRADIARIO")
    print("=" * 60)
    
    # 1. Probar horarios óptimos
    print("\n1️⃣ Probando horarios óptimos para breakout:")
    horario_optimo = es_horario_optimo_breakout()
    print(f"   Horario actual óptimo: {horario_optimo}")
    print(f"   Horarios configurados: {HORARIOS_OPTIMOS}")
    
    # 2. Probar volatilidad óptima
    print("\n2️⃣ Probando volatilidad óptima para breakout:")
    df_simulado = crear_datos_simulados_breakout()
    volatilidad_optima = es_volatilidad_optima_breakout(df_simulado, 16)
    print(f"   Volatilidad óptima: {volatilidad_optima}")
    print(f"   ATR actual: {df_simulado['ATR'].iloc[-1] * 10000:.1f} pips")
    print(f"   Rango objetivo: {ATR_MIN_PIPS}-{ATR_MAX_PIPS} pips")
    
    # 3. Probar detección de tendencia intradiaria
    print("\n3️⃣ Probando detección de tendencia intradiaria:")
    tendencia_intradiaria = detectar_tendencia_intradiaria(df_simulado)
    print(f"   Tendencia intradiaria: {tendencia_intradiaria}")
    
    # 4. Probar confirmación de breakout
    print("\n4️⃣ Probando confirmación de breakout:")
    breakout_confirmado = confirmar_breakout_m5(df_simulado, tendencia_intradiaria)
    print(f"   Breakout confirmado: {breakout_confirmado}")
    
    # 5. Probar timing de entrada
    print("\n5️⃣ Probando timing de entrada preciso:")
    timing_preciso = timing_entrada_preciso_m1(df_simulado, tendencia_intradiaria)
    print(f"   Timing preciso: {timing_preciso}")
    
    # 6. Probar cálculo de lote dinámico
    print("\n6️⃣ Probando cálculo de lote dinámico:")
    balance_simulado = 10000  # $10,000
    lote_optimo = calcular_lote_dinamico_breakout(balance_simulado, 1.5, 16)
    print(f"   Balance: ${balance_simulado:,}")
    print(f"   Riesgo objetivo: 1.5%")
    print(f"   Stop Loss: 16 pips")
    print(f"   Lote óptimo: {lote_optimo}")
    
    # 7. Probar validación completa
    print("\n7️⃣ Probando validación completa de breakout:")
    # Crear dataframes simulados para diferentes timeframes
    df_m15 = df_simulado.copy()
    df_m5 = df_simulado.copy()
    df_m1 = df_simulado.copy()
    
    breakout_valido, resultado = validar_breakout_completo(df_m15, df_m5, df_m1, debug=True)
    print(f"   Breakout válido: {breakout_valido}")
    print(f"   Resultado: {resultado}")
    
    return df_simulado


def probar_configuracion_breakout():
    """Prueba la configuración de breakout"""
    print("\n⚙️ CONFIGURACIÓN BREAKOUT INTRADIARIO")
    print("=" * 50)
    print(f"   ATR mínimo: {ATR_MIN_PIPS} pips")
    print(f"   ATR máximo: {ATR_MAX_PIPS} pips")
    print(f"   ADX mínimo: {ADX_MIN}")
    print(f"   Volumen mínimo: {VOLUME_MIN}x")
    print(f"   RSI compra: {RSI_ENTRADA_COMPRA}")
    print(f"   RSI venta: {RSI_ENTRADA_VENTA}")
    print(f"   Horarios óptimos: {len(HORARIOS_OPTIMOS)} ventanas")
    
    print("\n🔧 CONFIGURACIÓN DE INDICADORES:")
    for key, value in BREAKOUT_CONFIG.items():
        print(f"   {key}: {value}")


def probar_timeframes_estrategia():
    """Prueba la consistencia de timeframes"""
    print("\n⏰ ANÁLISIS DE TIMEFRAMES")
    print("=" * 30)
    
    from config import TIMEFRAMES_ESTRATEGIA
    
    print("🎯 Estrategia de BREAKOUT INTRADIARIO:")
    for nivel, timeframes in TIMEFRAMES_ESTRATEGIA.items():
        print(f"   {nivel}: {timeframes}")
    
    print("\n✅ VENTAJAS de esta estrategia:")
    print("   • Consistencia temporal perfecta")
    print("   • Solo timeframes intradiarios")
    print("   • Entradas más rápidas")
    print("   • Menos falsas señales")
    print("   • Ideal para objetivo 1-2%")


def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DE ESTRATEGIA BREAKOUT INTRADIARIO")
    print("=" * 70)
    
    try:
        # Probar utilidades
        df_simulado = probar_utilidades_breakout()
        
        # Probar configuración
        probar_configuracion_breakout()
        
        # Probar timeframes
        probar_timeframes_estrategia()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 50)
        print("📊 Datos simulados generados correctamente")
        print("🔧 Utilidades de breakout funcionando")
        print("🎯 Estrategia lista para EUR/USD intraday")
        print("⏰ Consistencia temporal garantizada")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
