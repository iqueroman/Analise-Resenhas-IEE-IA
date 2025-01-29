import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment

class AnalisadorConsolidado:
    def __init__(self, pasta_relatorios: Path):
        self.pasta_relatorios = pasta_relatorios
        self.logger = logging.getLogger('detector_ia')

    def gerar_relatorio_consolidado(self):
        """
        Gera relatório consolidado de todos os participantes
        """
        try:
            # Lista todos os arquivos Excel na pasta de relatórios
            arquivos_excel = list(self.pasta_relatorios.glob('relatório_*.xlsx'))
            
            resultados = []
            for arquivo in arquivos_excel:
                # Extrai nome do participante do nome do arquivo
                participante = arquivo.stem.replace('relatório_', '')
                
                # Lê o arquivo Excel
                df = pd.read_excel(arquivo)
                
                # Calcula as métricas existentes
                total_resenhas = len(df)
                total_gptzero_80 = len(df[df['GPTZero_Prob_IA'] >= 0.80])
                total_zerogpt_80 = len(df[df['ZeroGPT_Porcentagem_IA'] >= 80])
                total_gptzero_60 = len(df[df['GPTZero_Prob_IA'] >= 0.60])
                total_zerogpt_60 = len(df[df['ZeroGPT_Porcentagem_IA'] >= 60])
                media_gptzero = df['GPTZero_Prob_IA'].mean()
                media_zerogpt = df['ZeroGPT_Porcentagem_IA'].mean()
                
                # Novas métricas
                total_gptzero_40 = len(df[df['GPTZero_Prob_IA'] >= 0.40])
                total_zerogpt_40 = len(df[df['ZeroGPT_Porcentagem_IA'] >= 40])
                
                # Total de resenhas marcadas por qualquer detector (>=40)
                marcadas_ia = df[(df['GPTZero_Prob_IA'] >= 0.40) | 
                               (df['ZeroGPT_Porcentagem_IA'] >= 40)]
                total_marcadas_ia = len(marcadas_ia)
                
                # Percentual de resenhas marcadas
                percentual_marcadas = (total_marcadas_ia / total_resenhas * 100) if total_resenhas > 0 else 0
                
                resultados.append({
                    'Participante': participante,
                    'Total_Resenhas': total_resenhas,
                    'Total_GPTZero_80': total_gptzero_80,
                    'Total_ZeroGPT_80': total_zerogpt_80,
                    'Total_GPTZero_60': total_gptzero_60,
                    'Total_ZeroGPT_60': total_zerogpt_60,
                    'Total_GPTZero_40': total_gptzero_40,
                    'Total_ZeroGPT_40': total_zerogpt_40,
                    'Total_Marcadas_IA': total_marcadas_ia,
                    'Percentual_Marcadas_>40': percentual_marcadas,
                    'Media_GPTZero': media_gptzero,
                    'Media_ZeroGPT': media_zerogpt
                })
            
            # Cria DataFrame consolidado
            df_consolidado = pd.DataFrame(resultados)
            
            # Ordena por percentual de resenhas marcadas
            df_consolidado = df_consolidado.sort_values('Percentual_Marcadas_>40', ascending=False)
            
            # Gera gráfico de dispersão original
            plt.figure(figsize=(10, 8))
            plt.scatter(df_consolidado['Media_GPTZero'], df_consolidado['Media_ZeroGPT'])
            
            # Adiciona rótulos para cada ponto
            for i, participante in enumerate(df_consolidado['Participante']):
                plt.annotate(participante, 
                           (df_consolidado['Media_GPTZero'].iloc[i], 
                            df_consolidado['Media_ZeroGPT'].iloc[i]))
            
            plt.xlabel('Média GPTZero_Prob_IA')
            plt.ylabel('Média ZeroGPT_Porcentagem_IA')
            plt.title('Comparação entre Detectores por Participante')
            plt.grid(True)
            
            # Define limites fixos para os eixos
            plt.xlim(0, 1)  # GPTZero vai de 0 a 1
            plt.ylim(0, 100)  # ZeroGPT vai de 0 a 100
            
            # Salva o gráfico de dispersão
            arquivo_grafico_dispersao = self.pasta_relatorios / 'grafico_dispersao_consolidado.png'
            plt.savefig(arquivo_grafico_dispersao)
            plt.close()
            
            # Gera novo gráfico de barras
            plt.figure(figsize=(12, 6))
            bars = plt.bar(df_consolidado['Participante'], df_consolidado['Percentual_Marcadas_>40'])
            
            # Adiciona rótulos nas barras
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.xlabel('Participante')
            plt.ylabel('% de Resenhas Marcadas como IA (>40%)')
            plt.title('Percentual de Resenhas Marcadas como IA por Participante')
            plt.tight_layout()
            
            # Salva o gráfico de barras
            arquivo_grafico_barras = self.pasta_relatorios / 'grafico_barras_consolidado.png'
            plt.savefig(arquivo_grafico_barras)
            plt.close()
            
            # Agora sim formata a coluna de percentual para mostrar % no Excel
            df_consolidado['Percentual_Marcadas_>40'] = df_consolidado['Percentual_Marcadas_>40'].apply(lambda x: f'{x:.1f}%')
            
            # Gera arquivo Excel com formatação
            arquivo_saida = self.pasta_relatorios / 'relatorio_consolidado.xlsx'
            with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                df_consolidado.to_excel(writer, index=False, sheet_name='Consolidado')
                
                # Ajusta largura das colunas
                worksheet = writer.sheets['Consolidado']
                for idx, col in enumerate(df_consolidado.columns):
                    # Encontra o comprimento máximo na coluna
                    max_length = max(
                        df_consolidado[col].astype(str).apply(len).max(),  # Maior valor
                        len(str(col))  # Tamanho do cabeçalho
                    )
                    # Ajusta a largura (um pouco maior para garantir a legibilidade)
                    worksheet.column_dimensions[get_column_letter(idx + 1)].width = max_length + 2

                # Formata cabeçalhos
                for cell in worksheet[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal='center', wrap_text=True)
            
            self.logger.info(f"Relatório consolidado gerado: {arquivo_saida}")
            self.logger.info(f"Gráficos gerados: {arquivo_grafico_dispersao}, {arquivo_grafico_barras}")
            
            return arquivo_saida, arquivo_grafico_dispersao, arquivo_grafico_barras
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório consolidado: {str(e)}", exc_info=True)
            raise 