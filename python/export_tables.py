from dotenv import load_dotenv
from subprocess import run
from os import getenv

load_dotenv()
db_password=getenv("db_password")
db_user=getenv("db_user")
db_name=getenv("db_name")
export_path =getenv("db_export_path_file")

commands = [

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Estado" > "{export_path}\\Estado.csv"',
f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Municipio" > "{export_path}\\Municipio.csv"',

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Abastecimento" > "{export_path}\\Abastecimento.csv"',

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Abastecido" > "{export_path}\\Abastecido.csv"',

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Coleta_Amostra_LocalColeta" > "{export_path}\\Coleta_Amostra_LocalColeta.csv"',

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Classificacao" > "{export_path}\\Classificacao.csv"',

f'mysql -u{db_user} -p{db_password} --database={db_name} --default-character-set=utf8 --batch --column-names -e "SELECT * FROM Analise" > "{export_path}\\Analise.csv"'
]

for cmd in commands:
    print(f"Executando: {cmd}")
    run(cmd, shell=True)
    print("sucesso!")

print("Exportação concluída")