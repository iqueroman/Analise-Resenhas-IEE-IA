import sys
import logging
from processador_texto import (
    configurar_logging, 
    ler_resumos, 
    gerar_relatório_excel
)
from analisador_ia import AnalisadorIA, gerar_relatorio_completo
from pathlib import Path
import openpyxl
from time import sleep
import time
from config import GPT_ZERO_KEY, ZERO_GPT_KEY  # Importa as chaves do arquivo de configuração
from analisador_consolidado import AnalisadorConsolidado

def main():
    logger = configurar_logging()
    
    # Aceita nome do participante como argumento opcional
    participante_teste = sys.argv[1] if len(sys.argv) > 1 else None
    
    pasta_base = Path("Resumos")
    try:
        # Processa os textos
        resultados = ler_resumos(pasta_base, participante_teste)
        
        # Inicializa analisador com as chaves do config
        analisador = AnalisadorIA(GPT_ZERO_KEY, ZERO_GPT_KEY)
        
        # Processa cada participante
        for participante, resumos in resultados.items():
            logger.info(f"Analisando textos de: {participante}")
            
            # Analisa todos os resumos do participante
            resultados_analise = analisador.analisar_resumos(resumos)
            
            # Gera relatório com todos os dados
            gerar_relatorio_completo(resultados_analise, pasta_base, participante)
        
        logger.info("Processamento concluído")
        
        # Após processar todos os participantes, gera relatório consolidado
        analisador_consolidado = AnalisadorConsolidado(pasta_base / "Relatórios")
        analisador_consolidado.gerar_relatorio_consolidado()
        
    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 