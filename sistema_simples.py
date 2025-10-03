import MetaTrader5 as mt5
import os
import time
import threading
from datetime import datetime
import pytz

# Configurações
login = int(os.getenv('MT5_LOGIN', '103486755'))
server = os.getenv('MT5_SERVER', 'FBS-Demo')
password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

class SistemaTradingSimples:
    def __init__(self):
        self.running = False
        self.magic_number = 234001
        
    def start(self):
        print('🚀 Iniciando sistema de trading SIMPLES e LEVE...')
        
        # Inicializar MT5
        if not mt5.initialize(login=login, server=server, password=password):
            print('❌ Falha ao inicializar MT5')
            return False
            
        # Verificar conta
        account_info = mt5.account_info()
        print(f'✅ Conta conectada: #{account_info.login}, Saldo: ${account_info.balance:.2f}')
        
        # Selecionar símbolo
        if not mt5.symbol_select('US100', True):
            print('❌ Não foi possível selecionar US100')
            return False
            
        print('✅ Sistema iniciado com sucesso - Aguardando oportunidades...')
        self.running = True
        
        # Loop principal
        while self.running:
            try:
                # Verificar horário de trading
                ny_tz = pytz.timezone('America/New_York')
                current_time_ny = datetime.now(ny_tz)
                
                # Horário comercial (09:00-16:00 NY)
                market_open = datetime.strptime('09:00:00', '%H:%M:%S').time()
                market_close = datetime.strptime('16:00:00', '%H:%M:%S').time()
                current_time = current_time_ny.time()
                
                is_trading_hour = market_open <= current_time < market_close and 0 <= current_time_ny.weekday() <= 4
                
                if is_trading_hour:
                    print(f'💡 [{current_time_ny.strftime("%H:%M:%S")}] Horário de trading - Verificando oportunidades...')
                    # Aqui iria a lógica de análise e negociação
                else:
                    print(f'⏳ [{current_time_ny.strftime("%H:%M:%S")}] Fora do horário de trading - Aguardando...')
                    
                time.sleep(30)  # Verificar a cada 30 segundos
                
            except KeyboardInterrupt:
                print('🛑 Interrupção detectada')
                break
            except Exception as e:
                print(f'❌ Erro: {e}')
                time.sleep(10)
                
        mt5.shutdown()
        print('✅ Sistema encerrado')

# Iniciar sistema
if __name__ == '__main__':
    sistema = SistemaTradingSimples()
    sistema.start()