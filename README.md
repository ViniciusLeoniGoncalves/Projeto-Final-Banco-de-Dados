# SISAGUA - Normalização de Banco de Dados e Carga Automática (Python + MySQL)

Este projeto é o trabalho final da disciplina de Banco de Dados dee 2025.2.  
Nosso objetivo é normalizar e armazenar **dados públicos do Sistema de Informação de Vigilância da Qualidade da Água para Consumo Humano (SISAGUA)** referentes a análises de concentração de cianobactérias e cianotoxinas na água potável de consumo em diversos locais do Brasil.

Os dados foram extraídos de arquivos CSV de domínio público do Sistema Único de Saúde (SUS) Brasileiro pelo [OpenDataSUS](https://opendatasus.saude.gov.br/dataset/sisagua-vigilancia-cianobacterias-e-cianotoxinas).

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|-----------|-----|
| Python 3.9+ | Automação da carga |
| MySQL 8.0 | Banco relacional |
| CSV | Fonte de dados |
| `mysql-connector-python` | Driver de comunicação |
| `csv` | Manipulação e leitura da fonte de dados |
| `python-dotenv` | Controle seguro de credenciais |

Instalação das dependências:

```bash
pip install mysql-connector-python 
pip install dotenv
pip install csv


```
---

Credenciais

Crie um arquivo .env na raiz do projeto com suas credenciais:
```bash
db_host=localhost
db_user=root
db_password=SUASENHA
db_name=NOMEdoBANCO
db_export_path_file="C:\\Caminho\\inteiro\\Repositoriolocal\\Projeto-Final-Banco-de-Dados\\data\\db_export"

```
