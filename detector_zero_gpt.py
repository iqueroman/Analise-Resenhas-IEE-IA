import logging
from typing import Dict, Any
import requests
from time import sleep, time

class ZeroGPTDetector:
    """
    Detector de texto gerado por IA usando a API ZeroGPT.
    
    A API ZeroGPT fornece:
    1. Score de Detecção:
       - Valor entre 0 e 100 indicando a probabilidade de ser IA
       - Quanto maior o valor, maior a chance de ser texto de IA
    
    2. Análise de Confiança:
       - Indica o nível de confiança da análise
       - Baseado no tamanho e qualidade do texto analisado
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger('detector_ia')
        self.base_url = "https://api.zerogpt.com/api/detect/detectText"  # Endpoint correto
        self.headers = {
            "ApiKey": api_key,  # Header correto
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
        Analisa um texto usando a API ZeroGPT.
        
        Retorna um dicionário com os resultados da análise:
        
        - success (bool):
          Indica se a análise foi bem sucedida
        
        - input_text (str):
          Texto que foi analisado
        
        - textWords (int):
          Número total de palavras no texto
        
        - aiWords (int):
          Número de palavras identificadas como IA
        
        - fakePercentage (float):
          Porcentagem do texto identificada como IA
        
        - sentences (list):
          Lista de sentenças analisadas
        
        - feedback (str):
          Feedback detalhado da análise
        """
        try:
            self._esperar_rate_limit()
            
            payload = {
                "text": "",
                "input_text": texto
            }
            
            # Log da requisição
            self.logger.info(f"Enviando requisição para ZeroGPT - URL: {self.base_url}")
            self.logger.debug(f"Headers: {self.headers}")
            self.logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            # Log da resposta
            self.logger.info(f"Status code: {response.status_code}")
            self.logger.debug(f"Resposta bruta: {response.text}")
            
            if response.status_code == 429:
                self.logger.warning("Rate limit atingido, aguardando 60 segundos...")
                sleep(60)
                return self.analisar_texto(texto)
            
            response.raise_for_status()
            
            # Verifica se a resposta tem conteúdo
            if not response.text:
                raise ValueError("API retornou resposta vazia")
            
            data = response.json()
            
            # Processa e formata a resposta
            if data.get('success'):
                resultado = {
                    'success': data.get('success', False),
                    'input_text': data.get('data', {}).get('input_text', ''),
                    'total_palavras': data.get('data', {}).get('textWords', 0),
                    'palavras_ia': data.get('data', {}).get('aiWords', 0),
                    'porcentagem_ia': data.get('data', {}).get('fakePercentage', 0),
                    'sentencas': data.get('data', {}).get('sentences', []),
                    'sentencas_ia': data.get('data', {}).get('h', []),  # Array de sentenças mais prováveis de serem IA
                    'feedback': data.get('data', {}).get('feedback', ''),
                    'mensagem': data.get('message', '')
                }
            else:
                self.logger.warning(f"API retornou erro: {data.get('message')}")
                resultado = {
                    'success': False,
                    'input_text': texto,
                    'total_palavras': 0,
                    'palavras_ia': 0,
                    'porcentagem_ia': 0,
                    'sentencas': [],
                    'sentencas_ia': [],
                    'feedback': '',
                    'mensagem': data.get('message', 'Erro na análise')
                }
            
            return resultado
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na chamada à API ZeroGPT: {str(e)}")
            self.logger.error(f"Detalhes da requisição: URL={self.base_url}, Headers={self.headers}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao processar resposta da API ZeroGPT: {str(e)}")
            raise 