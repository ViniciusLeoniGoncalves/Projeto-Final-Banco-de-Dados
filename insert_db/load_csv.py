from dotenv import load_dotenv
from os import getenv
import csv
import mysql.connector

# conexão com database
load_dotenv()
conn = mysql.connector.connect(
    host=getenv("db_host"),
    user=getenv("db_user"),
    password=getenv("db_password"),
    database=getenv("db_name")
)

cursor = conn.cursor()

with open("data/tabela.csv", encoding="utf-8-sig") as arquivo:
    leitor = csv.DictReader(arquivo)

    for linha in leitor:
       

        regiao = linha["Região Geográfica"]
        uf = linha["UF"]

        # Tabela 1.
        query = """
                    INSERT IGNORE INTO Estado (UF, Regiao)
                    VALUES (%s, %s);

                """
        valores = (uf,regiao)
        cursor.execute(query, valores)

        # Tabela 2.
        CodigoDoIBGE = linha["Código IBGE"]
        RegionalDeSaude = linha["Regional de Saúde"]
        NomeMunicipio = linha["Município"]
        
        query = """
                    INSERT IGNORE INTO Municipio (CodigoDoIBGE, RegionalDeSaude,NomeMunicipio,fk_Estado_UF) 
                    VALUES (%s,%s,%s,%s); 
                """
        valores = (CodigoDoIBGE,RegionalDeSaude,NomeMunicipio,uf)
        cursor.execute(query, valores)
        
        # Tabela 3.
        CodigoFormaDeAbastecimento=linha["Código Forma de Abastecimento"]
        TipoDaFormaDeAbastecimento=linha["Tipo da Forma de Abastecimento"]
        NomeETA_UTA=linha["Nome da ETA/UTA"]
        NomeDaFormaDeAbastecimento=linha["Nome da Forma de Abastecimento"]
        query = """
                   INSERT IGNORE INTO Abastecimento (CodigoFormaDeAbastecimento,TipoDaFormaDeAbastecimento,NomeETA_UTA,NomeDaFormaDeAbastecimento)
                   VALUES (%s,%s,%s,%s); 
                """
        valores = (CodigoFormaDeAbastecimento,TipoDaFormaDeAbastecimento,NomeETA_UTA,NomeDaFormaDeAbastecimento)
        cursor.execute(query, valores)

        # Tabela 4.
        query = """INSERT IGNORE INTO Abastecido (fk_Municipio_CodigoDoIBGE, fk_Abastecimento_CodigoFormaDeAbastecimento)
                VALUES (%s,%s);
                """
        valores= (CodigoDoIBGE,CodigoFormaDeAbastecimento)
        cursor.execute(query, valores)

        # Tabela 5.
        NumeroDaAmostra=linha["Número da amostra"]
        DataDeRegistroNoSISAGUA=linha["Data de Registro no SISAGUA"]
        DataColeta=linha["Data da Coleta"]
        DescricaoDoLocal=linha["Descrição do Local"]
        Zona=linha["Zona"]
        CategoriaArea=linha["Categoria Área"]
        Area = linha["Área"]
        TipoDoLocal= linha["Tipo do Local"]
        NomeLocal=linha["Local"]
        Latitude=linha["Latitude"]
        Longitude=linha["Longitude"]

        Procedencia=linha["Procedência da Coleta"]
        PontoDeColeta=linha["Ponto de Coleta"]
        Motivo=linha["Motivo da Coleta"]
        Hora=linha["Hora da coleta"]

        query = """INSERT IGNORE INTO Coleta_Amostra_LocalColeta 
        (NumeroDaAmostra, DataDeRegistroNoSISAGUA, DataColeta, DescricaoDoLocal, Zona, CategoriaArea, Area, TipoDoLocal, NomeLocal, Latitude, Longitude, fk_Municipio_CodigoDoIBGE, Procedencia, PontoDeColeta, Motivo, Hora)
        VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
        valores= (NumeroDaAmostra, DataDeRegistroNoSISAGUA, DataColeta, DescricaoDoLocal, Zona, CategoriaArea, Area, TipoDoLocal, NomeLocal, Latitude, Longitude, CodigoDoIBGE, Procedencia, PontoDeColeta, Motivo, Hora)
        cursor.execute(query, valores)

        #Tabela 6.
        Grupo = linha["Grupo"]
        Parametro_ciano_ = linha["Parâmetro (ciano)"]

        query = """
                INSERT IGNORE INTO Classificacao (Grupo, Parametro_Ciano_)
                VALUES (%s, %s);
                """
        valores = (Grupo, Parametro_ciano_)
        cursor.execute(query, valores)

        #Tabela 7.
        Resultado = linha["Resultado"]
        DataDoLaudo = linha["Data do Laudo"]

        query = """
                INSERT IGNORE INTO Analise (fk_Amostra_DataColeta,fk_Amostra_Hora,fk_Amostra_NumeroDaAmostra,fk_Classificacao_Parametro_ciano_, Resultado, DataDoLaudo)  VALUES (%s,%s,%s,%s,%s,%s);
                """
        valores = (DataColeta,Hora,NumeroDaAmostra,Parametro_ciano_,Resultado,DataDoLaudo)
        cursor.execute(query, valores)

conn.commit()
cursor.close()
conn.close()

print("Inserção concluída!\n")
