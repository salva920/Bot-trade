#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ANÁLISIS MULTI-TIMEFRAME - ESTRATEGIA BREAKOUT
=================================================
Analiza la situación del mercado en todas las temporalidades
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime

def analizar_multitimeframe_completo(symbol="EURUSD"):
    """
    Análisis completo del mercado en todas las temporalidades
    """
    print("📊 ANÁLISIS MULTI-TIMEFRAME - EUR/USD")
    print("="*60)
    
    # Obtener datos de todas las temporalidades
    timeframes = {
        'D1': mt5.TIMEFRAME_D1,
        'H4': mt5.TIMEFRAME_H4,
        'H1': mt5.TIMEFRAME_H1,
        'M15': mt5.TIMEFRAME_M15,
        'M5': mt5.TIMEFRAME_M5,
        'M1': mt5.TIMEFRAME_M1
    }
    
    analisis = {}
    
    for nombre, tf in timeframes.items():
        try:
            # Obtener datos
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, 100)
            if rates is None or len(rates) < 50:
                continue
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calcular indicadores
            df = calcular_indicadores_simples(df)
            
            # Analizar tendencia
            tendencia = analizar_tendencia_timeframe(df, nombre)
            
            analisis[nombre] = {
                'tendencia': tendencia['direccion'],
                'fuerza': tendencia['fuerza'],
                'distancia_emas': tendencia['distancia_emas'],
                'volatilidad': tendencia['volatilidad'],
                'rsi': tendencia['rsi'],
                'adx': tendencia['adx'],
                'precio_actual': df['close'].iloc[-1],
                'timestamp': df['time'].iloc[-1]
            }
            
        except Exception as e:
            print(f"❌ Error analizando {nombre}: {e}")
            continue
    
    # Mostrar análisis
    mostrar_analisis_multitimeframe(analisis)
    
    return analisis

def calcular_indicadores_simples(df):
    """
    Calcula indicadores básicos para análisis
    """
    # EMAs
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ATR
    df['TR'] = pd.concat([
        df['high'] - df['low'],
        abs(df['high'] - df['close'].shift()),
        abs(df['low'] - df['close'].shift())
    ], axis=1).max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # ADX simplificado
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
    df['TR_smooth'] = df['TR'].rolling(window=14).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=14).mean() / df['TR_smooth'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=14).mean() / df['TR_smooth'])
    df['DX'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['ADX'] = df['DX'].rolling(window=14).mean()
    
    return df

def analizar_tendencia_timeframe(df, nombre_timeframe):
    """
    Analiza la tendencia en un timeframe específico
    """
    if len(df) < 26:
        return {
            'direccion': 'neutral',
            'fuerza': 'débil',
            'distancia_emas': 0,
            'volatilidad': 0,
            'rsi': 50,
            'adx': 0
        }
    
    ultima = df.iloc[-1]
    
    # Tendencia basada en EMAs
    ema_rapida = ultima['EMA_12']
    ema_lenta = ultima['EMA_26']
    
    if ema_rapida > ema_lenta:
        direccion = 'alcista'
    elif ema_rapida < ema_lenta:
        direccion = 'bajista'
    else:
        direccion = 'neutral'
    
    # Fuerza de la tendencia
    distancia_emas = abs(ema_rapida - ema_lenta) * 10000  # En pips
    adx = ultima['ADX'] if not pd.isna(ultima['ADX']) else 0
    
    if adx >= 30 and distancia_emas >= 20:
        fuerza = 'fuerte'
    elif adx >= 20 and distancia_emas >= 10:
        fuerza = 'moderada'
    else:
        fuerza = 'débil'
    
    # Volatilidad
    atr = ultima['ATR'] if not pd.isna(ultima['ATR']) else 0
    volatilidad = atr * 10000  # En pips
    
    # RSI
    rsi = ultima['RSI'] if not pd.isna(ultima['RSI']) else 50
    
    return {
        'direccion': direccion,
        'fuerza': fuerza,
        'distancia_emas': distancia_emas,
        'volatilidad': volatilidad,
        'rsi': rsi,
        'adx': adx
    }

def mostrar_analisis_multitimeframe(analisis):
    """
    Muestra el análisis multi-timeframe de forma organizada
    """
    print("\n📈 SITUACIÓN DEL MERCADO POR TIMEFRAME:")
    print("-" * 60)
    
    # Ordenar timeframes de mayor a menor
    orden_timeframes = ['D1', 'H4', 'H1', 'M15', 'M5', 'M1']
    
    for tf in orden_timeframes:
        if tf in analisis:
            data = analisis[tf]
            
            # Emoji según tendencia
            emoji_tendencia = "🟢" if data['tendencia'] == 'alcista' else "🔴" if data['tendencia'] == 'bajista' else "🟡"
            
            # Emoji según fuerza
            emoji_fuerza = "💪" if data['fuerza'] == 'fuerte' else "⚡" if data['fuerza'] == 'moderada' else "💨"
            
            print(f"🕐 {tf:3s}: {emoji_tendencia} {data['tendencia'].upper():8s} {emoji_fuerza} {data['fuerza'].upper():8s}")
            print(f"     📊 EMAs: {data['distancia_emas']:5.1f} pips | ATR: {data['volatilidad']:5.1f} pips")
            print(f"     📈 RSI: {data['rsi']:5.1f} | ADX: {data['adx']:5.1f}")
            print(f"     💰 Precio: {data['precio_actual']:.5f}")
            print()
    
    # Análisis de confluencia
    print("🎯 ANÁLISIS DE CONFLUENCIA:")
    print("-" * 30)
    
    tendencias_alcistas = sum(1 for tf in ['D1', 'H4', 'H1'] if tf in analisis and analisis[tf]['tendencia'] == 'alcista')
    tendencias_bajistas = sum(1 for tf in ['D1', 'H4', 'H1'] if tf in analisis and analisis[tf]['tendencia'] == 'bajista')
    
    if tendencias_alcistas >= 2:
        print("🟢 CONFLUENCIA ALCISTA en temporalidades grandes")
    elif tendencias_bajistas >= 2:
        print("🔴 CONFLUENCIA BAJISTA en temporalidades grandes")
    else:
        print("🟡 CONFLUENCIA NEUTRA en temporalidades grandes")
    
    print(f"📊 D1: {analisis.get('D1', {}).get('tendencia', 'N/A')} | H4: {analisis.get('H4', {}).get('tendencia', 'N/A')} | H1: {analisis.get('H1', {}).get('tendencia', 'N/A')}")
    print()

def obtener_resumen_tendencia_principal(analisis):
    """
    Obtiene un resumen de la tendencia principal
    """
    timeframes_principales = ['D1', 'H4', 'H1']
    tendencias = []
    
    for tf in timeframes_principales:
        if tf in analisis:
            tendencias.append(analisis[tf]['tendencia'])
    
    if len(tendencias) >= 2:
        if tendencias.count('alcista') >= 2:
            return 'alcista', 'fuerte'
        elif tendencias.count('bajista') >= 2:
            return 'bajista', 'fuerte'
        else:
            return 'neutral', 'débil'
    
    return 'neutral', 'débil'
