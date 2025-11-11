/* Lógico_2: */

CREATE TABLE Estado (
    UF CHAR(2) PRIMARY KEY,
    Regiao VARCHAR(255)
);

CREATE TABLE Municipio (
    CodigoDoIBGE VARCHAR(255) PRIMARY KEY,
    RegionalDeSaude VARCHAR(255),
    NomeMunicipio VARCHAR(255),
    fk_Estado_UF CHAR(2) NOT NULL
);

CREATE TABLE Abastecimento (
  CodigoFormaDeAbastecimento VARCHAR(255) PRIMARY KEY,
    TipoDaFormaDeAbastecimento VARCHAR(255),
      NomeETA_UTA VARCHAR(255),
    NomeDaFormaDeAbastecimento VARCHAR(255)
);

CREATE TABLE Abastecido (
    fk_Municipio_CodigoDoIBGE VARCHAR(255),
  fk_Abastecimento_CodigoFormaDeAbastecimento VARCHAR(255),
    PRIMARY KEY (fk_Municipio_CodigoDoIBGE, fk_Abastecimento_CodigoFormaDeAbastecimento)
);
 
 CREATE TABLE Coleta_Amostra_LocalColeta (
    NumeroDaAmostra VARCHAR(255),
    DataDeRegistroNoSISAGUA DATETIME,
   
    DataColeta DATE,
   	DescricaoDoLocal VARCHAR(255),
    Zona VARCHAR(255),
    CategoriaArea VARCHAR(255),
    Area VARCHAR(255),
    TipoDoLocal VARCHAR(255),
    NomeLocal VARCHAR(255),
    Latitude VARCHAR(255),
    Longitude VARCHAR(255),
   	fk_Municipio_CodigoDoIBGE VARCHAR(255),
   
   	Procedencia VARCHAR(255),
    PontoDeColeta VARCHAR(255),
    Motivo VARCHAR(255),
    Hora TIME,
    PRIMARY KEY (DataColeta, Hora, NumeroDaAmostra)
);
 
CREATE TABLE Classificacao (
    Grupo VARCHAR(255),
    Parametro_ciano_ VARCHAR(255) PRIMARY KEY
);


CREATE TABLE Analise (
    fk_Amostra_DataColeta DATE,
    fk_Amostra_Hora TIME,
    fk_Amostra_NumeroDaAmostra VARCHAR(255),
  
    fk_Classificacao_Parametro_ciano_ VARCHAR(255),
    Resultado DECIMAL(8,2),
    DataDoLaudo DATE,
  
    PRIMARY KEY (DataDoLaudo, fk_Amostra_NumeroDaAmostra, fk_Classificacao_Parametro_ciano_)
);


ALTER TABLE Municipio ADD CONSTRAINT FK_Municipio_2
    FOREIGN KEY (fk_Estado_UF)
    REFERENCES Estado (UF)
    ON DELETE NO ACTION;
   
ALTER TABLE Coleta_Amostra_LocalColeta
ADD UNIQUE (NumeroDaAmostra);
 
ALTER TABLE Coleta_Amostra_LocalColeta ADD CONSTRAINT FK_Coleta_Amostra_LocalColeta_2
    FOREIGN KEY (fk_Municipio_CodigoDoIBGE)
    REFERENCES Municipio (CodigoDoIBGE);
    
ALTER TABLE Analise
ADD CONSTRAINT FK_Analise_2
    FOREIGN KEY (fk_Amostra_DataColeta, fk_Amostra_Hora, fk_Amostra_NumeroDaAmostra)
    REFERENCES Coleta_Amostra_LocalColeta (DataColeta, Hora, NumeroDaAmostra)
    ON DELETE CASCADE;
 
ALTER TABLE Analise ADD CONSTRAINT FK_Analise_3
    FOREIGN KEY (fk_Classificacao_Parametro_ciano_)
    REFERENCES Classificacao (Parametro_ciano_)
    ON NO ACTION;
 
ALTER TABLE Abastecido ADD CONSTRAINT FK_Abastecido_1
    FOREIGN KEY (fk_Municipio_CodigoDoIBGE)
    REFERENCES Municipio (CodigoDoIBGE)
    ON DELETE NO ACTION;
 
ALTER TABLE Abastecido ADD CONSTRAINT FK_Abastecido_2
    FOREIGN KEY (fk_Abastecimento_CodigoFormaDeAbastecimento)
    REFERENCES Abastecimento (CodigoFormaDeAbastecimento)
    ON DELETE CASCADE;
