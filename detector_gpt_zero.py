import logging
from typing import Dict, Any
import requests
from time import sleep, time

class GPTZeroDetector:
    """
    Detector de texto gerado por IA usando a API GPTZero.
    
    A API GPTZero usa dois principais indicadores para detectar texto gerado por IA:
    
    1. Perplexidade (Perplexity):
       - Mede o quão "surpreso" o modelo está com o texto
       - Textos humanos tendem a ter alta perplexidade pois são mais imprevisíveis
       - Textos de IA tendem a ter baixa perplexidade pois são mais previsíveis/repetitivos
    
    2. Variação/Naturalidade (Burstiness):
       - Mede a variação na perplexidade entre diferentes partes do texto
       - Textos humanos tendem a ter alta variação (mais "bursts" de complexidade)
       - Textos de IA tendem a manter um nível mais constante de complexidade
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger('detector_ia')
        self.base_url = "https://api.gptzero.me/v2/predict/text"
        self.headers = {
            "accept": "application/json",
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        self.last_request_time = 0
        self.min_request_interval = 1  # segundos entre requisições
    
    def _esperar_rate_limit(self):
        """
        Garante um intervalo mínimo entre requisições
        """
        agora = time()
        tempo_desde_ultima = agora - self.last_request_time
        if tempo_desde_ultima < self.min_request_interval:
            sleep(self.min_request_interval - tempo_desde_ultima)
        self.last_request_time = time()
    
    def analisar_texto(self, texto: str) -> Dict[str, Any]:
        """
        Analisa um texto usando a API GPTZero.
        
        Retorna um dicionário com os resultados da análise:
        
        - version: Versão do detector usado na análise
        - scan_id: Identificador único do scan (pode ter múltiplos documentos)
        
        Dados do documento:
        - prob_media_ia: (0-1) Média das probabilidades de cada sentença ser gerada por IA
        - prob_classes: Probabilidades para cada classe:
          - ai: (0-1) Probabilidade de ser texto de IA
          - human: (0-1) Probabilidade de ser texto humano
          - mixed: (0-1) Probabilidade de ser texto misto
        - categoria_confianca: Confiança da predição:
          - "high": menos de 1% de taxa de erro
          - "medium": confiança moderada
          - "low": baixa confiança
        - pontuacao_confianca: Score normalizado de confiança (uso interno)
        - naturalidade_geral: Variação na perplexidade do documento (indicador de distinção IA/humano)
        - classe_prevista: Classificação com maior probabilidade:
          - "human": apenas texto humano
          - "ai": apenas texto de IA
          - "mixed": combinação de texto humano e IA
        - classificacao_documento: Classificação simplificada:
          - "HUMAN_ONLY": alta probabilidade de ser predominantemente humano
          - "MIXED": seções com forte assinatura de IA ou documento com fraca assinatura de IA
          - "AI_ONLY": documento inteiramente escrito por IA
        - mensagem_resultado: Mensagem principal da classificação
        """
        try:
            self._esperar_rate_limit()
            
            payload = {
                "document": texto,
                "multilingual": True
            }
            
            # Log da requisição
            self.logger.info(f"Enviando requisição para GPTZero - URL: {self.base_url}")
            self.logger.debug(f"Headers: {self.headers}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            # Log da resposta
            self.logger.info(f"Status code GPTZero: {response.status_code}")
            self.logger.debug(f"Resposta bruta GPTZero: {response.text}")
            
            # Se houver erro de rate limit, espera e tenta novamente
            if response.status_code == 429:
                self.logger.warning("Rate limit atingido, aguardando 60 segundos...")
                sleep(60)
                return self.analisar_texto(texto)
            
            response.raise_for_status()
            data = response.json()
            doc = data.get('documents', [{}])[0]  # Pega o primeiro documento
            
            # Processa e formata a resposta
            resultado = {
                'version': data.get('version', ''),
                'scan_id': data.get('scanId', ''),
                'documento': {
                    'prob_media_ia': doc.get('average_generated_prob', 0),
                    'prob_classes': {
                        'ai': doc.get('class_probabilities', {}).get('ai', 0),
                        'human': doc.get('class_probabilities', {}).get('human', 0),
                        'mixed': doc.get('class_probabilities', {}).get('mixed', 0)
                    },
                    'categoria_confianca': doc.get('confidence_category', ''),
                    'pontuacao_confianca': doc.get('confidence_score', 0),
                    'classe_prevista': doc.get('predicted_class', ''),
                    'classificacao_documento': doc.get('document_classification', ''),
                    'mensagem_resultado': doc.get('result_message', '')
                },
                'sentencas': [
                    {
                        'texto': s.get('sentence', ''),
                        'prob_ia': s.get('generated_prob', 0),
                        'perplexidade': s.get('perplexity', 0),
                        'destacar_ia': s.get('highlight_sentence_for_ai', False)
                    }
                    for s in doc.get('sentences', [])
                ]
            }
            
            return resultado
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na chamada à API GPTZero: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao processar resposta da API GPTZero: {str(e)}")
            raise 