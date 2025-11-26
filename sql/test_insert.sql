
USE Projeto_final;
--Inserção em ordem de dependencias, fizemos essas inserções para termos ideia da ordem de como fazer no script de população do banco

-- Tabela 1. Estado
INSERT INTO Estado VALUES ('SP', 'SUDESTE');
INSERT INTO Estado VALUES ('AL', 'NORDESTE');

-- Tabela 2. Município
INSERT INTO Municipio (CodigoDoIBGE, RegionalDeSaude,NomeMunicipio,fk_Estado_UF) VALUES ('353770', 'GVS XI - ARAÇATUBA','PIACATU','SP');
INSERT INTO Municipio VALUES ('270240', '10 REGIÃO DEG AL', 'DELMIRO GOUVEIA','AL');

-- Tabela 3. Forma de Abastecimento
INSERT INTO Abastecimento VALUES ('S353770000001', 'SAA', NULL,'PIACATU(19)');
INSERT INTO Abastecimento VALUES ('S270240000004', 'SAA', NULL, 'SAA DE DELMIRO GOUVEIA SALGADO E CRUZ LAGOINHA');

-- Tabela 4. Abastecido
INSERT INTO Abastecido VALUES ('353770', 'S353770000001');
INSERT INTO Abastecido VALUES ('270240', 'S270240000004');


-- Tabela 5. Coleta_Amostra_LocalColeta

INSERT INTO Coleta_Amostra_LocalColeta 
(NumeroDaAmostra, DataDeRegistroNoSISAGUA, DataColeta, DescricaoDoLocal, Zona, CategoriaArea, Area, TipoDoLocal, NomeLocal, Latitude, Longitude, fk_Municipio_CodigoDoIBGE, Procedencia, PontoDeColeta, Motivo, Hora)
VALUES 
('30', '2014-11-11 08:51:26', '2014-10-21', 'RUA SEVERINO PERINA, 1043', 'Urbana', 'Bairro', 'CENTRO', NULL, NULL, NULL, NULL, '353770', 'SISTEMA DE DISTRIBUIÇÃO', 'Cavalete/Hidrômetro', 'Rotina', '09:40'),

('1631.00/2015', '2019-09-03 09:42:53', '2015-05-27', 'PONTO DE CAPTAÇÃO ORIGEM ETA (SALGADO I)', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '270240', 'PONTO DE CAPTAÇÃO ORIGEM ETA (SALGADO I)', NULL, 'Rotina', '09:00');

-- Tabela 6. Classificação
INSERT INTO Classificacao (Grupo, Parametro_Ciano_) VALUES ('Cianotoxinas', 'Cilindrospermopsinas (µg/L)');
INSERT INTO Classificacao (Grupo, Parametro_Ciano_) VALUES ('Cianotoxinas', 'Miscrocistinas (µg/L)');


-- Tabela 7. Analise
INSERT INTO Analise (fk_Amostra_DataColeta,fk_Amostra_Hora,fk_Amostra_NumeroDaAmostra,fk_Classificacao_Parametro_ciano_, Resultado, DataDoLaudo)  VALUES ('2014-10-21','09:40','30', 'Cilindrospermopsinas (µg/L)',0, '2014-10-24');
INSERT INTO Analise (fk_Amostra_DataColeta,fk_Amostra_Hora,fk_Amostra_NumeroDaAmostra,fk_Classificacao_Parametro_ciano_, Resultado, DataDoLaudo) VALUES ('2015-05-27','09:00','1631.00/2015', 'Miscrocistinas (µg/L)', 0, '2015-06-01');

-- Visualizando as tabelas pós inserção

SELECT * FROM Estado;

SELECT * FROM Municipio;

SELECT * FROM Abastecimento;

SELECT * FROM Abastecido;

SELECT * FROM Coleta_Amostra_LocalColeta;

SELECT * FROM Classificacao;

SELECT * FROM Analise;
