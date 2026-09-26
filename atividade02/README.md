# Atividade 02 — Dashboard interativo com Streamlit

## Objetivo

Dashboard exploratório do S&P 500, dando continuidade à Atividade 01. A aplicação investiga:

1. Como o preço médio de fechamento varia ao longo dos anos para as empresas selecionadas?
2. Quais empresas apresentam maior volume médio de negociação?
3. Como as empresas estão distribuídas por setor?

## Dados

Os dois arquivos são carregados diretamente pelas URLs raw do GitHub:

- `sp500_companies.csv`: cadastro e setor das empresas;
- `sp500_stocks.csv`: observações diárias de preço e volume.

A aplicação carrega todos os registros da tabela de cotações no pandas, sem amostragem. Para melhorar a performance, utiliza `usecols`, tipos numéricos compactos e `st.cache_data`. O download inicial ainda pode exigir alguns minutos e memória disponível.

## Instalação e execução

No PowerShell, dentro desta pasta:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run app.py
```

Abra a URL exibida pelo Streamlit, normalmente `http://localhost:8501`.

## Interações

O dashboard possui filtros por setor, período e `symbol`. Toda seleção atualiza os gráficos e informa quando não existem registros para o recorte escolhido.

## Bibliotecas

- Streamlit: estrutura da aplicação e controles;
- Altair: evolução anual do preço médio de fechamento;
- Plotly: volume médio e distribuição por setor.

## Limitações

Esta etapa não realiza limpeza, imputação, criação de variáveis para modelagem ou previsão. Os resultados são descritivos. A composição histórica do índice, eventos corporativos e outras informações financeiras podem não estar completamente representados nos arquivos.
