from pathlib import Path
from analisador_consolidado import AnalisadorConsolidado
import logging

def configurar_logging():
    logger = logging.getLogger('detector_ia')
    logger.setLevel(logging.INFO)
    Path('logs').mkdir(exist_ok=True)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def main():
    logger = configurar_logging()
    pasta_relatorios = Path("Resumos/Relatórios")
    
    try:
        analisador = AnalisadorConsolidado(pasta_relatorios)
        analisador.gerar_relatorio_consolidado()
        logger.info("Relatório consolidado gerado com sucesso")
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise

if __name__ == "__main__":
    main() 