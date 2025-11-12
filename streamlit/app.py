# app.py
import streamlit as st
import pandas as pd
import os
import csv
from pandasql import sqldf


#########################
# carregar CSVs
#########################

@st.cache_data
def carregar_tabelas():
    tabelas = {}
    pasta_dados = "dados"

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
col1, col2 = st.columns([7, 1])

with col1:
    st.title("Visualizador de dados do SISAGUA")

with col2:
    st.image("sus-sistema-unico-de-saude.png", width=150)

st.markdown("""
    Este é um projeto desenvolvido para a disciplina de Banco de Dados. Os dados utilizados é sobre o nível de qualidade de água de amostras que foram 
    retiradas em diversos locais do Brasil, levando em consideração a concentração de Cianobactérias e Cianotoxinas. Os dados foram disponibilizados
    pelo SISAGUA e podem ser acessados no site do [OpenDataSUS](https://opendatasus.saude.gov.br/dataset/sisagua-vigilancia-cianobacterias-e-cianotoxinas).
""")

tabelas = carregar_tabelas()

if not tabelas:
    st.stop()

# abas disponiveis
aba1, aba2, aba3 = st.tabs(["Visualização simplificada", "Filtro Simples", "Busca avançada"])

###############################
# aba 1: visualizar tabelas
###############################

with aba1:
    nome = st.selectbox("Selecione uma tabela:", list(tabelas.keys()))
    df = tabelas[nome]
    st.caption(f"`{nome}` — {df.shape[0]} linhas × {df.shape[1]} colunas")
    
    # delimitar quantidade de linhas
    n_linhas = st.slider("Quantas linhas mostrar?", 5, min(100, len(df)), 10)
    st.dataframe(df.head(n_linhas), use_container_width=True)

###############################
# aba 2: filtro simples
###############################
with aba2:
    nome = st.selectbox("Tabela:", list(tabelas.keys()), key="filtro_tab")
    df = tabelas[nome]

    if not df.empty:
        coluna = st.selectbox("Coluna para filtrar:", df.columns)
        valores_unicos = df[coluna].dropna().unique()

        if len(valores_unicos) <= 50:
            valor = st.selectbox("Valor:", [""] + sorted(valores_unicos))
        else:
            valor = st.text_input("Pesquisar (substring):")

        if valor:
            resultado = df[df[coluna].str.contains(valor, case=False, na=False)]
            st.write(f"{len(resultado)} resultados:")
            st.dataframe(resultado.head(50), use_container_width=True)

###############################
# aba 3: consultas SQL
###############################
with aba3:
    st.markdown("""
        ### Consultas rápidas
    """)

# query default
    if "current_query" not in st.session_state:
        st.session_state.current_query = """
        SELECT 
            m.NomeMunicipio, 
            e.UF,
            COUNT(ca.NumeroDaAmostra) AS QuantidadeAmostras
        FROM 
            Municipio m 
            JOIN Estado e ON m.fk_Estado_UF = e.UF 
            JOIN Coleta_Amostra_LocalColeta ca ON m.CodigoDoIBGE = ca.fk_Municipio_CodigoDoIBGE
        GROUP BY 
            m.NomeMunicipio, 
            e.UF 
        HAVING COUNT(ca.NumeroDaAmostra) > 10;
        """

# definindo queries de cada botão
    PREDEFINED_QUERIES = {
        "mais_10_amostras": """
    SELECT 
        m.NomeMunicipio, 
        e.UF,
        COUNT(ca.NumeroDaAmostra) AS QuantidadeAmostras
    FROM 
        Municipio m 
        JOIN Estado e ON m.fk_Estado_UF = e.UF 
        JOIN Coleta_Amostra_LocalColeta ca ON m.CodigoDoIBGE = ca.fk_Municipio_CodigoDoIBGE
    GROUP BY 
        m.NomeMunicipio, 
        e.UF 
    HAVING COUNT(ca.NumeroDaAmostra) > 10;
    """,
        
        "municipios_abastecimento": """
    SELECT
        m.NomeMunicipio,
        e.UF,
        a.NomeDaFormaDeAbastecimento
    FROM Municipio m
        JOIN Estado e ON m.fk_Estado_UF = e.UF
        LEFT JOIN Abastecido ab ON m.CodigoDoIBGE = ab.fk_Municipio_CodigoDoIBGE
        LEFT JOIN Abastecimento a ON ab.fk_Abastecimento_CodigoFormaDeAbastecimento = a.CodigoFormaDeAbastecimento;
    """,

    "filtro_data": """
    SELECT
        m.NomeMunicipio,
        e.UF,
        ca.DataColeta,
        ca.Hora,
        ca.NumeroDaAmostra,
        c.Parametro_ciano_,
        a.Resultado,
        a.DataDoLaudo
    FROM Coleta_Amostra_LocalColeta ca
        JOIN Municipio m ON ca.fk_Municipio_CodigoDoIBGE = m.CodigoDoIBGE
        JOIN Estado e ON m.fk_Estado_UF = e.UF
        JOIN Analise a ON ca.DataColeta = a.fk_Amostra_DataColeta
            AND ca.Hora = a.fk_Amostra_Hora
            AND ca.NumeroDaAmostra = a.fk_Amostra_NumeroDaAmostra
        JOIN Classificacao c ON a.fk_Classificacao_Parametro_ciano_ = c.Parametro_ciano_
    WHERE ca.DataColeta = '2014-10-21';
    """
    }

    def set_query(query_key):
        st.session_state.current_query = PREDEFINED_QUERIES[query_key]

    c1, c2, c3 = st.columns(3)

    c1.button(
        "Municípios com mais de 10 amostras", 
        use_container_width=True,
        on_click=set_query,
        args=("mais_10_amostras",)
    )
        
    c2.button(
        "Municípios e formas de abastecimento", 
        use_container_width=True,
        on_click=set_query,
        args=("municipios_abastecimento",)
    )

    c3.button(
        "Filtro por data específica", 
        use_container_width=True,
        on_click=set_query,
        args=("filtro_data",)
    )

    st.markdown("""
        #### Dicionário de cada busca:
        - **Municípios com mais de 10 amostras.** Objetivo: Listar o nome dos municípios, seus estados e a quantidade de amostras coletadas 
        em cada município, considerando apenas municípios com mais de 10 amostras coletadas.
                    
        - **Municípios e formas de abastecimento.** Objetivo: Listar todos os municípios e seus estados, mostrando também o nome da forma de 
        abastecimento, se houver. Inclui municípios que não estão associados a nenhuma forma de abastecimento.
                    
        - **Filtro por data específica.** Obter detalhes completos (município, estado, data/hora da coleta, número da amostra, parâmetro 
        analisado, resultado e data do laudo) para todas as amostras coletadas em uma data específica (2014-10-21).
    """)

    st.markdown("---")

    query = st.text_area(
        "Sua consulta SQL:",
        value=st.session_state.current_query,
        height=200,
    )

# atualiza o estado se o usuário digitar algo
    st.session_state.current_query = query

# executar resultado
    if st.button("Executar", type="primary"):
        try:
            resultado = sqldf(query, tabelas)
            st.success(f"{len(resultado)} linhas retornadas.")
            st.dataframe(resultado, use_container_width=True)

            # botão para baixar
            csv = resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Baixar como CSV",
                csv,
                "resultado.csv",
                "text/csv",
                key='sql-download'
            )
        except Exception as e:
            st.error(f"Erro: {e}")
            st.info("Dica: a busca é case sensitive.\n Verifique nomes de tabelas e colunas (ex: 'Municipio', não 'municipio')")

st.markdown("---")
st.caption("Dados retirados no OpenDataSUS")