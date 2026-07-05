DROP TABLE IF EXISTS visualiza CASCADE;
DROP TABLE IF EXISTS colabora CASCADE;
DROP TABLE IF EXISTS contem CASCADE;
DROP TABLE IF EXISTS Hist_Reproducao CASCADE;
DROP TABLE IF EXISTS Pagamento CASCADE;
DROP TABLE IF EXISTS Playlist CASCADE;
DROP TABLE IF EXISTS Humor CASCADE;
DROP TABLE IF EXISTS Musica CASCADE;
DROP TABLE IF EXISTS Genero CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS Artista CASCADE;
DROP TABLE IF EXISTS Usuario CASCADE;
DROP TABLE IF EXISTS Plano CASCADE;
DROP TABLE IF EXISTS Anuncio CASCADE;

CREATE TABLE Anuncio (
    id_anuncio INT PRIMARY KEY,
    empresa_anunciante VARCHAR(150),
    tempo_duracao_segundos INT
);

CREATE TABLE Plano (
    id_plano INT PRIMARY KEY,
    tipo VARCHAR(50),
    valor_mensal DECIMAL(10,2),
    beneficios TEXT
);

CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY,
    id_plano INT,
    data_cadastro DATE,
    nome VARCHAR(100),
    cpf CHAR(11),
    status_conta VARCHAR(20)
        CHECK (status_conta IN ('ATIVA','INATIVA','SUSPENSA')),
    FOREIGN KEY (id_plano) REFERENCES Plano(id_plano)
);

CREATE TABLE Artista (
    id_artista INT PRIMARY KEY,
    bio TEXT,
    nome_artistico VARCHAR(200)
);

CREATE TABLE Album (
    id_album INT PRIMARY KEY,
    id_artista INT,
    titulo VARCHAR(200),
    data_lancamento DATE,
    FOREIGN KEY (id_artista) REFERENCES Artista(id_artista)
);

CREATE TABLE Genero (
    id_genero INT PRIMARY KEY,
    nome VARCHAR(100),
    descricao TEXT
);

CREATE TABLE Musica (
    id_musica INT PRIMARY KEY,
    titulo VARCHAR(200),
    duracao_segundos INT,
    id_album INT,
    id_genero INT,
    FOREIGN KEY (id_album) REFERENCES Album(id_album),
    FOREIGN KEY (id_genero) REFERENCES Genero(id_genero)
);

CREATE TABLE Humor (
    id_humor INT PRIMARY KEY,
    id_usuario INT,
    data_requisicao TIMESTAMP,
    descricao VARCHAR(500),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Playlist (
    id_playlist INT PRIMARY KEY,
    id_humor INT,
    nome VARCHAR(100),
    data_criacao DATE,
    gerada_por_ia BOOLEAN,
    FOREIGN KEY (id_humor) REFERENCES Humor(id_humor)
);

CREATE TABLE Pagamento (
    id_pagamento INT PRIMARY KEY,
    id_usuario INT,
    valor_pago DECIMAL(10,2),
    data_pagamento DATE,
    status VARCHAR(20),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Hist_Reproducao (
    id_reproducao INT PRIMARY KEY,
    data_hora TIMESTAMP,
    id_musica INT,
    id_usuario INT,
    FOREIGN KEY (id_musica) REFERENCES Musica(id_musica),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE contem (
    id_musica INT,
    id_playlist INT,
    PRIMARY KEY (id_musica, id_playlist),
    FOREIGN KEY (id_musica) REFERENCES Musica(id_musica),
    FOREIGN KEY (id_playlist) REFERENCES Playlist(id_playlist)
);

CREATE TABLE colabora (
    id_playlist INT,
    id_usuario INT,
    PRIMARY KEY (id_playlist, id_usuario),
    FOREIGN KEY (id_playlist) REFERENCES Playlist(id_playlist),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE visualiza (
    id_anuncio INT,
    id_usuario INT,
    data_vizualizacao DATE,
    PRIMARY KEY (id_anuncio, id_usuario, data_vizualizacao),
    FOREIGN KEY (id_anuncio) REFERENCES Anuncio(id_anuncio),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);
