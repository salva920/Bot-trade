from broker.mt5_connector import conectar_mt5, obtener_datos, enviar_orden
from strategy.interbank import detectar_entrada
from utils.time_utils import es_horario_ny
import MetaTrader5 as mt5
import time


def main():
    print("Iniciando bot de trading con confluencia de 4 timeframes...")
    
    if not conectar_mt5():
        print("Error conectando a MT5")
        return
        
    print("Conectado a MetaTrader 5")

    last_bar_time = None
    last_trade_time = 0
    last_trade_side = None
    COOLDOWN_SECONDS = 15 * 60
    
    while True:
        try:
            if es_horario_ny():
                print("Verificando señales de trading...")
                
                # Obtener datos de todos los timeframes
                df_m5 = obtener_datos(timeframe=mt5.TIMEFRAME_M5, n=100)
                df_m15 = obtener_datos(timeframe=mt5.TIMEFRAME_M15, n=100)
                df_h1 = obtener_datos(timeframe=mt5.TIMEFRAME_H1, n=100)
                df_h4 = obtener_datos(timeframe=mt5.TIMEFRAME_H4, n=100)
                df_d1 = obtener_datos(timeframe=mt5.TIMEFRAME_D1, n=100)
                
                if df_m5 is None or df_m5.empty:
                    print("Error obteniendo datos M5")
                    time.sleep(30)
                    continue

                # Detectar cambio de vela (usando M5 como referencia)
                current_bar_time = int(df_m5.iloc[-1]['time']) if 'time' in df_m5.columns else None
                is_new_bar = (current_bar_time is not None and current_bar_time != last_bar_time)

                # Usar confluencia de 4 timeframes
                señal = detectar_entrada(
                    df=df_m5,  # Timeframe principal para análisis
                    df_m5=df_m5,
                    df_m15=df_m15,
                    df_h1=df_h1,
                    df_h4=df_h4,
                    df_d1=df_d1,
                    debug=True  # Activar debug para ver las tendencias
                )
                
                if señal:
                    # Compatibilidad con retorno (tipo, precio) o (tipo, precio, factor)
                    if len(señal) == 3:
                        tipo, precio, factor_riesgo = señal
                    else:
                        tipo, precio = señal
                        factor_riesgo = 1.0

                    now = int(time.time())
                    in_cooldown = (now - last_trade_time) < COOLDOWN_SECONDS

                    if not is_new_bar:
                        print("Misma vela: se omite envío de orden.")
                    elif in_cooldown and last_trade_side == tipo:
                        print("En cooldown para la misma dirección; no se envía orden.")
                    else:
                        print(f"Señal detectada: {tipo} a {precio} (factor riesgo: {factor_riesgo:.2f})")
                        if enviar_orden(tipo, precio, factor_riesgo):
                            print("Orden ejecutada exitosamente")
                            last_trade_time = now
                            last_trade_side = tipo
                            last_bar_time = current_bar_time
                        else:
                            print("Error al ejecutar la orden")
                            # Aun así actualizamos la vela para no spamear durante la misma barra
                            last_bar_time = current_bar_time
                else:
                    print("Sin señal válida.")
            else:
                print("Fuera del horario de trading de NY")
                
            # Esperar 30s para respuesta más ágil intradía
            time.sleep(30)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main() 