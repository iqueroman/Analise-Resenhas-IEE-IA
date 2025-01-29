import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

def configurar_logging():
    logger = logging.getLogger('detector_ia')
    logger.setLevel(logging.INFO)
    
    # Cria pasta de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    
    # Handler para arquivo
    fh = logging.FileHandler('logs/detector_ia.log', encoding='utf-8')
    fh.setLevel(logging.INFO)
    
    # Handler para console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

def gerar_grafico_barras(df, coluna, titulo, arquivo_saida):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(df['Participante'], df[coluna])
    
    # Adiciona rótulos nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Participante')
    plt.ylabel('% de Resenhas Marcadas como IA')
    plt.title(titulo)
    plt.tight_layout()
    
    plt.savefig(arquivo_saida)
    plt.close()

def gerar_grafico_barras_absoluto(df, coluna, titulo, arquivo_saida):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(df['Participante'], df[coluna])
    
    # Adiciona rótulos nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',  # Valor inteiro para contagem absoluta
                ha='center', va='bottom')
    
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Participante')
    plt.ylabel('Número de Resenhas Marcadas como IA')
    plt.title(titulo)
    plt.tight_layout()
    
    plt.savefig(arquivo_saida)
    plt.close()

def gerar_grafico_dispersao(df, arquivo_saida):
    plt.figure(figsize=(10, 8))
    # Normaliza ZeroGPT para escala 0-1
    plt.scatter(df['Media_ZeroGPT'] / 100, df['Media_GPTZero'])
    
    # Adiciona rótulos para cada ponto
    for i, participante in enumerate(df['Participante']):
        plt.annotate(participante, 
                   (df['Media_ZeroGPT'].iloc[i] / 100, 
                    df['Media_GPTZero'].iloc[i]))
    
    plt.xlabel('ZeroGPT_Porcentagem_IA (normalizado 0-1)')
    plt.ylabel('GPTZero_Prob_IA')
    plt.title('Comparação entre Detectores por Participante')
    plt.grid(True)
    
    plt.savefig(arquivo_saida)
    plt.close()

def gerar_grafico_dispersao_absoluto(pasta_relatorios, arquivo_saida):
    plt.figure(figsize=(10, 8))
    
    # Processa cada arquivo para obter contagens absolutas
    contagens = []
    for arquivo in pasta_relatorios.glob('relatório_*.xlsx'):
        if 'consolidado' not in arquivo.stem:
            participante = arquivo.stem.replace('relatório_', '')
            df = pd.read_excel(arquivo)
            
            # Conta resenhas acima de 0.40 para cada detector
            total_gptzero = len(df[df['GPTZero_Prob_IA'] >= 0.40])
            total_zerogpt = len(df[df['ZeroGPT_Porcentagem_IA'] >= 40])
            
            contagens.append({
                'Participante': participante,
                'Total_GPTZero_40': total_gptzero,
                'Total_ZeroGPT_40': total_zerogpt
            })
    
    df_contagens = pd.DataFrame(contagens)
    
    # Plota o gráfico com eixos invertidos
    plt.scatter(df_contagens['Total_ZeroGPT_40'], df_contagens['Total_GPTZero_40'])
    
    # Adiciona rótulos para cada ponto
    for i, participante in enumerate(df_contagens['Participante']):
        plt.annotate(participante, 
                   (df_contagens['Total_ZeroGPT_40'].iloc[i], 
                    df_contagens['Total_GPTZero_40'].iloc[i]))
    
    plt.xlabel('Número de Resenhas com ZeroGPT_Porcentagem_IA >= 40')
    plt.ylabel('Número de Resenhas com GPTZero_Prob_IA >= 0.40')
    plt.title('Comparação do Número de Resenhas Marcadas por Cada Detector')
    plt.grid(True)
    
    # Força o uso de números inteiros nos eixos
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    plt.savefig(arquivo_saida)
    plt.close()

def gerar_grafico_dispersao_individual(df, participante, arquivo_saida):
    plt.figure(figsize=(10, 8))
    # Normaliza ZeroGPT para escala 0-1
    plt.scatter(df['ZeroGPT_Porcentagem_IA'] / 100, df['GPTZero_Prob_IA'])
    
    # Adiciona rótulos para cada ponto
    for i, livro in enumerate(df['Livro/curso']):
        plt.annotate(livro, 
                   (df['ZeroGPT_Porcentagem_IA'].iloc[i] / 100, 
                    df['GPTZero_Prob_IA'].iloc[i]),
                   fontsize=8)
    
    plt.xlabel('ZeroGPT_Porcentagem_IA (normalizado 0-1)')
    plt.ylabel('GPTZero_Prob_IA')
    plt.title(f'Comparação entre Detectores - {participante}')
    plt.grid(True)
    
    # Define limites fixos para os eixos (agora ambos 0-1)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    
    plt.savefig(arquivo_saida, bbox_inches='tight', dpi=300)
    plt.close()

def main():
    logger = configurar_logging()
    pasta_relatorios = Path("Resumos/Relatórios")
    
    try:
        # Gera gráficos individuais
        for arquivo in pasta_relatorios.glob('relatório_*.xlsx'):
            if 'consolidado' not in arquivo.stem:
                participante = arquivo.stem.replace('relatório_', '')
                df_individual = pd.read_excel(arquivo)
                
                # Gera gráfico de dispersão individual
                gerar_grafico_dispersao_individual(
                    df_individual,
                    participante,
                    pasta_relatorios / f'grafico_dispersao_{participante}.png'
                )
                logger.info(f"Gerado gráfico de dispersão para {participante}")
        
        # Lê o relatório consolidado
        df = pd.read_excel(pasta_relatorios / "relatorio_consolidado.xlsx")
        
        # Gera gráfico de dispersão (sem escalas fixas)
        gerar_grafico_dispersao(df, pasta_relatorios / 'grafico_dispersao_consolidado.png')
        logger.info("Gerado gráfico de dispersão consolidado")
        
        # Processa cada arquivo individual para calcular percentuais
        resultados = []
        for arquivo in pasta_relatorios.glob('relatório_*.xlsx'):
            if 'consolidado' not in arquivo.stem:
                participante = arquivo.stem.replace('relatório_', '')
                df_individual = pd.read_excel(arquivo)
                total_resenhas = len(df_individual)
                
                if total_resenhas > 0:  # Evita divisão por zero
                    # Calcula percentuais para diferentes thresholds
                    total_40 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.40) | 
                                               (df_individual['ZeroGPT_Porcentagem_IA'] >= 40)])
                    total_60 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.60) | 
                                               (df_individual['ZeroGPT_Porcentagem_IA'] >= 60)])
                    total_80 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.80) | 
                                               (df_individual['ZeroGPT_Porcentagem_IA'] >= 80)])
                    
                    resultados.append({
                        'Participante': participante,
                        'Percentual_Marcadas_>40': (total_40 / total_resenhas) * 100,
                        'Percentual_Marcadas_>60': (total_60 / total_resenhas) * 100,
                        'Percentual_Marcadas_>80': (total_80 / total_resenhas) * 100
                    })
        
        # Cria DataFrame com os resultados
        df_resultados = pd.DataFrame(resultados)
        
        # Adiciona contagem absoluta aos resultados
        for arquivo in pasta_relatorios.glob('relatório_*.xlsx'):
            if 'consolidado' not in arquivo.stem:
                participante = arquivo.stem.replace('relatório_', '')
                df_individual = pd.read_excel(arquivo)
                
                # Calcula contagens absolutas para diferentes thresholds
                total_40 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.40) | 
                                           (df_individual['ZeroGPT_Porcentagem_IA'] >= 40)])
                total_60 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.60) | 
                                           (df_individual['ZeroGPT_Porcentagem_IA'] >= 60)])
                total_80 = len(df_individual[(df_individual['GPTZero_Prob_IA'] >= 0.80) | 
                                           (df_individual['ZeroGPT_Porcentagem_IA'] >= 80)])
                
                # Atualiza o dicionário existente com as contagens absolutas
                idx = df_resultados[df_resultados['Participante'] == participante].index[0]
                df_resultados.loc[idx, 'Total_Marcadas_>40'] = total_40
                df_resultados.loc[idx, 'Total_Marcadas_>60'] = total_60
                df_resultados.loc[idx, 'Total_Marcadas_>80'] = total_80
        
        # Gera os três gráficos de barra com percentuais
        for threshold in ['40', '60', '80']:
            coluna = f'Percentual_Marcadas_>{threshold}'
            df_ordenado = df_resultados.sort_values(coluna, ascending=False)
            
            gerar_grafico_barras(
                df_ordenado,
                coluna,
                f'Percentual de Resenhas Marcadas como IA (>{threshold}%)',
                pasta_relatorios / f'grafico_barras_consolidado_{threshold}.png'
            )
            logger.info(f"Gerado gráfico percentual para threshold >{threshold}%")
        
        # Gera os três novos gráficos de barra com números absolutos
        for threshold in ['40', '60', '80']:
            coluna = f'Total_Marcadas_>{threshold}'
            df_ordenado = df_resultados.sort_values(coluna, ascending=False)
            
            gerar_grafico_barras_absoluto(
                df_ordenado,
                coluna,
                f'Número de Resenhas Marcadas como IA (>{threshold}%)',
                pasta_relatorios / f'grafico_barras_consolidado_{threshold}_absoluto.png'
            )
            logger.info(f"Gerado gráfico absoluto para threshold >{threshold}%")
        
        # Gera o novo gráfico de dispersão com números absolutos
        gerar_grafico_dispersao_absoluto(
            pasta_relatorios,
            pasta_relatorios / 'grafico_dispersao_consolidado_absoluto.png'
        )
        logger.info("Gerado gráfico de dispersão consolidado com números absolutos")
        
        logger.info("Geração de gráficos extras concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos extras: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 