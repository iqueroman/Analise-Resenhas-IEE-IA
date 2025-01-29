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
- Relatório Excel consolidado com métricas por participante
- Gráficos consolidados:
  - Dispersão comparando médias dos detectores
  - Dispersão comparando contagens absolutas >40%
  - Barras com percentuais >40%, >60% e >80%
  - Barras com números absolutos >40%, >60% e >80%

## Uso

### Análise Completa
```bash
python main.py
```

### Análise Individual
```bash
python main.py -p NOME_DO_PARTICIPANTE
```

### Apenas Relatório Consolidado
```bash
python gerar_consolidado.py
```

### Apenas Gráficos
```bash
python gerar_graficos_extras.py
```

## Estrutura de Pastas
```
Resumos/
  ├── Participante1/
  │   ├── resenha1.txt
  │   └── resenha2.txt
  ├── Participante2/
  │   └── ...
  └── Relatórios/
      ├── relatório_Participante1.xlsx
      ├── relatório_Participante2.xlsx
      └── relatorio_consolidado.xlsx
```

## Arquivos Sensíveis

### config.py
Este arquivo contém as chaves de API e foi excluído do repositório por segurança. Crie-o com a seguinte estrutura:

```python
# config.py
GPT_ZERO_KEY = "sua_chave_gptzero_aqui"
ZERO_GPT_KEY = "sua_chave_zerogpt_aqui"
```

> ⚠️ **IMPORTANTE**: Nunca compartilhe ou comite o arquivo `config.py` com suas chaves de API!

## Notas
- O programa processa resenhas em lotes para respeitar limites de API
- Inclui tratamento de erros e logging detalhado
- Formatação visual otimizada para análise rápida
- Gráficos com escalas padronizadas para comparação consistente

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

