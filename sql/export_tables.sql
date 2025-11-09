SELECT * FROM Estado
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Estado.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
SELECT * FROM Municipio
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Municipio.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT * FROM Abastecimento
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Abastecimento.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT * FROM Abastecido
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Abastecido.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT * FROM Coleta_Amostra_LocalColeta
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Coleta_Amostra_LocalColeta.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT * FROM Classificacao
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Classificacao.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT * FROM Analise
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Analise.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

