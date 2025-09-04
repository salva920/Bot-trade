# ============================================================================
# 🚀 CONFIGURACIÓN GANADORA - ESTRATEGIA BREAKOUT INTRADIARIO
# ============================================================================
# Configuración que logró: Win Rate 84.6% | Rendimiento 15.56% | Sharpe 26.25

# Configuración de MetaTrader 5
MT5_LOGIN = 10006727030
MT5_PASSWORD = "X*J7QuIk"
MT5_INVESTOR = "*5NaLiNo"
MT5_SERVER = "MetaQuotes-Demo"

# Configuración de trading EUR/USD - ESTRATEGIA GANADORA
SYMBOL = "EURUSD"
LOT = 0.1
RISK_REWARD = 3.0  # Ratio optimizado para la estrategia ganadora
SL_PIPS = 16
TP_PIPS = 48  # 16 * 3 = 48 pips

# Horarios optimizados para EUR/USD
NY_START = (8, 0)   # 8:00 AM NY
NY_END = (17, 0)    # 5:00 PM NY

# ESTRATEGIA BREAKOUT INTRADIARIO - CONFIGURACIÓN GANADORA
TIMEFRAMES_ESTRATEGIA = {
    'TENDENCIA_INTRADIARIA': ['M15'],     # Tendencia intradiaria
    'CONFIRMACION_BREAKOUT': ['M5'],      # Confirmación de breakout
    'TIMING_ENTRADA': ['M1']              # Timing preciso de entrada
}

# FILTROS OPTIMIZADOS - CONFIGURACIÓN GANADORA
ADX_MIN = 8         # ADX mínimo ultra reducido para más señales
VOLUME_MIN = 0.3    # Volumen mínimo ultra reducido
RSI_ENTRADA_COMPRA = 50  # RSI menos extremo para entradas de compra
RSI_ENTRADA_VENTA = 50   # RSI menos extremo para entradas de venta
ATR_MIN_PIPS = 0.5  # Volatilidad mínima ultra reducida
ATR_MAX_PIPS = 50   # Volatilidad máxima aumentada

# PARÁMETROS ULTRA FLEXIBLES PARA MÁXIMAS SEÑALES
PENDIENTE_MINIMA = 0.00005  # Pendiente mínima ultra reducida
PENDIENTE_MAXIMA = -0.00005 # Pendiente máxima ultra reducida

# ============================================================================
# 🚀 GESTIÓN DE RIESGO INTELIGENTE - CONFIGURACIÓN GANADORA
# ============================================================================

# STOP LOSS ADAPTATIVO BASADO EN ATR
STOP_LOSS_ATR_MULTIPLIER = 2.0    # Stop Loss = 2 × ATR
STOP_LOSS_MIN_PIPS = 5             # Stop Loss mínimo = 5 pips
STOP_LOSS_MAX_PIPS = 20            # Stop Loss máximo = 20 pips

# TAKE PROFIT DINÁMICO CON RATIO RIESGO/BENEFICIO OPTIMIZADO
TAKE_PROFIT_RATIO = 3.0            # Take Profit = 3 × Stop Loss (ratio 1:3)
TAKE_PROFIT_MIN_PIPS = 15          # Take Profit mínimo = 15 pips
TAKE_PROFIT_MAX_PIPS = 60          # Take Profit máximo = 60 pips

# TRAILING STOP AUTOMÁTICO PARA PROTEGER GANANCIAS
TRAILING_STOP_ACTIVAR_PIPS = 10    # Activar trailing cuando ganancia > 10 pips
TRAILING_STOP_ATR_MULTIPLIER = 1.0 # Trailing = 1 × ATR
TRAILING_STOP_MIN_PIPS = 3         # Trailing mínimo = 3 pips

# GESTIÓN DE POSICIÓN DINÁMICA
POSITION_SIZE_RISK_PERCENT = 2.0   # Riesgo máximo por operación = 2%
POSITION_SIZE_MAX_LOTS = 1.0       # Lote máximo por operación = 1.0
POSITION_SIZE_MIN_LOTS = 0.01      # Lote mínimo por operación = 0.01

# FILTROS DE TENDENCIA AVANZADOS
TREND_CONFIRMATION_TIMEFRAMES = ['H1', 'H4', 'D1']
TREND_STRENGTH_MIN_ADX = 25
TREND_MOMENTUM_RSI_MIN = 30
TREND_MOMENTUM_RSI_MAX = 70

# VALIDACIÓN DE VOLUMEN EN TIEMPO REAL
VOLUME_SPIKE_MULTIPLIER = 1.2      # Volumen debe ser 1.2x mayor que el promedio
VOLUME_CONFIRMATION_PERIODS = 20
VOLUME_MIN_ABSOLUTE = 50           # Volumen mínimo absoluto

# TIMING DE ENTRADA ULTRA PRECISO (M1)
ENTRY_TIMING_RSI_OVERBOUGHT = 80   # RSI M1 para evitar entradas en sobrecompra
ENTRY_TIMING_RSI_OVERSOLD = 20     # RSI M1 para evitar entradas en sobreventa
ENTRY_TIMING_VOLUME_MIN = 0.5      # Volumen mínimo M1
ENTRY_TIMING_ATR_MIN = 0.5         # ATR mínimo M1

# RATIOS DE RIESGO/BENEFICIO DINÁMICOS
RISK_REWARD_RATIO_MIN = 2.0        # Ratio mínimo 1:2
RISK_REWARD_RATIO_TARGET = 3.0     # Ratio objetivo 1:3
RISK_REWARD_RATIO_MAX = 5.0        # Ratio máximo 1:5

# PROTECCIÓN CONTRA DRAWDOWN
MAX_DRAWDOWN_PERCENT = 5.0         # Drawdown máximo permitido = 5%
MAX_CONSECUTIVE_LOSSES = 5         # Máximo 5 pérdidas consecutivas
BREAK_EVEN_ACTIVATION_PIPS = 8     # Activar break-even cuando ganancia > 8 pips

# Configuración de breakout - CONFIGURACIÓN GANADORA
BREAKOUT_CONFIG = {
    'PERIODO_EMA_RAPIDA': 20,     # EMA rápida para tendencia
    'PERIODO_EMA_LENTA': 50,      # EMA lenta para tendencia
    'PERIODO_RSI': 14,            # RSI para momentum
    'PERIODO_ADX': 14,            # ADX para fuerza de tendencia
    'PERIODO_VOLUMEN': 20,        # Volumen relativo
    'PERIODO_ATR': 14,            # ATR para volatilidad
    'PERIODO_PENDIENTE': 20       # Pendiente de tendencia
}

# Horarios óptimos específicos para EUR/USD
HORARIOS_OPTIMOS = [
    (8, 0),   # 8:00 AM NY
    (9, 0),   # 9:00 AM NY
    (10, 0),  # 10:00 AM NY
    (11, 0),  # 11:00 AM NY
    (12, 0),  # 12:00 PM NY
    (13, 0),  # 1:00 PM NY
    (14, 0),  # 2:00 PM NY
    (15, 0),  # 3:00 PM NY
    (16, 0),  # 4:00 PM NY
    (17, 0),  # 5:00 PM NY
]

# ============================================================================
# 📊 ESTADÍSTICAS DE LA CONFIGURACIÓN GANADORA
# ============================================================================
ESTADISTICAS_GANADORAS = {
    'win_rate': 84.6,
    'rendimiento': 15.56,
    'sharpe_ratio': 26.25,
    'drawdown_maximo': 0.44,
    'total_operaciones': 13,
    'operaciones_ganadoras': 11,
    'operaciones_perdedoras': 2,
    'promedio_por_trade': 119.66,
    'mejor_trade': 155.57,
    'peor_trade': -50.00
}

print("🚀 CONFIGURACIÓN GANADORA CARGADA")
print(f"📊 Win Rate: {ESTADISTICAS_GANADORAS['win_rate']}%")
print(f"📈 Rendimiento: {ESTADISTICAS_GANADORAS['rendimiento']}%")
print(f"⚡ Sharpe Ratio: {ESTADISTICAS_GANADORAS['sharpe_ratio']}")
print(f"🛡️ Drawdown Máximo: {ESTADISTICAS_GANADORAS['drawdown_maximo']}%")
