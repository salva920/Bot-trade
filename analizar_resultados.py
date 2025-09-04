#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ANALIZADOR DE RESULTADOS - TRADING TODOS LOS HORARIOS
========================================================
Analiza el rendimiento del bot en diferentes horarios para optimización
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import datetime
import os

def analizar_log_trading():
    """Analiza el archivo de log de trading"""
    
    if not os.path.exists('trading_log.txt'):
        print("❌ No se encontró el archivo trading_log.txt")
        return
    
    print("📊 ANALIZANDO RESULTADOS DE TRADING TODOS LOS HORARIOS")
    print("=" * 60)
    
    # Leer datos del log
    datos = []
    with open('trading_log.txt', 'r', encoding='utf-8') as f:
        for linea in f:
            if '|' in linea:
                partes = linea.strip().split(' | ')
                if len(partes) >= 6:
                    datos.append({
                        'fecha_hora': partes[0],
                        'horario': partes[1],
                        'tipo': partes[2],
                        'precio': float(partes[3]),
                        'lote': float(partes[4]),
                        'estado': partes[5]
                    })
    
    if not datos:
        print("❌ No hay datos para analizar")
        return
    
    df = pd.DataFrame(datos)
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    df['hora'] = df['fecha_hora'].dt.hour
    df['dia_semana'] = df['fecha_hora'].dt.day_name()
    
    # Estadísticas generales
    print(f"📈 TOTAL DE OPERACIONES: {len(df)}")
    print(f"📅 PERIODO: {df['fecha_hora'].min()} a {df['fecha_hora'].max()}")
    print(f"⏰ DURACIÓN: {(df['fecha_hora'].max() - df['fecha_hora'].min()).days} días")
    
    # Análisis por horario
    print("\n🕐 ANÁLISIS POR HORARIO:")
    print("-" * 40)
    
    stats_por_hora = df.groupby('hora').agg({
        'estado': 'count',
        'tipo': lambda x: (x == 'BUY').sum()
    }).rename(columns={'estado': 'total_operaciones', 'tipo': 'operaciones_buy'})
    
    stats_por_hora['operaciones_sell'] = stats_por_hora['total_operaciones'] - stats_por_hora['operaciones_buy']
    stats_por_hora['porcentaje_buy'] = (stats_por_hora['operaciones_buy'] / stats_por_hora['total_operaciones'] * 100).round(1)
    
    for hora, stats in stats_por_hora.iterrows():
        print(f"🕐 {hora:02d}:00 - {stats['total_operaciones']} operaciones "
              f"({stats['operaciones_buy']} BUY, {stats['operaciones_sell']} SELL) "
              f"({stats['porcentaje_buy']}% BUY)")
    
    # Análisis por día de la semana
    print("\n📅 ANÁLISIS POR DÍA DE LA SEMANA:")
    print("-" * 40)
    
    stats_por_dia = df.groupby('dia_semana').agg({
        'estado': 'count'
    }).rename(columns={'estado': 'total_operaciones'})
    
    for dia, stats in stats_por_dia.iterrows():
        print(f"📅 {dia}: {stats['total_operaciones']} operaciones")
    
    # Horarios más activos
    print("\n🔥 HORARIOS MÁS ACTIVOS:")
    print("-" * 40)
    
    top_horarios = stats_por_hora.nlargest(5, 'total_operaciones')
    for hora, stats in top_horarios.iterrows():
        print(f"🕐 {hora:02d}:00 - {stats['total_operaciones']} operaciones")
    
    # Generar gráficos
    generar_graficos(df, stats_por_hora)
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    print("-" * 40)
    
    mejor_horario = stats_por_hora.loc[stats_por_hora['total_operaciones'].idxmax()]
    mejor_hora = stats_por_hora['total_operaciones'].idxmax()
    
    print(f"🎯 Horario más activo: {mejor_hora:02d}:00 ({mejor_horario['total_operaciones']} operaciones)")
    
    # Analizar distribución BUY/SELL
    total_buy = stats_por_hora['operaciones_buy'].sum()
    total_sell = stats_por_hora['operaciones_sell'].sum()
    total_ops = total_buy + total_sell
    
    print(f"📊 Distribución: {total_buy} BUY ({total_buy/total_ops*100:.1f}%) vs {total_sell} SELL ({total_sell/total_ops*100:.1f}%)")
    
    # Horarios recomendados
    print("\n🚀 HORARIOS RECOMENDADOS PARA OPTIMIZACIÓN:")
    print("-" * 40)
    
    horarios_altos = stats_por_hora[stats_por_hora['total_operaciones'] >= stats_por_hora['total_operaciones'].mean()]
    for hora, stats in horarios_altos.iterrows():
        print(f"✅ {hora:02d}:00 - {stats['total_operaciones']} operaciones")
    
    print(f"\n📝 Guardando análisis en 'analisis_resultados.txt'...")
    guardar_analisis_completo(df, stats_por_hora, stats_por_dia)

def generar_graficos(df, stats_por_hora):
    """Genera gráficos de análisis"""
    
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Gráfico 1: Operaciones por hora
    axes[0, 0].bar(stats_por_hora.index, stats_por_hora['total_operaciones'])
    axes[0, 0].set_title('Operaciones por Hora del Día')
    axes[0, 0].set_xlabel('Hora')
    axes[0, 0].set_ylabel('Número de Operaciones')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gráfico 2: Distribución BUY/SELL por hora
    x = stats_por_hora.index
    width = 0.35
    axes[0, 1].bar(x - width/2, stats_por_hora['operaciones_buy'], width, label='BUY', alpha=0.8)
    axes[0, 1].bar(x + width/2, stats_por_hora['operaciones_sell'], width, label='SELL', alpha=0.8)
    axes[0, 1].set_title('Distribución BUY/SELL por Hora')
    axes[0, 1].set_xlabel('Hora')
    axes[0, 1].set_ylabel('Número de Operaciones')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Gráfico 3: Operaciones por día de la semana
    stats_por_dia = df.groupby('dia_semana').size()
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    stats_por_dia_ordenado = stats_por_dia.reindex(dias_orden, fill_value=0)
    
    axes[1, 0].bar(range(len(stats_por_dia_ordenado)), stats_por_dia_ordenado.values)
    axes[1, 0].set_title('Operaciones por Día de la Semana')
    axes[1, 0].set_xlabel('Día')
    axes[1, 0].set_ylabel('Número de Operaciones')
    axes[1, 0].set_xticks(range(len(stats_por_dia_ordenado)))
    axes[1, 0].set_xticklabels(['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'], rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Gráfico 4: Evolución temporal
    df['fecha'] = df['fecha_hora'].dt.date
    operaciones_por_fecha = df.groupby('fecha').size()
    
    axes[1, 1].plot(operaciones_por_fecha.index, operaciones_por_fecha.values, marker='o')
    axes[1, 1].set_title('Evolución de Operaciones por Fecha')
    axes[1, 1].set_xlabel('Fecha')
    axes[1, 1].set_ylabel('Número de Operaciones')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('analisis_resultados.png', dpi=300, bbox_inches='tight')
    print("📊 Gráficos guardados en 'analisis_resultados.png'")

def guardar_analisis_completo(df, stats_por_hora, stats_por_dia):
    """Guarda análisis completo en archivo de texto"""
    
    with open('analisis_resultados.txt', 'w', encoding='utf-8') as f:
        f.write("📊 ANÁLISIS COMPLETO DE RESULTADOS - TRADING TODOS LOS HORARIOS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"📈 TOTAL DE OPERACIONES: {len(df)}\n")
        f.write(f"📅 PERIODO: {df['fecha_hora'].min()} a {df['fecha_hora'].max()}\n")
        f.write(f"⏰ DURACIÓN: {(df['fecha_hora'].max() - df['fecha_hora'].min()).days} días\n\n")
        
        f.write("🕐 ANÁLISIS DETALLADO POR HORARIO:\n")
        f.write("-" * 40 + "\n")
        for hora, stats in stats_por_hora.iterrows():
            f.write(f"🕐 {hora:02d}:00 - {stats['total_operaciones']} operaciones "
                   f"({stats['operaciones_buy']} BUY, {stats['operaciones_sell']} SELL) "
                   f"({stats['porcentaje_buy']}% BUY)\n")
        
        f.write("\n📅 ANÁLISIS POR DÍA DE LA SEMANA:\n")
        f.write("-" * 40 + "\n")
        for dia, stats in stats_por_dia.iterrows():
            f.write(f"📅 {dia}: {stats['total_operaciones']} operaciones\n")
        
        f.write("\n💡 RECOMENDACIONES:\n")
        f.write("-" * 40 + "\n")
        
        mejor_hora = stats_por_hora['total_operaciones'].idxmax()
        mejor_stats = stats_por_hora.loc[mejor_hora]
        f.write(f"🎯 Horario más activo: {mejor_hora:02d}:00 ({mejor_stats['total_operaciones']} operaciones)\n")
        
        total_buy = stats_por_hora['operaciones_buy'].sum()
        total_sell = stats_por_hora['operaciones_sell'].sum()
        total_ops = total_buy + total_sell
        
        f.write(f"📊 Distribución: {total_buy} BUY ({total_buy/total_ops*100:.1f}%) vs {total_sell} SELL ({total_sell/total_ops*100:.1f}%)\n")
        
        f.write("\n🚀 HORARIOS RECOMENDADOS PARA OPTIMIZACIÓN:\n")
        f.write("-" * 40 + "\n")
        
        horarios_altos = stats_por_hora[stats_por_hora['total_operaciones'] >= stats_por_hora['total_operaciones'].mean()]
        for hora, stats in horarios_altos.iterrows():
            f.write(f"✅ {hora:02d}:00 - {stats['total_operaciones']} operaciones\n")
    
    print("✅ Análisis completo guardado en 'analisis_resultados.txt'")

if __name__ == "__main__":
    analizar_log_trading()
