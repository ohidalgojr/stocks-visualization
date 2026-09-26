from __future__ import annotations

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


@st.cache_resource(show_spinner="Carregando e indexando o conjunto completo de cotações...")
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], dict[str, object]]:
    """Carrega todos os registros uma vez e cria estruturas para filtros rápidos.

    A tabela de cotações permanece completa. A ordenação pelo índice `symbol`
    permite recuperar apenas as empresas necessárias a cada interação.
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

    volume_por_empresa = (
        cotacoes.groupby("symbol", observed=True, sort=False)["volume"]
        .mean()
        .rename("volume_medio")
        .reset_index()
    )
    ranking = (
        volume_por_empresa.merge(empresas[["symbol", "sector"]], on="symbol", how="inner")
        .dropna(subset=["sector"])
        .sort_values(["sector", "volume_medio"], ascending=[True, False])
    )
    top5_por_setor = (
        ranking.groupby("sector", observed=True, sort=False)
        .head(5)
        .groupby("sector", observed=True, sort=False)["symbol"]
        .agg(list)
        .to_dict()
    )
    top5_por_setor["Todos"] = ranking.nlargest(5, "volume_medio")["symbol"].tolist()

    metadados = {
        "total_registros": len(cotacoes),
        "data_min": cotacoes["date"].min().date(),
        "data_max": cotacoes["date"].max().date(),
    }
    cotacoes_indexadas = cotacoes.set_index("symbol").sort_index()
    return empresas, cotacoes_indexadas, top5_por_setor, metadados


empresas, cotacoes_indexadas, top5_por_setor, metadados = carregar_dados()

st.title("S&P 500 — Dashboard exploratório")
st.caption(
    "Exploração de preços e volume das empresas do S&P 500. "
    "A tabela completa é carregada uma vez e os filtros consultam apenas as empresas selecionadas."
)

with st.sidebar:
    st.header("Filtros")
    setores = ["Todos"] + sorted(set(top5_por_setor) - {"Todos"})
    setor_escolhido = st.selectbox("Setor", setores)

    periodo = st.date_input(
        "Período",
        value=(metadados["data_min"], metadados["data_max"]),
        min_value=metadados["data_min"],
        max_value=metadados["data_max"],
    )
    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio = fim = periodo

    simbolos = top5_por_setor[setor_escolhido]
    st.caption("Empresas exibidas: as 5 com maior volume médio de negociação no setor.")
    st.code(", ".join(simbolos), language=None)

cotacoes_selecionadas = cotacoes_indexadas.loc[simbolos].reset_index()
cotacoes_filtro = cotacoes_selecionadas.loc[
    cotacoes_selecionadas["date"].between(pd.Timestamp(inicio), pd.Timestamp(fim))
]

if cotacoes_filtro.empty:
    st.warning("A seleção atual não possui registros no período escolhido.")
    st.stop()

empresas_filtro = empresas if setor_escolhido == "Todos" else empresas[empresas["sector"] == setor_escolhido]

col1, col2, col3 = st.columns(3)
col1.metric("Registros carregados", f"{metadados['total_registros']:,}")
col2.metric("Registros filtrados", f"{len(cotacoes_filtro):,}")
col3.metric("Empresas exibidas", f"{len(simbolos):,}")

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
        tooltip=[
            alt.Tooltip("ano:O", title="Ano"),
            alt.Tooltip("symbol:N", title="Empresa"),
            alt.Tooltip("preco_medio:Q", title="Preço médio (US$)", format="$.2f"),
        ],
    )
    .properties(height=420)
)
st.altair_chart(grafico_precos, use_container_width=True)
st.caption("Passe o cursor sobre um ponto para ver o ano, a empresa e o preço médio de fechamento.")

st.subheader("2. Quais empresas apresentam maior volume médio de negociação?")
volume_medio = (
    cotacoes_filtro.groupby("symbol", as_index=False)["volume"]
    .mean()
    .rename(columns={"volume": "volume_medio"})
    .sort_values("volume_medio", ascending=False)
)
grafico_volume = (
    alt.Chart(volume_medio)
    .mark_bar()
    .encode(
        x=alt.X("volume_medio:Q", title="Volume médio (ações)"),
        y=alt.Y("symbol:N", title="Symbol", sort="-x"),
        color=alt.Color("symbol:N", title="Symbol", legend=None),
        tooltip=[
            alt.Tooltip("symbol:N", title="Empresa"),
            alt.Tooltip("volume_medio:Q", title="Volume médio (ações)", format=",.0f"),
        ],
    )
    .properties(height=300)
)
st.altair_chart(grafico_volume, use_container_width=True)
st.caption("Passe o cursor sobre uma barra para ver a empresa e seu volume médio no período filtrado.")

st.subheader("3. Como as empresas estão distribuídas por setor?")
contagem_setores = empresas_filtro["sector"].value_counts().rename_axis("sector").reset_index(name="empresas")
grafico_setores = px.bar(
    contagem_setores.sort_values("empresas"),
    x="empresas",
    y="sector",
    orientation="h",
    labels={"empresas": "Número de empresas", "sector": "Setor"},
    title="Empresas por setor no cadastro selecionado",
    hover_data={"empresas": ":,"},
)
st.plotly_chart(grafico_setores, use_container_width=True)

st.divider()
st.caption(
    "Fonte: ohidalgojr/stock-exchange-dataset no GitHub. "
    "Esta versão é exploratória e não constitui recomendação de investimento."
)
