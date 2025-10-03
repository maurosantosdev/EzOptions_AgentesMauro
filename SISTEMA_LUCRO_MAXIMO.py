#!/usr/bin/env python3
"""
SISTEMA DE TRADING LUCRATIVO - VERSÃO OTIMIZADA
Sistema completo com 14 agentes melhorado para máxima lucratividade
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_completo_14_agentes import SistemaCompletoAgentes
import time
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_lucrativo.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal do sistema lucrativo"""
    print("=" * 60)
    print("SISTEMA DE TRADING LUCRATIVO - 14 AGENTES OTIMIZADOS")
    print("=" * 60)
    print()
    print("Melhorias implementadas:")
    print("  - Limite de confianca reduzido para 45%")
    print("  - Filtros de horario otimizados")
    print("  - Sistema de recuperacao de perdas (Martingale inteligente)")
    print("  - Gerenciamento dinamico de lot size")
    print("  - Filtro de volatilidade minima")
    print("  - Analise melhorada com forca de sinais")
    print("  - Stop loss e take profit otimizados")
    print()

    # Configuração otimizada para lucratividade
    config = {
        'name': 'SistemaLucrativo14Agentes',
        'symbol': 'US100',
        'magic_number': 234001,
        'lot_size': 0.03
    }

    # Criar e iniciar o sistema
    sistema = SistemaCompletoAgentes(config)

    try:
        logger.info("Iniciando sistema lucrativo...")
        sistema.start()

        print("Sistema iniciado com sucesso!")
        print("Monitore o arquivo 'sistema_lucrativo.log' para acompanhar as operacoes")
        print()
        print("DICAS PARA MAXIMIZAR LUCROS:")
        print("  - Mantenha o sistema rodando durante horarios de alta volatilidade")
        print("  - Nao interrompa operacoes consecutivas de recuperacao")
        print("  - Monitore o PnL diario para ajustes manuais se necessario")
        print()

        # Manter o programa rodando
        while sistema.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupcao detectada pelo usuario")
        print("\nEncerrando sistema...")
    except Exception as e:
        logger.error(f"Erro critico no sistema: {e}")
        print(f"\nErro critico: {e}")
    finally:
        sistema.stop()
        sistema.join()
        print("Sistema encerrado")

if __name__ == '__main__':
    main()