# app.py
import streamlit as st
import pandas as pd
import os
import csv
from pandasql import sqldf
import plotly.express as px
import json
import urllib.request

#########################
# URL do GeoJSON dos estados do Brasil (padrão IBGE)
#########################
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

#########################
# carregar CSVs
#########################

base_dir = os.path.dirname(__file__)

st.set_page_config(
    page_title="VISISAGUA",  
    page_icon="🌊",
    layout="centered"
)

@st.cache_data
def carregar_tabelas():
    tabelas = {}
    pasta_dados = os.path.join(base_dir, "..", "data", "db_export")

    arquivos_csv = [f for f in os.listdir(pasta_dados) if f.endswith('.csv')]
    for arquivo in sorted(arquivos_csv):
        nome_tabela = os.path.splitext(arquivo)[0]
        caminho = os.path.join(pasta_dados, arquivo)

        df = None
        for encoding in ['utf-8', 'latin1']:
            try:
                df = pd.read_csv(
                    caminho,
                    sep='\t',
                    encoding=encoding,
                    on_bad_lines='skip',
                    engine='python'
                )
                break
            except Exception:
                continue

        df = df.fillna('').astype(str)
        df = df.apply(lambda col: col.str.strip().str.slice(0, 120))

        tabelas[nome_tabela] = df

    return tabelas

################################
# interface com streamlit
################################
col1, col2 = st.columns([6, 1])

with col1:
    st.title("Visualizador de dados do SISAGUA")

with col2:
    st.image(os.path.join(base_dir, "..", "data" ,"sus-sistema-unico-de-saude.png"), width=150)

st.markdown("""
    Este é um projeto desenvolvido para a disciplina de Banco de Dados. Os dados utilizados são sobre o nível de qualidade de água de amostras que foram 
    retiradas em diversos locais do Brasil, levando em consideração a concentração de Cianobactérias e Cianotoxinas. Os dados foram disponibilizados
    pelo SISAGUA e podem ser acessados no site do [OpenDataSUS](https://opendatasus.saude.gov.br/dataset/sisagua-vigilancia-cianobacterias-e-cianotoxinas).
""")

tabelas = carregar_tabelas()

if not tabelas:
    st.stop()

###############################
# abas disponiveis
###############################
aba1, aba2, aba3 = st.tabs(["Visão Geral", "Em Detalhes", "Filtro Simples"])

###############################
# aba 1: visão geral (amostras)
###############################

with aba1:
    # Query 1 --------------------------------------------------
    query_visao_geral = """
        SELECT
            COUNT(*) AS total,
            MIN(DataColeta) AS antiga,
            MAX(DataColeta) AS recente
        FROM Coleta_Amostra_LocalColeta
        WHERE DataColeta IS NOT NULL 
          AND DataColeta != ''
          AND LENGTH(DataColeta) = 10
          AND SUBSTR(DataColeta, 5, 1) = '-'
          AND SUBSTR(DataColeta, 8, 1) = '-' 
    """
    
    try:
        resultado = sqldf(query_visao_geral, tabelas)
        row = resultado.iloc[0]

        total_amostras = int(row["total"])
        coleta_antiga = row["antiga"]
        coleta_recente = row["recente"]

        # Função para formatar as datas (garantir que não são nulas).
        def formatar_data(dt):
            if pd.isna(dt) or dt == "":
                return "—"
            try:
                return pd.to_datetime(dt).strftime("%d/%m/%Y")
            except Exception:
                return str(dt)

        data_antiga_fmt = formatar_data(coleta_antiga)
        data_recente_fmt = formatar_data(coleta_recente)

    except Exception as e:
        st.error(f"Erro ao executar a query de visão geral: {e}")
        total_amostras = "Erro"
        data_antiga_fmt = "Erro"
        data_recente_fmt = "Erro"

    # Estilo CSS
    st.markdown("""
    <style>
    .dashboard-card {
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08);
        margin: 10px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .card-title {
        font-size: 14px;
        color: #555;
        margin-bottom: 8px;
    }
    .card-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-title">Coleta mais antiga</div>
            <div class="card-value">{data_antiga_fmt}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-title">Total de amostras</div>
            <div class="card-value">{total_amostras:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-title">Coleta mais recente</div>
            <div class="card-value">{data_recente_fmt}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Query 2 --------------------------------------------------
    query_dist_temporal = """
        SELECT
            strftime('%Y', DataColeta) AS ano,
            COUNT(*) AS total
        FROM Coleta_Amostra_LocalColeta
        WHERE DataColeta IS NOT NULL 
          AND DataColeta != ''
          AND LENGTH(DataColeta) = 10
          AND SUBSTR(DataColeta, 5, 1) = '-'
          AND SUBSTR(DataColeta, 8, 1) = '-'
        GROUP BY strftime('%Y', DataColeta)
        ORDER BY ano;
    """
    
    try: 
        df_dist_temporal = sqldf(query_dist_temporal, tabelas)
        
        if df_dist_temporal.empty:
            st.warning("Nenhum dado encontrado para gerar o gráfico de distribuição temporal.")
        else:
            df_dist_temporal["ano"] = pd.to_numeric(df_dist_temporal["ano"], errors="coerce")
            df_dist_temporal = df_dist_temporal.dropna(subset=["ano"])
            df_dist_temporal = df_dist_temporal.sort_values("ano")

            fig2 = px.bar(
                df_dist_temporal,
                x="ano",
                y="total",
                labels={"ano": "Ano", "total": "Número de Amostras"},
                title="Distribuição de Amostras por Ano<br><sup>Visão Geral</sup>",
                color="total",
                color_continuous_scale="Blues",
                text="total"
            )
            
            fig2.update_layout(
                title={
                    'y': 0.90,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis_title="Ano",
                yaxis_title="Número de Amostras",
                xaxis_type='category',
                height=500,
                coloraxis_showscale=False
            )
            fig2.update_traces(
                texttemplate="%{text}",
                textposition="outside",
                hovertemplate=(
                    "<b>Ano:</b> %{x}<br>"
                    "<b>Amostras:</b> %{y} coletas<extra></extra>"
                )
            )

            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao gerar o gráfico de distribuição temporal: {e}")
    
    st.divider()
    
    # Query 3 --------------------------------------------------
    query_ufs = """
        SELECT 
            e.UF,
            COUNT(ca.NumeroDaAmostra) AS total_amostras
        FROM Coleta_Amostra_LocalColeta ca
            JOIN Municipio m ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
            JOIN Estado e ON m.fk_Estado_UF = e.UF
        GROUP BY e.UF
        ORDER BY e.UF;
    """

    try:
        df_ufs = sqldf(query_ufs, tabelas)

        if df_ufs.empty:
            st.warning("Nenhum dado encontrado para gerar o mapa por estado.")
        else:
            df_ufs["UF"] = df_ufs["UF"].astype(str)

            # Carregar GeoJSON dos estados do Brasil
            with urllib.request.urlopen(geojson_url) as response:
                geojson_brasil = json.load(response)

            estado_nomes = {
                'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
                'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
                'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
                'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
                'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
                'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
                'SE': 'Sergipe', 'TO': 'Tocantins'
            }
            df_ufs["nome_estado"] = df_ufs["UF"].map(estado_nomes)

            # Agora passe os dados extras via customdata
            fig = px.choropleth(
                df_ufs,
                geojson=geojson_brasil,
                locations="UF",
                featureidkey="properties.sigla", 
                color="total_amostras",
                color_continuous_scale="Blues",
                range_color=(0, df_ufs["total_amostras"].max()),
                labels={"total_amostras": "Amostras"},
                title="Distribuição de Amostras por Estado<br><sup>Visão Geral</sup>",
                custom_data=["UF", "nome_estado", "total_amostras"]
            )
            
            fig.update_geos(
                fitbounds="locations",
                visible=False,
                lonaxis_range=[-75, -30], 
                lataxis_range=[-35, 5]
            )
            fig.update_layout(
                title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                height=500
            )
            fig.update_traces(
                hovertemplate=(
                    "<b>Estado:</b> %{customdata[1]} (%{customdata[0]})<br>"
                    "<b>Amostras:</b> %{customdata[2]:,} coletas<br>"
                    "<extra></extra>"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao gerar o mapa: {e}")
        st.info("Verifique se as tabelas 'Coleta_Amostra_LocalColeta', 'Municipio' e 'Estado' estão presentes e com as chaves corretas.")
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Query 4 --------------------------------------------------
    query_regioes = """
        SELECT 
            e.Regiao,
            COUNT(ca.NumeroDaAmostra) AS total_amostras
        FROM Coleta_Amostra_LocalColeta ca
            JOIN Municipio m ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
            JOIN Estado e ON m.fk_Estado_UF = e.UF
        GROUP BY e.Regiao
        ORDER BY total_amostras DESC;
    """

    try:
        df_regioes = sqldf(query_regioes, tabelas)

        if df_regioes.empty:
            st.warning("Nenhum dado encontrado para gerar o gráfico por região.")
        else:
            df_regioes["Regiao"] = df_regioes["Regiao"].astype(str)

            fig_regioes = px.pie(
                df_regioes,
                values="total_amostras",
                names="Regiao",
                title="Representatividade das Regiões nas Amostras<br><sup>Visão Geral</sup>",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.5
            )

            fig_regioes.update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Amostras: %{value:,}<br>"
                    "Participação: %{percent}<extra></extra>"
                ),
                textinfo="percent",
                textfont_size=14
            )

            fig_regioes.update_layout(
                title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={"t": 80, "b": 50, "l": 50, "r": 50},
                height=450
            )

            st.plotly_chart(fig_regioes, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao gerar gráfico por região: {e}")
          
###############################
# aba 2: em detalhes (por estado e múnicipio)
###############################
with aba2:
    try:
        query_ufs = """
            SELECT DISTINCT UF
            FROM Estado
            WHERE UF IS NOT NULL AND UF != ''
            ORDER BY UF;
        """
        df_ufs = sqldf(query_ufs, tabelas)
        ufs = df_ufs["UF"].tolist()
    except Exception as e:
        st.error(f"Erro ao carregar UFs: {e}")
        ufs = []

    uf_selecionada = st.selectbox("Selecione a UF:", [""] + ufs, key="uf_select_sql")

    municipio_selecionado = None
    if uf_selecionada:
        try:
            ## Query 5 --------------------------------------------------
            query_municipios = f"""
                SELECT DISTINCT m.NomeMunicipio
                FROM Municipio m
                WHERE m.fk_Estado_UF IN (
                    SELECT e.UF
                    FROM Estado e
                    WHERE e.UF = '{uf_selecionada}'
                )
                AND m.NomeMunicipio IS NOT NULL AND m.NomeMunicipio != ''
                ORDER BY m.NomeMunicipio;
            """
            df_municipios = sqldf(query_municipios, tabelas)
            municipios = df_municipios["NomeMunicipio"].tolist()

            if municipios:
                municipio_selecionado = st.selectbox(
                    "Selecione o Município:",
                    [""] + municipios,
                    key="municipio_select_sql"
                )
            else:
                st.warning(f"Nenhum município encontrado para a UF **{uf_selecionada}**.")
        except Exception as e:
            st.error(f"Erro ao carregar municípios da UF {uf_selecionada}: {e}")

    st.divider()
    
    if municipio_selecionado:
        ## Query 6 --------------------------------------------------
        query_visao_municipio = f"""
            SELECT 
                COUNT(*) AS total,
                MIN(sub.DataColeta) AS antiga,
                MAX(sub.DataColeta) AS recente
            FROM (
                -- Subconsulta: todas as amostras do município (e UF) selecionado, com validação de data
                SELECT 
                    ca.DataColeta
                FROM Coleta_Amostra_LocalColeta ca
                JOIN Municipio m 
                    ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
                WHERE ca.DataColeta IS NOT NULL 
                  AND ca.DataColeta != ''
                  AND LENGTH(ca.DataColeta) = 10
                  AND SUBSTR(ca.DataColeta, 5, 1) = '-'
                  AND SUBSTR(ca.DataColeta, 8, 1) = '-'
                  AND m.NomeMunicipio = '{municipio_selecionado}'
                  AND m.fk_Estado_UF = '{uf_selecionada}'
            ) AS sub;
        """
        
        try:
            resultado_m = sqldf(query_visao_municipio, tabelas)
            row_m = resultado_m.iloc[0]

            total_amostras_m = int(row_m["total"])
            coleta_antiga_m = row_m["antiga"]
            coleta_recente_m = row_m["recente"]

            # Função para formatar as datas (garantir que não são nulas).
            def formatar_data(dt):
                if pd.isna(dt) or dt == "":
                    return "—"
                try:
                    return pd.to_datetime(dt).strftime("%d/%m/%Y")
                except Exception:
                    return str(dt)

            data_antiga_fmt_m = formatar_data(coleta_antiga_m)
            data_recente_fmt_m = formatar_data(coleta_recente_m)

        except Exception as e:
            st.error(f"Erro ao executar a query de visão geral: {e}")
            total_amostras_m = "Erro"
            data_antiga_fmt_m = "Erro"
            data_recente_fmt_m = "Erro"

        # Estilo CSS
        st.markdown("""
        <style>
        .dashboard-card {
            background-color: #f9f9f9;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
            margin: 10px;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .card-title {
            font-size: 14px;
            color: #555;
            margin-bottom: 8px;
        }
        .card-value {
            font-size: 24px;
            font-weight: bold;
            color: #1f77b4;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Coleta mais antiga</div>
                <div class="card-value">{data_antiga_fmt_m}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Total de amostras</div>
                <div class="card-value">{total_amostras_m:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Coleta mais recente</div>
                <div class="card-value">{data_recente_fmt_m}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        ## Query 7 --------------------------------------------------    
        try:
            query_dist_temporal_municipio = f"""
                SELECT
                    strftime('%Y', ca.DataColeta) AS ano,
                    COUNT(*) AS total
                FROM Coleta_Amostra_LocalColeta ca
                JOIN Municipio m 
                    ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
                JOIN Estado e 
                    ON m.fk_Estado_UF = e.UF
                WHERE 
                    ca.DataColeta IS NOT NULL 
                    AND ca.DataColeta != ''
                    AND LENGTH(ca.DataColeta) = 10
                    AND SUBSTR(ca.DataColeta, 5, 1) = '-'
                    AND SUBSTR(ca.DataColeta, 8, 1) = '-'
                    AND m.NomeMunicipio = '{municipio_selecionado}'
                    AND e.UF = '{uf_selecionada}'
                GROUP BY strftime('%Y', ca.DataColeta)
                ORDER BY ano;
            """

            df_temp_muni = sqldf(query_dist_temporal_municipio, tabelas)

            if df_temp_muni.empty:
                st.info(f"Nenhuma coleta registrada para **{municipio_selecionado} - {uf_selecionada}**.")
            else:
                # Garantir ordenação correta
                df_temp_muni["ano"] = pd.to_numeric(df_temp_muni["ano"], errors="coerce")
                df_temp_muni = df_temp_muni.dropna(subset=["ano"]).sort_values("ano")

                # Gráfico de barras
                fig_temp_muni = px.bar(
                    df_temp_muni,
                    x="ano",
                    y="total",
                    labels={"ano": "Ano", "total": "Número de Amostras"},
                    title=f"Distribuição de Amostras por Ano<br><sup>{municipio_selecionado} - {uf_selecionada}</sup>",
                    color="total",
                    color_continuous_scale="Blues",
                    text="total"
                )
                
                fig_temp_muni.update_layout(
                    title={
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    xaxis_title="Ano",
                    yaxis_title="Número de Amostras",
                    xaxis_type="category",
                    height=500,
                    coloraxis_showscale=False 
                )
                fig_temp_muni.update_traces(
                    texttemplate="%{text}",
                    textposition="outside",
                    hovertemplate=(
                        "<b>Ano:</b> %{x}<br>"
                        "<b>Amostras:</b> %{y} coletas<extra></extra>"
                    )
                )

                st.plotly_chart(fig_temp_muni, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao gerar distribuição temporal do município: {e}")
        
        st.divider()
        
        ## Query 8 --------------------------------------------------
        query_abastecimento_bruto = f"""
            SELECT
                a.NomeDaFormaDeAbastecimento,
                COUNT(*) AS total
            FROM Municipio m
                JOIN Estado e ON m.fk_Estado_UF = e.UF
                LEFT JOIN Abastecido ab ON m.CodigoDoIBGE = ab.fk_Municipio_CodigoDoIBGE
                LEFT JOIN Abastecimento a ON ab.fk_Abastecimento_CodigoFormaDeAbastecimento = a.CodigoFormaDeAbastecimento
            WHERE m.NomeMunicipio = '{municipio_selecionado}'
              AND e.UF = '{uf_selecionada}'
            GROUP BY a.CodigoFormaDeAbastecimento;
        """
        
        df_abast = sqldf(query_abastecimento_bruto, tabelas)

        if df_abast.empty:
            st.info("Nenhuma informação de abastecimento encontrada.")
        else:
            df_abast["NomeDaFormaDeAbastecimento"] = (df_abast["NomeDaFormaDeAbastecimento"].fillna("Indeterminado").replace("", "Indeterminado").replace("null", "Indeterminado").astype(str))

            fig = px.pie(
                df_abast,
                values="total",
                names="NomeDaFormaDeAbastecimento",
                title=f"Formas de Abastecimento<br><sup>{municipio_selecionado} - {uf_selecionada}</sup>",
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(
                title={
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={"t": 80, "b": 50, "l": 50, "r": 50},
                height=450
            )
            fig.update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"
                ),
                textinfo="none",
                textfont_size=14
            )
            st.plotly_chart(fig, use_container_width=True)
        

        ## Query 9 --------------------------------------------------
        query_localcoleta_bruto = f"""
            SELECT
                ca.TipoDoLocal,
                COUNT(*) AS total
            FROM Municipio m
                JOIN Estado e ON m.fk_Estado_UF = e.UF
                LEFT JOIN Coleta_Amostra_LocalColeta ca ON m.CodigoDoIBGE = ca.fk_Municipio_CodigoDoIBGE
            WHERE m.NomeMunicipio = '{municipio_selecionado}'
              AND e.UF = '{uf_selecionada}'
            GROUP BY ca.TipoDoLocal;
        """
        
        df_localcoleta = sqldf(query_localcoleta_bruto, tabelas)

        if df_localcoleta.empty:
            st.info("Nenhuma informação de abastecimento encontrada.")
        else:
            df_localcoleta["TipoDoLocal"] = (df_localcoleta["TipoDoLocal"].fillna("Indeterminado").replace("", "Indeterminado").replace("null", "Indeterminado").astype(str))

            fig = px.pie(
                df_localcoleta,
                values="total",
                names="TipoDoLocal",
                title=f"Locais de Coleta<br><sup>{municipio_selecionado} - {uf_selecionada}</sup>",
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(
                title={
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                margin={"t": 80, "b": 50, "l": 50, "r": 50},
                height=450
            )
            fig.update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Amostras: %{value:,}<br>"
                    "Participação: %{percent}<extra></extra>"
                ),
                textinfo="percent",
                textfont_size=14
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        if municipio_selecionado and uf_selecionada:
            try:
                if "Classificacao" in tabelas:
                    df_param = tabelas["Classificacao"]
                    parametros = (
                        df_param["Parametro_ciano_"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .replace("", pd.NA)
                        .dropna()
                        .sort_values()
                        .unique()
                        .tolist()
                    )
                else:
                    st.error("Tabela 'Classificacao' não encontrada.")
                    parametros = []
            except Exception as e:
                st.warning(f"Erro ao carregar parâmetros: {e}")
                parametros = []

            if parametros:
                parametro_selecionado = st.selectbox("Selecione o parâmetro cianobacteriano:", options=parametros, key="parametro_select")
            else:
                st.info("Nenhum parâmetro disponível para seleção.")
                parametro_selecionado = None

            ## Query 10 --------------------------------------------------
            if parametro_selecionado:
                try:
                    query_estatisticas = f"""
                        SELECT 
                            COUNT(a.Resultado) AS total_resultados,
                            MIN(a.Resultado) AS min_resultado,
                            ROUND(AVG(a.Resultado), 2) AS media_resultado,
                            MAX(a.Resultado) AS max_resultado
                        FROM Analise a
                        JOIN Coleta_Amostra_LocalColeta ca
                            ON a.fk_Amostra_DataColeta = ca.DataColeta
                           AND a.fk_Amostra_Hora = ca.Hora
                           AND a.fk_Amostra_NumeroDaAmostra = ca.NumeroDaAmostra
                        JOIN Municipio m
                            ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
                        JOIN Estado e
                            ON m.fk_Estado_UF = e.UF
                        WHERE 
                            e.UF = '{uf_selecionada}'
                            AND m.NomeMunicipio = '{municipio_selecionado}'
                            AND a.fk_Classificacao_Parametro_ciano_ = '{parametro_selecionado}'
                            AND a.Resultado IS NOT NULL;
                    """

                    df_stats = sqldf(query_estatisticas, tabelas)
                    row_stats = df_stats.iloc[0]

                    total_resultados = int(row_stats["total_resultados"])
                    min_valor = row_stats["min_resultado"]
                    media_valor = row_stats["media_resultado"]
                    max_valor = row_stats["max_resultado"]
                    
                    def formatar_valor(val):
                        if pd.isna(val) or val is None:
                            return "—"
                        try:
                            return f"{float(val):.2f}"
                        except:
                            return str(val)

                    min_fmt = formatar_valor(min_valor)
                    media_fmt = formatar_valor(media_valor)
                    max_fmt = formatar_valor(max_valor)

                except Exception as e:
                    st.error(f"Erro ao calcular estatísticas: {e}")
                    min_fmt = media_fmt = max_fmt = "Erro"
                
                st.markdown("""
                <style>
                .dashboard-card {
                    background-color: #f9f9f9;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.08);
                    margin: 10px;
                    min-height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .card-title {
                    font-size: 14px;
                    color: #555;
                    margin-bottom: 8px;
                }
                .card-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #1f77b4;
                }
      
                </style>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div class="card-title">Menor Medida Observada</div>
                        <div class="card-value">{min_fmt}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div class="card-title">Média Geral</div>
                        <div class="card-value media">{media_fmt}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div class="card-title">Maior Medida Observada</div>
                        <div class="card-value max">{max_fmt}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                

                ## Query 11 --------------------------------------------------
                query_evolu_anual = f"""
                SELECT
                    strftime('%Y', a.DataDoLaudo) AS ano,
                    ROUND(AVG(a.Resultado), 2) AS media_resultado,
                    COUNT(a.Resultado) AS qtd_amostras
                FROM Analise a
                JOIN Coleta_Amostra_LocalColeta ca
                    ON a.fk_Amostra_DataColeta = ca.DataColeta
                   AND a.fk_Amostra_Hora = ca.Hora
                   AND a.fk_Amostra_NumeroDaAmostra = ca.NumeroDaAmostra
                JOIN Municipio m
                    ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
                JOIN Estado e
                    ON m.fk_Estado_UF = e.UF
                WHERE 
                    e.UF = '{uf_selecionada}'
                    AND m.NomeMunicipio = '{municipio_selecionado}'
                    AND a.fk_Classificacao_Parametro_ciano_ = '{parametro_selecionado}'
                    AND a.Resultado IS NOT NULL
                    AND a.DataDoLaudo IS NOT NULL
                GROUP BY strftime('%Y', a.DataDoLaudo)
                ORDER BY ano;
                """
                
                try:
                    df_evolucao = sqldf(query_evolu_anual, tabelas)

                    if df_evolucao.empty:
                        st.info(f"Nenhum resultado encontrado para o parâmetro **{parametro_selecionado}** em **{municipio_selecionado} - {uf_selecionada}**.")
                    else:
                        # Garantir que 'ano' é string categórica (para eixo X não interpolar)
                        df_evolucao["ano"] = df_evolucao["ano"].astype(str)

                        # Criar gráfico de linha
                        fig_linha = px.line(
                            df_evolucao,
                            x="ano",
                            y="media_resultado",
                            title=f"Evolução da média de '{parametro_selecionado}'<br><sup>{municipio_selecionado} - {uf_selecionada}</sup>",
                            markers=True,
                            text="media_resultado"
                        )

                        # Estilizar
                        fig_linha.update_traces(
                            line=dict(width=3, color="#1f77b4"),
                            marker=dict(size=8, color="#1f77b4", line=dict(width=1, color="white")),
                            texttemplate="%{text:.2f}",
                            textposition="top center",
                            hovertemplate=(
                                "<b>Ano:</b> %{x}<br>"
                                "<b>Média:</b> %{y:.2f}<br>"
                                "<b>Amostras:</b> %{customdata} coletas<extra></extra>"
                            ),
                            customdata=df_evolucao["qtd_amostras"]
                        )

                        fig_linha.update_layout(
                            title={
                                'y': 0.95,
                                'x': 0.5,
                                'xanchor': 'center'
                            },
                            xaxis_title="Ano",
                            yaxis_title="Média do Resultado",
                            xaxis=dict(type="category"),
                            yaxis=dict(tickformat=".2f"),
                            height=450,
                            hovermode="x unified"
                        )
                        
                        st.plotly_chart(fig_linha, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Erro ao gerar evolução anual: {e}")
        
###############################
# aba 3: filtro simples 
###############################
with aba3:
    st.caption("Escolha uma tabela")
    nome = st.selectbox(
        "Tabela:",
        list(tabelas.keys()),
        key="filtro_tab",
        label_visibility="collapsed"
    )
    df = tabelas[nome]

    if df.empty:
        st.warning("Esta tabela está vazia.")
    else:
        # --- Informações da Tabela ---
        with st.expander("**Detalhes da Tabela**", expanded=False):
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("Linhas", f"{len(df):,}")
            with col_info2:
                st.metric("Colunas", len(df.columns))

            st.markdown("##### Estrutura da Tabela")
            schema = pd.DataFrame({
                "Coluna": df.columns,
                "Tipo": df.dtypes.astype(str),
                "Nulos": df.isnull().sum(),
                "% Nulos": (df.isnull().mean() * 100).round(2),
                "Únicos": df.nunique(),
                "Exemplo": df.apply(lambda x: x.dropna().iloc[0] if not x.dropna().empty else "—")
            })
            # Estilizar o schema visualmente
            st.dataframe(
                schema.style.format({
                    "% Nulos": "{:.1f}%",
                    "Nulos": "{:,}",
                    "Únicos": "{:,}"
                }),
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        col_filtro1, col_filtro2 = st.columns([2, 3])

        with col_filtro1:
            st.caption("1. Escolha a coluna")
            coluna = st.selectbox(
                "Coluna",
                options=df.columns,
                label_visibility="collapsed",
                key="coluna_filtro"
            )

        with col_filtro2:
            st.caption("2. Informe o valor")
            valores_unicos = df[coluna].dropna().unique()

            if len(valores_unicos) <= 50 and df[coluna].dtype == 'object':
                valor = st.selectbox(
                    "Valor",
                    options=[""] + sorted(valores_unicos),
                    label_visibility="collapsed",
                    key="valor_selecao"
                )
            else:
                valor = st.text_input(
                    "Buscar substring",
                    placeholder=f"Digite parte do valor em '{coluna}'",
                    label_visibility="collapsed",
                    key="valor_texto"
                )

        st.divider()

        # --- Resultados ---
        if valor:
            # Garantir comparação segura (evitar erro em colunas numéricas)
            if pd.api.types.is_string_dtype(df[coluna]) or df[coluna].dtype == 'object':
                mask = df[coluna].astype(str).str.contains(valor, case=False, na=False)
            else:
                # Converter valor digitado para o tipo da coluna (ex: número)
                try:
                    valor_convertido = type(df[coluna].dropna().iloc[0])(valor)
                    mask = df[coluna] == valor_convertido
                except (ValueError, IndexError):
                    mask = df[coluna].astype(str).str.contains(valor, case=False, na=False)

            resultado = df[mask].copy().reset_index(drop=True)
            total = len(resultado)

            # Feedback visual com destaque
            if total == 0:
                st.warning("Nenhum resultado encontrado.")
            else:
                st.success(f"Encontrado(s) **{total:,}** registro(s).")

                # Mostrar amostra (limitada)
                exibir = min(50, total)
                st.markdown(f"**Mostrando os primeiros {exibir} resultados:**")
                
                # Estilizar a tabela: cabeçalhos em negrito, bordas, etc.
                st.dataframe(
                    resultado.head(50),
                    use_container_width=True,
                    height=400,
                    column_config={
                        "__index__": None,
                    }
                )

                # Botão de download
                if total > 0:
                    csv = resultado.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Baixar Resultados (CSV)",
                        data=csv,
                        file_name=f"{nome}_filtrado_{coluna}_{valor}.csv",
                        mime="text/csv",
                        type="secondary"
                    )
        else:
            st.info("Ajuste os filtros acima para buscar dados.")
			

st.divider()
st.caption("Dados retirados no OpenDataSUS")