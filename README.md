# Análise de Resenhas com Detectores de IA

Este programa analisa resenhas de livros usando duas APIs de detecção de texto gerado por IA: GPTZero e ZeroGPT.

## Funcionalidades

### 1. Análise Individual
Para cada participante, o programa:
- Lê as resenhas da pasta "Resumos"
- Analisa cada resenha usando GPTZero e ZeroGPT
- Gera um relatório Excel individual com:
  - Probabilidades de ser texto de IA
  - Níveis de confiança
  - Classificações
  - Sentenças suspeitas
  - Formatação condicional por cores (verde=humano, vermelho=IA)
- Gera um gráfico de dispersão comparando os scores dos dois detectores

### 2. Análise Consolidada
Após processar todos os participantes, gera:
- Um relatório Excel consolidado com:
  - Total de resenhas por participante
  - Contagem de resenhas com alta probabilidade de IA (>80%, >60%, >40%)
  - Percentual de resenhas marcadas como IA
  - Médias dos scores de cada detector
- Dois gráficos:
  - Dispersão: comparando médias dos detectores por participante
  - Barras: ranking de participantes por % de resenhas marcadas como IA

## Estrutura do Projeto

- `main.py`: Arquivo principal de execução
- `analisador_ia.py`: Processamento e geração de relatórios individuais
- `analisador_consolidado.py`: Geração do relatório consolidado
- `detector_gpt_zero.py`: Interface com API GPTZero
- `detector_zero_gpt.py`: Interface com API ZeroGPT
- `config.py`: Configurações e chaves das APIs

## Métricas Principais

### GPTZero
- `GPTZero_Prob_IA`: Probabilidade do texto ser inteiramente IA (0-1)
- `GPTZero_Categoria_Confianca`: Nível de confiança (high/medium/low)
- `GPTZero_Classificacao`: Classificação final (HUMAN_ONLY/MIXED/AI_ONLY)

### ZeroGPT
- `ZeroGPT_Porcentagem_IA`: Porcentagem do texto identificada como IA (0-100%)
- `ZeroGPT_Feedback`: Análise detalhada do texto
- `ZeroGPT_Sentencas_IA`: Sentenças específicas identificadas como IA

## Estrutura de Pastas

```
projeto/
│
├── Resumos/                    # Pasta raiz dos textos
│   ├── Participante1/         # Uma pasta por participante
│   │   ├── resenha1.txt      # Arquivos de texto com as resenhas
│   │   └── resenha2.txt
│   ├── Participante2/
│   │   └── ...
│   └── Relatórios/           # Gerada automaticamente
│       ├── relatório_Participante1.xlsx
│       ├── grafico_dispersao_Participante1.png
│       ├── relatorio_consolidado.xlsx
│       ├── grafico_dispersao_consolidado.png
│       └── grafico_barras_consolidado.png
│
├── logs/                      # Logs de execução (gerada automaticamente)
│   └── detector_ia.log
│
├── main.py                    # Arquivos do programa
├── analisador_ia.py
├── analisador_consolidado.py
├── detector_gpt_zero.py
├── detector_zero_gpt.py
└── config.py                  # Arquivo de configuração (criar baseado no exemplo)
```

### Preparação do Ambiente

1. Clone o repositório
2. Crie a pasta `Resumos` na raiz do projeto
3. Dentro de `Resumos`, crie uma pasta para cada participante
4. Coloque os arquivos .txt das resenhas nas pastas dos participantes
5. Copie `config.example.py` para `config.py` e configure suas chaves de API
6. Execute o programa

As pastas `logs` e `Resumos/Relatórios` serão criadas automaticamente durante a execução.

### Formato dos Arquivos

- Resenhas devem estar em formato .txt
- Nome do arquivo será usado como identificador da resenha
- Encoding UTF-8 recomendado
- Uma resenha por arquivo

## Como Usar

1. Configure as chaves das APIs no arquivo `config.py`
2. Coloque as resenhas na pasta "Resumos" em subpastas por participante
3. Execute o programa:
   ```bash
   python main.py
   ```
4. Os relatórios serão gerados na pasta "Relatórios"

## Requisitos

- Python 3.8+
- Bibliotecas: pandas, matplotlib, openpyxl, requests
- Chaves de API válidas para GPTZero e ZeroGPT

## Formatação dos Relatórios

### Relatórios Individuais
- Cabeçalhos coloridos por detector (azul=GPTZero, verde=ZeroGPT)
- Formatação condicional em degradê (verde→amarelo→vermelho)
- Células formatadas para melhor visualização
- Gráfico de dispersão comparando scores

### Relatório Consolidado
- Todas as métricas importantes em um único lugar
- Colunas ajustadas para legibilidade
- Gráficos de dispersão e barras para visualização rápida
- Ordenação por percentual de resenhas marcadas como IA

## Notas
- O programa processa resenhas em lotes para respeitar limites de API
- Inclui tratamento de erros e logging detalhado
- Formatação visual otimizada para análise rápida
- Gráficos com escalas padronizadas para comparação consistente 

## Arquivos Sensíveis

### config.py
Este arquivo contém as chaves de API e foi excluído do repositório por segurança. Crie-o com a seguinte estrutura:

```python
# config.py
GPT_ZERO_KEY = "sua_chave_gptzero_aqui"
ZERO_GPT_KEY = "sua_chave_zerogpt_aqui"
```
> ⚠️ **IMPORTANTE**: Nunca compartilhe ou comite o arquivo `config.py` com suas chaves de API!

