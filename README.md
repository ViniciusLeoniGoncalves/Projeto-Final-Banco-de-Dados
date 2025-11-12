# SISAGUA - Normalização de Banco de Dados e Carga Automática (Python + MySQL)

Este projeto é o **trabalho final da disciplina de Banco de Dados dee 2025.2**.  
Nosso objetivo é normalizar e armazenar **dados públicos do Sistema de Informação de Vigilância da Qualidade da Água para Consumo Humano (SISAGUA)** referentes a análises de concentração de cianobactérias e cianotoxinas na água potável de consumo em diversos locais do Brasil.

Os dados foram extraídos de arquivos CSV de domínio público do Sistema Único de Saúde (SUS) Brasileiro pelo [OpenDataSUS](https://opendatasus.saude.gov.br/dataset/sisagua-vigilancia-cianobacterias-e-cianotoxinas).

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|-----------|-----|
| Python 3.9+ | Automação da carga |
| MySQL 8.0 | Banco relacional |
| CSV | Fonte de dados |
| `mysql-connector-python` | Driver de comunicação pra automatizar população do banco |
| `csv` | Manipulação e leitura da fonte de dados |
| `python-dotenv` | Controle seguro de credenciais |
| `streamlit` | Para que seja exibido o frontEnd |
| `Streamlit` | Interface web interativa para análise dos dados |
| `pandas / pandasql` | Manipulação de dados e consultas SQL em memória |
| `csv` | Leitura e escrita dos arquivos de dados |

## Instalação das dependências:

```bash
pip install mysql-connector-python 
pip install python-dotenv
pip install csv
pip install streamlit
pip install pandas
pip install pandasql


```
---

## Credenciais

Crie um arquivo .env na raiz do projeto com suas credenciais:
```bash
db_host=localhost
db_user=root
db_password=SUASENHA
db_name=NOMEdoBANCO
db_export_path_file="C:\\Users\\SeuUsuario\\CaminhoCompleto\\Projeto-Final-Banco-de-Dados\\data\\db_export"

```

## Executando a interface Web (Streamlit)

O Streamlit permite visualizar e consultar os dados exportados do banco.
Para executá-la, abra um terminal na raiz do projeto e rode:

```bash
streamlit run streamlit/app.py
```

Esse comando garante que os caminhos relativos à pasta com o banco de dados exportado funcionem corretamente.
