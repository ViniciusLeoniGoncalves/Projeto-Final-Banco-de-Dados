from dotenv import load_dotenv
from subprocess import run
from os import getenv, path

load_dotenv()

db_user = getenv("db_user")
db_password = getenv("db_password")
db_name = getenv("db_name")
current_path = path.dirname(path.abspath(__file__))
sql_path = path.join(current_path, "..", "sql", "tabelas_squema.sql") # caminho deste arquivo é usado como referencia, sem necessidade de salvar isso no .env, só as credenciais do banco local mesmo


commands = [
    f'mysql -u{db_user} -p{db_password} -e "source {sql_path}"',
    f'{current_path}\load_csv.py'
]

for cmd in commands:
    print(f"Executando: {cmd}")
    run(cmd, shell=True)
    print("sucesso!")

print("Execução concluída")
