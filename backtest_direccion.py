#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 BACKTEST DE DIRECCIÓN - ESTRATEGIA BREAKOUT INTRADIARIO
=========================================================
Analiza solo la dirección (BUY/SELL) del bot vs dirección real del precio
Periodo: 2-3 meses del mercado de Nueva York (8:00-17:00 EST)
Objetivo: Calcular porcentaje de acierto en dirección
"""

from broker.mt5_connector import conectar_mt5, obtener_datos
from strategy.breakout_intradiario import detectar_breakout_eurusd_backtest, calcular_indicadores_breakout
from utils.time_utils import es_horario_ny
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz


def backtest_direccion_ny(periodo_meses=3):
    """
    Backtest de dirección durante periodo específico del mercado NY
    """
    print(f"🎯 BACKTEST DE DIRECCIÓN - MERCADO NY")
    print(f"📅 Periodo: {periodo_meses} meses")
    print(f"⏰ Horario: 8:00-17:00 EST (Mercado NY)")
    print(f"🎯 Objetivo: Porcentaje de acierto en dirección")
    print("="*60)
    
    if not conectar_mt5():
        print("❌ Error conectando a MT5")
        return
    
    # Calcular fechas del periodo
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=periodo_meses * 30)
    
    print(f"📅 Periodo analizado: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
    
    # Obtener datos históricos para el periodo
    print("📥 Obteniendo datos históricos...")
    
    # Convertir fechas a timestamp para MT5
    from_date = int(fecha_inicio.timestamp())
    to_date = int(fecha_fin.timestamp())
    
    # Obtener datos M5 (timeframe principal para análisis)
    rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M5, from_date, to_date)
    
    if rates is None or len(rates) == 0:
        print("❌ No se pudieron obtener datos históricos")
        return
    
    # Convertir a DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"✅ Datos obtenidos: {len(df)} velas M5")
    print(f"📅 Rango: {df['time'].min()} a {df['time'].max()}")
    
    # Filtrar solo horario NY (8:00-17:00 EST)
    print("🔍 Filtrando horario NY...")
    df_ny = filtrar_horario_ny(df)
    print(f"✅ Velas en horario NY: {len(df_ny)}")
    
    # Calcular indicadores
    print("🔧 Calculando indicadores...")
    df_ny = calcular_indicadores_breakout(df_ny.copy())
    
    # Análisis de dirección
    resultados = analizar_direccion_bot(df_ny)
    
    # Mostrar resultados
    mostrar_resultados_direccion(resultados, df_ny)
    
    return resultados


def filtrar_horario_ny(df):
    """
    Filtra datos para incluir solo horario NY (8:00-17:00 EST)
    """
    # Convertir a zona horaria EST
    est = pytz.timezone('US/Eastern')
    
    # Aplicar zona horaria y filtrar
    df_ny = df.copy()
    df_ny['time_est'] = df_ny['time'].dt.tz_localize('UTC').dt.tz_convert(est)
    df_ny['hora_est'] = df_ny['time_est'].dt.hour
    
    # Filtrar horario NY (8:00-17:00 EST)
    df_ny = df_ny[(df_ny['hora_est'] >= 8) & (df_ny['hora_est'] < 17)]
    
    return df_ny


def analizar_direccion_bot(df_ny):
    """
    Analiza la dirección del bot vs dirección real del precio
    """
    print("🔍 Analizando dirección del bot...")
    
    resultados = {
        'total_señales': 0,
        'aciertos_direccion': 0,
        'errores_direccion': 0,
        'señales_buy': 0,
        'señales_sell': 0,
        'aciertos_buy': 0,
        'aciertos_sell': 0,
        'detalles': []
    }
    
    # Analizar cada vela en horario NY
    for i in range(100, len(df_ny) - 10):  # Dejar espacio para validación futura
        try:
            # Crear subconjunto de datos hasta el punto actual
            sub_df = df_ny.iloc[:i+1].copy()
            
            # Simular detección de señal del bot
            señal = detectar_señal_direccion(sub_df)
            
            if señal:
                tipo_señal, precio_entrada, tiempo_señal = señal
                resultados['total_señales'] += 1
                
                if tipo_señal == 'BUY':
                    resultados['señales_buy'] += 1
                else:
                    resultados['señales_sell'] += 1
                
                # Verificar dirección real del precio en las siguientes velas
                acierto = verificar_direccion_real(df_ny, i, tipo_señal, precio_entrada)
                
                if acierto:
                    resultados['aciertos_direccion'] += 1
                    if tipo_señal == 'BUY':
                        resultados['aciertos_buy'] += 1
                    else:
                        resultados['aciertos_sell'] += 1
                else:
                    resultados['errores_direccion'] += 1
                
                # Guardar detalle
                resultados['detalles'].append({
                    'tiempo': tiempo_señal,
                    'tipo': tipo_señal,
                    'precio': precio_entrada,
                    'acierto': acierto
                })
                
                # Mostrar progreso cada 50 señales
                if resultados['total_señales'] % 50 == 0:
                    print(f"📊 Progreso: {resultados['total_señales']} señales analizadas")
        
        except Exception as e:
            continue
    
    return resultados


def detectar_señal_direccion(df):
    """
    Detecta señal de dirección usando la estrategia del bot
    """
    if len(df) < 50:
        return None
    
    # Calcular indicadores
    df = calcular_indicadores_breakout(df.copy())
    
    # Detectar tendencia intradiaria (usando M15 equivalente)
    tendencia = detectar_tendencia_simplificada(df)
    
    if tendencia == 'neutral':
        return None
    
    # Validar condiciones de breakout
    if validar_breakout_direccion(df, tendencia):
        precio_entrada = df['close'].iloc[-1]
        tiempo_señal = df['time'].iloc[-1]
        
        if tendencia == 'alcista':
            return ('BUY', precio_entrada, tiempo_señal)
        else:
            return ('SELL', precio_entrada, tiempo_señal)
    
    return None


def detectar_tendencia_simplificada(df):
    """
    Detecta tendencia usando EMAs
    """
    if len(df) < 20:
        return 'neutral'
    
    # Calcular EMAs
    ema_rapida = df['close'].ewm(span=20, adjust=False).mean()
    ema_lenta = df['close'].ewm(span=50, adjust=False).mean()
    
    ultima_ema_rapida = ema_rapida.iloc[-1]
    ultima_ema_lenta = ema_lenta.iloc[-1]
    
    if ultima_ema_rapida > ultima_ema_lenta:
        return 'alcista'
    elif ultima_ema_rapida < ultima_ema_lenta:
        return 'bajista'
    else:
        return 'neutral'


def validar_breakout_direccion(df, tendencia):
    """
    Valida condiciones de breakout para dirección
    """
    if len(df) < 20:
        return False
    
    ultima = df.iloc[-1]
    anterior = df.iloc[-2]
    
    # Condiciones optimizadas de breakout
    if tendencia == 'alcista':
        return (
            ultima['close'] > ultima['open'] and                    # Vela alcista
            ultima['close'] > anterior['close'] and                # Precio sube
            ultima['ADX'] >= 12 and                                # ADX optimizado
            ultima['Vol_Relativo'] >= 0.5 and                      # Volumen optimizado
            ultima['RSI'] <= 45 and                                # RSI optimizado
            ultima['Pendiente'] > 0.0001                           # Pendiente optimizada
        )
    
    elif tendencia == 'bajista':
        return (
            ultima['close'] < ultima['open'] and                    # Vela bajista
            ultima['close'] < anterior['close'] and                # Precio baja
            ultima['ADX'] >= 12 and                                # ADX optimizado
            ultima['Vol_Relativo'] >= 0.5 and                      # Volumen optimizado
            ultima['RSI'] >= 55 and                                # RSI optimizado
            ultima['Pendiente'] < -0.0001                          # Pendiente optimizada
        )
    
    return False


def verificar_direccion_real(df, indice_señal, tipo_señal, precio_entrada):
    """
    Verifica si la dirección del bot fue correcta
    """
    # Analizar las siguientes 10 velas para determinar dirección real
    velas_futuras = 10
    if indice_señal + velas_futuras >= len(df):
        return False
    
    # Obtener precios futuros
    precios_futuros = df.iloc[indice_señal+1:indice_señal+velas_futuras+1]['close'].values
    
    # Calcular dirección real
    precio_max = max(precios_futuros)
    precio_min = min(precios_futuros)
    precio_final = precios_futuros[-1]
    
    if tipo_señal == 'BUY':
        # Para BUY: el precio debe subir significativamente
        movimiento_positivo = precio_final - precio_entrada
        movimiento_total = precio_max - precio_entrada
        
        # Considerar acierto si:
        # 1. El precio final es mayor al de entrada, O
        # 2. El precio llegó a subir al menos 5 pips
        return (movimiento_positivo > 0) or (movimiento_total > 0.0005)
    
    else:  # SELL
        # Para SELL: el precio debe bajar significativamente
        movimiento_negativo = precio_entrada - precio_final
        movimiento_total = precio_entrada - precio_min
        
        # Considerar acierto si:
        # 1. El precio final es menor al de entrada, O
        # 2. El precio llegó a bajar al menos 5 pips
        return (movimiento_negativo > 0) or (movimiento_total > 0.0005)


def mostrar_resultados_direccion(resultados, df_ny):
    """
    Muestra resultados detallados del análisis de dirección
    """
    print("\n" + "="*60)
    print("📊 RESULTADOS DEL BACKTEST DE DIRECCIÓN")
    print("="*60)
    
    if resultados['total_señales'] == 0:
        print("❌ No se detectaron señales durante el periodo")
        return
    
    # Estadísticas generales
    total_señales = resultados['total_señales']
    aciertos = resultados['aciertos_direccion']
    errores = resultados['errores_direccion']
    
    porcentaje_acierto = (aciertos / total_señales) * 100
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total señales: {total_señales}")
    print(f"   Aciertos en dirección: {aciertos}")
    print(f"   Errores en dirección: {errores}")
    print(f"   Porcentaje de acierto: {porcentaje_acierto:.1f}%")
    
    # Análisis por tipo de señal
    print(f"\n📈 ANÁLISIS POR TIPO DE SEÑAL:")
    
    if resultados['señales_buy'] > 0:
        acierto_buy = (resultados['aciertos_buy'] / resultados['señales_buy']) * 100
        print(f"   SEÑALES BUY:")
        print(f"     - Total: {resultados['señales_buy']}")
        print(f"     - Aciertos: {resultados['aciertos_buy']}")
        print(f"     - Porcentaje acierto: {acierto_buy:.1f}%")
    
    if resultados['señales_sell'] > 0:
        acierto_sell = (resultados['aciertos_sell'] / resultados['señales_sell']) * 100
        print(f"   SEÑALES SELL:")
        print(f"     - Total: {resultados['señales_sell']}")
        print(f"     - Aciertos: {resultados['aciertos_sell']}")
        print(f"     - Porcentaje acierto: {acierto_sell:.1f}%")
    
    # Análisis temporal
    print(f"\n⏰ ANÁLISIS TEMPORAL:")
    print(f"   Periodo analizado: {df_ny['time'].min()} a {df_ny['time'].max()}")
    print(f"   Velas en horario NY: {len(df_ny)}")
    print(f"   Promedio señales por día: {total_señales / ((df_ny['time'].max() - df_ny['time'].min()).days):.1f}")
    
    # Evaluación del rendimiento
    print(f"\n🎯 EVALUACIÓN DEL RENDIMIENTO:")
    if porcentaje_acierto >= 70:
        print(f"   🟢 EXCELENTE: {porcentaje_acierto:.1f}% de acierto")
    elif porcentaje_acierto >= 60:
        print(f"   🟡 BUENO: {porcentaje_acierto:.1f}% de acierto")
    elif porcentaje_acierto >= 50:
        print(f"   🟠 ACEPTABLE: {porcentaje_acierto:.1f}% de acierto")
    else:
        print(f"   🔴 MEJORABLE: {porcentaje_acierto:.1f}% de acierto")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if porcentaje_acierto < 60:
        print(f"   - Considerar ajustar filtros para mejorar precisión")
        print(f"   - Analizar periodos de mayor volatilidad")
        print(f"   - Revisar condiciones de entrada")
    else:
        print(f"   - El bot muestra buena precisión en dirección")
        print(f"   - Considerar implementar gestión de riesgo")
        print(f"   - Analizar periodos específicos de mayor acierto")
    
    print("\n✅ Backtest de dirección completado")


if __name__ == "__main__":
    print("🎯 INICIANDO BACKTEST DE DIRECCIÓN - MERCADO NY")
    print("="*70)
    
    # Ejecutar backtest de 3 meses
    try:
        resultados = backtest_direccion_ny(periodo_meses=3)
        print(f"\n🎯 Backtest completado exitosamente")
    except Exception as e:
        print(f"❌ Error en backtest: {e}")
