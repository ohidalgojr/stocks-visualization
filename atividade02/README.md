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

A aplicação carrega todos os registros da tabela de cotações no pandas, sem amostragem. Para melhorar a performance, utiliza `usecols`, tipos numéricos compactos e `st.cache_resource`: os dados são carregados, indexados por `symbol` e mantidos em memória uma única vez. O primeiro carregamento ainda pode exigir alguns minutos e memória disponível; as mudanças posteriores de filtro consultam apenas as empresas necessárias.

## Instalação e execução

No PowerShell, dentro desta pasta, instale as dependências:

```powershell
py -m pip install -r requirements.txt
```

Depois, execute o dashboard usando o mesmo Python que instalou as dependências:

```powershell
py -m streamlit run app.py
```

O uso de ambiente virtual não é necessário para este projeto. A forma `py -m streamlit` evita problemas quando o executável `streamlit` não está disponível no `PATH` do Windows.

Abra a URL exibida pelo Streamlit, normalmente `http://localhost:8501`.

## Interações

O dashboard possui filtros por setor e período. Ao selecionar um setor, ele carrega automaticamente as cinco empresas desse setor com maior volume médio de negociação no conjunto completo de dados. Toda seleção atualiza os gráficos e informa quando não existem registros para o recorte escolhido.

## Bibliotecas

- Streamlit: estrutura da aplicação e controles;
- Altair: evolução anual do preço médio de fechamento;
- Plotly: volume médio e distribuição por setor.

## Limitações

Esta etapa não realiza limpeza, imputação, criação de variáveis para modelagem ou previsão. Os resultados são descritivos. A composição histórica do índice, eventos corporativos e outras informações financeiras podem não estar completamente representados nos arquivos.
