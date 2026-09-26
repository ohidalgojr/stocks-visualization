from __future__ import annotations

from datetime import date

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st


URL_EMPRESAS = (
    "https://media.githubusercontent.com/media/ohidalgojr/stock-exchange-dataset/"
    "refs/heads/main/sp500_companies.csv"
)
URL_COTACOES = (
    "https://media.githubusercontent.com/media/ohidalgojr/stock-exchange-dataset/"
    "refs/heads/main/sp500_stocks.csv"
)


st.set_page_config(
    page_title="S&P 500 — Dashboard exploratório",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(show_spinner="Carregando o conjunto completo de cotações...")
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega todos os registros disponíveis, sem amostragem.

    usecols e dtype reduzem o consumo de memória sem alterar o conteúdo
    analítico das colunas utilizadas no dashboard.
    """
    tipos_empresas = {
        "symbol": "string",
        "company": "string",
        "sector": "string",
        "sub_industry": "string",
        "headquarters": "string",
        "date_added": "string",
        "founded": "string",
    }
    empresas = pd.read_csv(URL_EMPRESAS, dtype=tipos_empresas, low_memory=False)

    colunas_cotacoes = ["date", "open", "high", "low", "close", "volume", "symbol"]
    tipos_cotacoes = {
        "open": "float32",
        "high": "float32",
        "low": "float32",
        "close": "float32",
        "volume": "float64",
        "symbol": "string",
    }
    cotacoes = pd.read_csv(
        URL_COTACOES,
        usecols=colunas_cotacoes,
        dtype=tipos_cotacoes,
        parse_dates=["date"],
        low_memory=False,
    )
    return empresas, cotacoes


empresas, cotacoes = carregar_dados()

st.title("S&P 500 — Dashboard exploratório")
st.caption(
    "Exploração de preços e volume das empresas do S&P 500. "
    "Os dados são carregados integralmente pelas URLs raw do GitHub."
)

with st.sidebar:
    st.header("Filtros")

    setores = ["Todos"] + sorted(empresas["sector"].dropna().unique().tolist())
    setor_escolhido = st.selectbox("Setor", setores)

    data_min = cotacoes["date"].min().date()
    data_max = cotacoes["date"].max().date()
    periodo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio = fim = periodo

    empresas_filtro = empresas
    if setor_escolhido != "Todos":
        empresas_filtro = empresas[empresas["sector"] == setor_escolhido]

    simbolos_disponiveis = sorted(
        set(empresas_filtro["symbol"].dropna())
        & set(cotacoes["symbol"].dropna())
    )
    preferidos = [s for s in ["AAPL", "NVDA"] if s in simbolos_disponiveis]
    simbolos_padrao = preferidos or simbolos_disponiveis[:2]
    simbolos = st.multiselect(
        "Empresas (symbol)",
        options=simbolos_disponiveis,
        default=simbolos_padrao,
    )

if not simbolos:
    st.warning("Selecione pelo menos uma empresa para atualizar as visualizações.")
    st.stop()

cotacoes_filtro = cotacoes[
    cotacoes["symbol"].isin(simbolos)
    & cotacoes["date"].between(pd.Timestamp(inicio), pd.Timestamp(fim))
].copy()

if cotacoes_filtro.empty:
    st.warning("A seleção atual não possui registros no período escolhido.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Registros carregados", f"{len(cotacoes):,}")
col2.metric("Registros filtrados", f"{len(cotacoes_filtro):,}")
col3.metric("Empresas selecionadas", f"{len(simbolos):,}")

st.subheader("1. Como o preço médio de fechamento varia ao longo dos anos?")
precos_anuais = (
    cotacoes_filtro.assign(ano=cotacoes_filtro["date"].dt.year)
    .groupby(["ano", "symbol"], as_index=False)["close"]
    .mean()
    .rename(columns={"close": "preco_medio"})
)
grafico_precos = (
    alt.Chart(precos_anuais)
    .mark_line(point=True)
    .encode(
        x=alt.X("ano:O", title="Ano"),
        y=alt.Y("preco_medio:Q", title="Preço médio de fechamento (US$ por ação)"),
        color=alt.Color("symbol:N", title="Symbol"),
        tooltip=["ano", "symbol", alt.Tooltip("preco_medio:Q", format=",.2f")],
    )
    .properties(height=420)
)
st.altair_chart(grafico_precos, use_container_width=True)
st.caption("Cada ponto representa o preço médio de fechamento anual no período filtrado.")

st.subheader("2. Quais empresas apresentam maior volume médio de negociação?")
volume_medio = (
    cotacoes_filtro.groupby("symbol", as_index=False)["volume"]
    .mean()
    .rename(columns={"volume": "volume_medio"})
    .sort_values("volume_medio", ascending=False)
    .head(10)
)
grafico_volume = px.bar(
    volume_medio.sort_values("volume_medio"),
    x="volume_medio",
    y="symbol",
    orientation="h",
    labels={"volume_medio": "Volume médio (ações)", "symbol": "Symbol"},
    title="Dez maiores volumes médios entre as empresas selecionadas",
)
st.plotly_chart(grafico_volume, use_container_width=True)
st.caption("O volume representa a quantidade de ações negociadas nas observações disponíveis.")

st.subheader("3. Como as empresas estão distribuídas por setor?")
contagem_setores = empresas_filtro["sector"].value_counts().rename_axis("sector").reset_index(name="empresas")
grafico_setores = px.bar(
    contagem_setores.sort_values("empresas"),
    x="empresas",
    y="sector",
    orientation="h",
    labels={"empresas": "Número de empresas", "sector": "Setor"},
    title="Empresas por setor no cadastro selecionado",
)
st.plotly_chart(grafico_setores, use_container_width=True)

st.divider()
st.caption(
    "Fonte: ohidalgojr/stock-exchange-dataset no GitHub. "
    "Esta versão é exploratória e não constitui recomendação de investimento."
)
