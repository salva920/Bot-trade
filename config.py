# Configuración de MetaTrader 5
MT5_LOGIN = 10006727030
MT5_PASSWORD = "X*J7QuIk"
MT5_INVESTOR = "*5NaLiNo"
MT5_SERVER = "MetaQuotes-Demo"

# Configuración de trading EUR/USD Intraday - BREAKOUT
SYMBOL = "EURUSD"
LOT = 0.1
RISK_REWARD = 1.5  # Ratio más conservador para intraday
SL_PIPS = 16        # Stop loss ajustado para objetivo 1-2%
TP_PIPS = 24        # Take profit 1.5:1 (16 * 1.5 = 24 pips)

# Horarios optimizados para EUR/USD
NY_START = (8, 0)   # 8:00 AM NY
NY_END = (17, 0)    # 5:00 PM NY

# ESTRATEGIA BREAKOUT INTRADIARIO - Solo timeframes intradiarios
TIMEFRAMES_ESTRATEGIA = {
    'TENDENCIA_INTRADIARIA': ['M15'],     # Tendencia intradiaria
    'CONFIRMACION_BREAKOUT': ['M5'],      # Confirmación de breakout
    'TIMING_ENTRADA': ['M1']              # Timing preciso de entrada
}

# FILTROS OPTIMIZADOS para breakout intradiario - BALANCE PRECISIÓN/SEÑALES
ADX_MIN = 12        # ADX mínimo optimizado para mayor precisión
VOLUME_MIN = 0.5    # Volumen mínimo optimizado para confirmación
RSI_ENTRADA_COMPRA = 45  # RSI optimizado para entradas de compra
RSI_ENTRADA_VENTA = 55   # RSI optimizado para entradas de venta
ATR_MIN_PIPS = 1.0  # Volatilidad mínima optimizada
ATR_MAX_PIPS = 40   # Volatilidad máxima optimizada

# PARÁMETROS OPTIMIZADOS PARA MEJOR PRECISIÓN
PENDIENTE_MINIMA = 0.0001   # Pendiente mínima optimizada para mayor precisión
PENDIENTE_MAXIMA = -0.0001  # Pendiente máxima optimizada para mayor precisión

# ============================================================================
# 🚀 GESTIÓN DE RIESGO INTELIGENTE - OPTIMIZACIÓN AUTOMÁTICA
# ============================================================================

# STOP LOSS ADAPTATIVO BASADO EN ATR - AJUSTADO PARA INTRADIARIO
STOP_LOSS_ATR_MULTIPLIER = 1.0    # Stop Loss = 1 × ATR (más conservador)
STOP_LOSS_MIN_PIPS = 8             # Stop Loss mínimo = 8 pips (protección básica)
STOP_LOSS_MAX_PIPS = 15            # Stop Loss máximo = 15 pips (realista para intradiario)

# TAKE PROFIT DINÁMICO CON RATIO RIESGO/BENEFICIO REALISTA
TAKE_PROFIT_RATIO = 2.0            # Take Profit = 2 × Stop Loss (ratio 1:2)
TAKE_PROFIT_MIN_PIPS = 16          # Take Profit mínimo = 16 pips (ganancia mínima)
TAKE_PROFIT_MAX_PIPS = 30          # Take Profit máximo = 30 pips (realista para intradiario)

# TRAILING STOP AUTOMÁTICO PARA PROTEGER GANANCIAS
TRAILING_STOP_ACTIVAR_PIPS = 10    # Activar trailing cuando ganancia > 10 pips
TRAILING_STOP_ATR_MULTIPLIER = 1.0 # Trailing = 1 × ATR (seguimiento dinámico)
TRAILING_STOP_MIN_PIPS = 3         # Trailing mínimo = 3 pips (protección básica)

# GESTIÓN DE POSICIÓN DINÁMICA - CONSERVADORA
POSITION_SIZE_RISK_PERCENT = 1.0   # Riesgo máximo por operación = 1% del balance
POSITION_SIZE_MAX_LOTS = 0.5       # Lote máximo por operación = 0.5
POSITION_SIZE_MIN_LOTS = 0.01      # Lote mínimo por operación = 0.01

# FILTROS DE TENDENCIA AVANZADOS
TREND_CONFIRMATION_TIMEFRAMES = ['H1', 'H4', 'D1']  # Múltiples timeframes para confirmar tendencia
TREND_STRENGTH_MIN_ADX = 25        # ADX mínimo para confirmar tendencia fuerte
TREND_MOMENTUM_RSI_MIN = 30        # RSI mínimo para confirmar momentum
TREND_MOMENTUM_RSI_MAX = 70        # RSI máximo para confirmar momentum

# VALIDACIÓN DE VOLUMEN EN TIEMPO REAL
VOLUME_SPIKE_MULTIPLIER = 1.2      # Volumen debe ser 1.2x mayor que el promedio (MÁS FLEXIBLE)
VOLUME_CONFIRMATION_PERIODS = 20    # Períodos para calcular volumen promedio
VOLUME_MIN_ABSOLUTE = 50           # Volumen mínimo absoluto (tick volume) - MÁS FLEXIBLE

# TIMING DE ENTRADA ULTRA PRECISO (M1)
ENTRY_TIMING_RSI_OVERBOUGHT = 80   # RSI M1 para evitar entradas en sobrecompra (MÁS FLEXIBLE)
ENTRY_TIMING_RSI_OVERSOLD = 20     # RSI M1 para evitar entradas en sobreventa (MÁS FLEXIBLE)
ENTRY_TIMING_VOLUME_MIN = 0.5      # Volumen mínimo M1 para confirmar entrada (MÁS FLEXIBLE)
ENTRY_TIMING_ATR_MIN = 0.5         # ATR mínimo M1 para confirmar volatilidad (MÁS FLEXIBLE)

# RATIOS DE RIESGO/BENEFICIO DINÁMICOS
RISK_REWARD_RATIO_MIN = 2.0        # Ratio mínimo 1:2
RISK_REWARD_RATIO_TARGET = 3.0     # Ratio objetivo 1:3
RISK_REWARD_RATIO_MAX = 5.0        # Ratio máximo 1:5

# PROTECCIÓN CONTRA DRAWDOWN
MAX_DRAWDOWN_PERCENT = 5.0         # Drawdown máximo permitido = 5%
MAX_CONSECUTIVE_LOSSES = 5         # Máximo 5 pérdidas consecutivas
BREAK_EVEN_ACTIVATION_PIPS = 8     # Activar break-even cuando ganancia > 8 pips

# Configuración de breakout
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
    (8, 30),   # Apertura NY
    (9, 0),    # 9:00 AM NY
    (10, 0),   # 10:00 AM NY
    (14, 0),   # 2:00 PM NY (London close)
    (15, 0),   # 3:00 PM NY
    (16, 0),   # 4:00 PM NY
] 