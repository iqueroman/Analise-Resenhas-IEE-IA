import os
import pandas as pd
from pathlib import Path
import re
import unicodedata
import docx
import logging
from datetime import datetime

def configurar_logging():
    """
    Configura o sistema de logging para arquivo e console
    """
    # Cria pasta de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    log_file = f"logs/detector_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configura o formato do log
    formato = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formato)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)
    
    # Configura o logger
    logger = logging.getLogger('detector_ia')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def corrigir_palavras_bugadas(texto):
    """
    Corrige palavras com caracteres bugados comuns
    """
    # Corrige aspas bugadas (? no lugar de ")
    texto = re.sub(r'\?([^\?]+)\?', r'"\1"', texto)
    
    # Lista de correções comuns
    correcoes = {
        'â€™': "'",    # apóstrofo bugado
        'â€"': "-",    # hífen bugado
        'â€œ': '"',    # aspas de abertura bugadas
        'â€': '"',     # aspas de fechamento bugadas
        '\x96': '-',   # hífen especial
        '\x93': '"',   # aspas especiais
        '\x94': '"',   # aspas especiais
        '…': '...',    # reticências
    }
    
    for bugado, correto in correcoes.items():
        texto = texto.replace(bugado, correto)
    
    return texto

def ler_arquivo_docx(caminho):
    """
    Lê o conteúdo de um arquivo .docx
    """
    doc = docx.Document(caminho)
    texto_completo = []
    for paragrafo in doc.paragraphs:
        texto_completo.append(paragrafo.text)
    return '\n'.join(texto_completo)

def normalizar_texto(texto):
    """
    Normaliza o texto preservando acentuação e formatação básica
    """
    texto = corrigir_palavras_bugadas(texto)
    texto = ''.join(char for char in texto if not unicodedata.category(char).startswith('C') 
                    or char in ['\n', '\t'])
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', texto)
    texto = re.sub(r' +', ' ', texto)
    texto = re.sub(r'\n+', '\n', texto)
    return texto.strip()

def ler_resumos(pasta_base, participante_filtro=None):
    """
    Lê os resumos de cada participante das pastas existentes
    Retorna: dict com {participante: [(nome_livro, texto_normalizado)]}
    """
    logger = logging.getLogger('detector_ia')
    resultados = {}
    pasta_base = Path(pasta_base)
    
    if not pasta_base.exists():
        logger.error(f"Pasta base '{pasta_base}' não encontrada")
        return resultados
    
    logger.info(f"Iniciando processamento da pasta: {pasta_base}")
    
    if participante_filtro:
        pasta_participante = pasta_base / participante_filtro
        if not pasta_participante.exists() or not pasta_participante.is_dir():
            logger.error(f"Pasta do participante '{participante_filtro}' não encontrada")
            return resultados
        pastas_para_processar = [pasta_participante]
    else:
        pastas_para_processar = [p for p in pasta_base.iterdir() 
                                if p.is_dir() and p.name != "Relatórios"]
    
    for pasta_participante in pastas_para_processar:
        nome_participante = pasta_participante.name
        logger.info(f"Processando participante: {nome_participante}")
        resumos = []
        
        for extensao in ['*.txt', '*.docx']:
            for arquivo in pasta_participante.glob(extensao):
                logger.info(f"Processando arquivo: {arquivo}")
                try:
                    if arquivo.suffix.lower() == '.txt':
                        with open(arquivo, 'r', encoding='utf-8') as f:
                            texto = f.read()
                    else:  # .docx
                        texto = ler_arquivo_docx(arquivo)
                    
                    texto_normalizado = normalizar_texto(texto)
                    nome_livro = arquivo.stem
                    resumos.append((nome_livro, texto_normalizado))
                    logger.info(f"Arquivo processado com sucesso: {arquivo}")
                    
                except UnicodeDecodeError as e:
                    logger.error(f"Erro de encoding ao ler {arquivo}: {str(e)}")
                    try:
                        with open(arquivo, 'r', encoding='latin-1') as f:
                            texto = f.read()
                        texto_normalizado = normalizar_texto(texto)
                        nome_livro = arquivo.stem
                        resumos.append((nome_livro, texto_normalizado))
                        logger.info(f"Arquivo recuperado com encoding alternativo: {arquivo}")
                    except Exception as e2:
                        logger.error(f"Falha na recuperação com encoding alternativo: {str(e2)}")
                
                except Exception as e:
                    logger.error(f"Erro ao processar {arquivo}: {str(e)}", exc_info=True)
        
        if resumos:
            resultados[nome_participante] = resumos
            logger.info(f"Participante {nome_participante}: {len(resumos)} resumos processados")
        else:
            logger.warning(f"Nenhum resumo encontrado para o participante: {nome_participante}")
    
    return resultados

def gerar_relatório_excel(resultados, pasta_base):
    """
    Gera relatório Excel para cada participante
    """
    logger = logging.getLogger('detector_ia')
    pasta_relatórios = Path(pasta_base) / "Relatórios"
    pasta_relatórios.mkdir(exist_ok=True)
    
    for participante, resumos in resultados.items():
        try:
            df = pd.DataFrame(resumos, columns=['Livro', 'Texto_Normalizado'])
            excel_file = pasta_relatórios / f"relatório_{participante}.xlsx"
            df.to_excel(excel_file, index=False)
            logger.info(f"Relatório gerado com sucesso para {participante}: {excel_file}")
        except Exception as e:
            logger.error(f"Erro ao gerar relatório para {participante}: {str(e)}", exc_info=True) 