import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import google.generativeai as genai
import psycopg2

engine = create_engine(
    "postgresql+psycopg2://postgres:060806@localhost:5432/Velvtune", pool_pre_ping=True
)

def executar(sql, params=None):
    try:
        with engine.begin() as conn:
            if params:
                conn.execute(text(sql), params)
            else:
                conn.execute(text(sql))
        print("Operação realizada com sucesso!")
    except Exception as e: import traceback
    traceback.print_exc()

def listar(tabela, ordem=None):
    try:
        q = f"SELECT * FROM {tabela}"
        if ordem:
            q += f" ORDER BY {ordem}"
        df = pd.read_sql(q, engine)
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print("Erro:", e)
        return None

def input_int(msg):
    while True:
        v = input(msg).strip()
        if v.lstrip('-').isdigit():
            return int(v)
        print("Digite um número inteiro válido.")

def input_decimal(msg):
    while True:
        v = input(msg).strip()
        try:
            return float(v)
        except ValueError:
            print("Digite um valor decimal válido (ex: 9.90).")

def input_data(msg):
    while True:
        v = input(msg + " (AAAA-MM-DD): ").strip()
        if len(v) == 10 and v[4] == '-' and v[7] == '-':
            return v
        print("Formato inválido. Use AAAA-MM-DD.")

def input_datetime(msg):
    while True:
        v = input(msg + " (AAAA-MM-DD HH:MM:SS): ").strip()
        if len(v) >= 19:
            return v
        print("Formato inválido. Use AAAA-MM-DD HH:MM:SS.")

def input_bool(msg):
    while True:
        v = input(msg + " (s/n): ").strip().lower()
        if v in ('s', 'n'):
            return v == 's'
        print("Digite 's' para sim ou 'n' para não.")

def pressione_enter():
    input("\nPressione Enter para continuar...")

from sqlalchemy import text

def apagar_banco():
    confirma = input("Isso apagará todas as tabelas. Deseja continuar? ")

    if confirma.lower() != "s":
        print("Operação cancelada.")
        return

    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS visualiza CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS colabora CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS contem CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Hist_Reproducao CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Pagamento CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Playlist CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Humor CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Musica CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Genero CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Album CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Artista CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Usuario CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Plano CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS Anuncio CASCADE"))

        print("\nBanco apagado com sucesso!")

    except Exception as e:
        print("Erro:", e)

from sqlalchemy import text

def recriar_banco():
    confirma = input("Recriar todas as tabelas? ")

    if confirma.lower() != "s":
        return

    try:
        with engine.begin() as conn:

            conn.execute(text("""
            CREATE TABLE Anuncio (
                id_anuncio INT PRIMARY KEY,
                empresa_anunciante VARCHAR(150),
                tempo_duracao_segundos INT)"""))

            conn.execute(text("""
            CREATE TABLE Plano (
                id_plano INT PRIMARY KEY,
                tipo VARCHAR(50),
                valor_mensal DECIMAL(10,2),
                beneficios TEXT)"""))

            conn.execute(text("""
            CREATE TABLE Usuario (
                id_usuario INT PRIMARY KEY,
                id_plano INT,
                data_cadastro DATE,
                nome VARCHAR(100),
                cpf CHAR(11),
                status_conta VARCHAR(20)
                CHECK (status_conta IN ('ATIVA','INATIVA','SUSPENSA')),
                FOREIGN KEY (id_plano) REFERENCES Plano(id_plano))"""))

            conn.execute(text("""
            CREATE TABLE Artista (
                id_artista INT PRIMARY KEY,
                bio TEXT,
                nome_artistico VARCHAR(200))"""))

            conn.execute(text("""
            CREATE TABLE Album (
                id_album INT PRIMARY KEY,
                id_artista INT,
                titulo VARCHAR(200),
                data_lancamento DATE,
                FOREIGN KEY (id_artista) REFERENCES Artista(id_artista))"""))

            conn.execute(text("""
            CREATE TABLE Genero (
                id_genero INT PRIMARY KEY,
                nome VARCHAR(100),
                descricao TEXT)"""))

            conn.execute(text("""
            CREATE TABLE Musica (
                id_musica INT PRIMARY KEY,
                titulo VARCHAR(200),
                duracao_segundos INT,
                id_album INT,
                id_genero INT,
                FOREIGN KEY (id_album) REFERENCES Album(id_album),
                FOREIGN KEY (id_genero) REFERENCES Genero(id_genero))"""))

            conn.execute(text("""
            CREATE TABLE Humor (
                id_humor INT PRIMARY KEY,
                id_usuario INT,
                data_requisicao TIMESTAMP,
                descricao VARCHAR(500),
                FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))"""))

            conn.execute(text("""
            CREATE TABLE Playlist (
                id_playlist INT PRIMARY KEY,
                id_humor INT,
                nome VARCHAR(100),
                data_criacao DATE,
                gerada_por_ia BOOLEAN,
                FOREIGN KEY (id_humor) REFERENCES Humor(id_humor))"""))

            conn.execute(text("""
            CREATE TABLE Pagamento (
                id_pagamento INT PRIMARY KEY,
                id_usuario INT,
                valor_pago DECIMAL(10,2),
                data_pagamento DATE,
                status VARCHAR(20),
                FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))"""))

            conn.execute(text("""
            CREATE TABLE Hist_Reproducao (
                id_reproducao INT PRIMARY KEY,
                data_hora TIMESTAMP,
                id_musica INT,
                id_usuario INT,
                FOREIGN KEY (id_musica) REFERENCES Musica(id_musica),
                FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))"""))

            conn.execute(text("""
            CREATE TABLE contem (
                id_musica INT,
                id_playlist INT,
                PRIMARY KEY (id_musica, id_playlist),
                FOREIGN KEY (id_musica) REFERENCES Musica(id_musica),
                FOREIGN KEY (id_playlist) REFERENCES Playlist(id_playlist))"""))

            conn.execute(text("""
            CREATE TABLE colabora (
                id_playlist INT,
                id_usuario INT,
                PRIMARY KEY (id_playlist, id_usuario),
                FOREIGN KEY (id_playlist) REFERENCES Playlist(id_playlist),
                FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))"""))

            conn.execute(text("""
            CREATE TABLE visualiza (
                id_anuncio INT,
                id_usuario INT,
                data_vizualizacao DATE,
                PRIMARY KEY (id_anuncio, id_usuario, data_vizualizacao),
                FOREIGN KEY (id_anuncio) REFERENCES Anuncio(id_anuncio),
                FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))"""))

        popular_banco()

        print("\nBanco recriado com sucesso!")

    except Exception as e:
        print("Erro:", e)

def popular_banco():
    with engine.begin() as conn:

        conn.execute(text("""
            INSERT INTO Plano VALUES
            (1, 'Gratuito', 0.00, 'Com anúncios'),
            (2, 'Premium', 29.90, 'Sem anúncios'),
            (3, 'Família', 49.90, 'Até 6 contas');"""))

        conn.execute(text("""
            INSERT INTO Anuncio VALUES
            (1, 'JBL', 30),
            (2, 'Samsung', 15),
            (3, 'Airbuds', 20);"""))

        conn.execute(text("""
            INSERT INTO Usuario VALUES
            (1, 1, '2025-01-10', 'Fulano', '11111111111', 'ATIVA'),
            (2, 2, '2025-02-15', 'Ciclano', '22222222222', 'ATIVA'),
            (3, 3, '2025-03-01', 'Beltrano', '33333333333', 'ATIVA');"""))

        conn.execute(text("""
            INSERT INTO Artista VALUES
            (1, 'Cantora pop canadense', 'Tate McRae'),
            (2, 'Grupo feminino de k-pop', 'ILLIT'),
            (3, 'Banda de rock japonesa', 'UVERworld');"""))

        conn.execute(text("""
            INSERT INTO Genero VALUES
            (1, 'Pop', 'Música Pop'),
            (2, 'KPop', 'Música K-Pop'),
            (3, 'Rock', 'Música Rock');"""))

        conn.execute(text("""
            INSERT INTO Album VALUES
            (1, 1, 'THINK LATER', '2023-12-08'),
            (2, 2, 'bomb', '2025-06-16'),
            (3, 3, 'LIVING THINGS', '2012-06-19');"""))

        conn.execute(text("""
            INSERT INTO Musica VALUES
            (1, 'greedy', 129, 1, 1),
            (2, 'jellyous', 163, 2, 2),
            (3, 'ILL BE GONE', 211, 3, 3);"""))

        conn.execute(text("""
            INSERT INTO Humor VALUES
            (1, 1, '2025-06-01 09:00:00', 'Triste'),
            (2, 2, '2025-06-01 10:00:00', 'Animada'),
            (3, 3, '2025-06-01 11:00:00', 'Relaxante');"""))

        conn.execute(text("""
            INSERT INTO Playlist VALUES
            (1, 1, 'Favoritas', '2025-06-01', TRUE),
            (2, 2, 'Treino', '2025-06-02', FALSE),
            (3, 3, 'Viagem', '2025-06-03', TRUE);"""))

        conn.execute(text("""
            INSERT INTO Pagamento VALUES
            (1, 2, 29.90, '2025-06-05', 'Pago'),
            (2, 3, 49.90, '2025-06-05', 'Pago');"""))

        conn.execute(text("""
            INSERT INTO Hist_Reproducao VALUES
            (1, '2025-06-10 09:10:00', 1, 1),
            (2, '2025-06-10 09:15:00', 2, 2),
            (3, '2025-06-10 09:20:00', 3, 3),
            (4, '2025-06-10 09:25:00', 2, 1),
            (5, '2025-06-10 09:30:00', 1, 2);"""))

        conn.execute(text("""
            INSERT INTO contem VALUES
            (1,1),
            (2,1),
            (2,2),
            (3,3);"""))

        conn.execute(text("""
            INSERT INTO colabora VALUES
            (1,2),
            (1,3),
            (2,1);"""))

        conn.execute(text("""
            INSERT INTO visualiza VALUES
            (1,1,'2025-06-01'),
            (2,2,'2025-06-02'),
            (3,3,'2025-06-03');"""))
        
        print("Banco populado com sucesso")

genai.configure(api_key="AQ.Ab8RN6L55mhed0YKsK-yifMZBI56adL95NgTbA4ONOstrq1QxQ")

def llm_ia():

    model = genai.GenerativeModel("gemini-flash-latest")

    humor = input("Humor do usuário: ")
    genero = input("Gênero favorito: ")

    prompt = f"""
    Você é um assistente do VelvTune.

    O usuário informou:

    Humor: {humor}
    Gênero favorito: {genero}

    Sugira uma playlist com 5 músicas e explique rapidamente cada sugestão.
    """

    try:
        resposta = model.generate_content(prompt)

        print("\n--- Resposta da IA ---")
        print(resposta.text)

    except Exception as e:
        print(e)

def inserir_anuncio():
    print("\n--- Inserir Anúncio ---")
    listar("Anuncio", "id_anuncio")
    id_a = input_int("id_anuncio: ")
    empresa = input("empresa_anunciante: ").strip()
    tempo = input_int("tempo_duracao_segundos: ")
    executar(
        "INSERT INTO Anuncio VALUES (:id, :emp, :tempo)",
        {"id": id_a, "emp": empresa, "tempo": tempo}
    )

def atualizar_anuncio():
    print("\n--- Atualizar Anúncio ---")
    listar("Anuncio", "id_anuncio")
    id_a = input_int("id_anuncio a atualizar: ")
    empresa = input("Nova empresa_anunciante (Enter para manter): ").strip()
    tempo = input("Novo tempo_duracao_segundos (Enter para manter): ").strip()
    if empresa:
        executar("UPDATE Anuncio SET empresa_anunciante=:v WHERE id_anuncio=:id", {"v": empresa, "id": id_a})
    if tempo.lstrip('-').isdigit():
        executar("UPDATE Anuncio SET tempo_duracao_segundos=:v WHERE id_anuncio=:id", {"v": int(tempo), "id": id_a})

def excluir_anuncio():
    print("\n--- Excluir Anúncio ---")
    listar("Anuncio", "id_anuncio")
    id_a = input_int("id_anuncio a excluir: ")
    executar("DELETE FROM Anuncio WHERE id_anuncio=:id", {"id": id_a})

def consultar_anuncio():
    print("\n--- Consultar Anúncios ---")
    listar("Anuncio", "id_anuncio")

def inserir_plano():
    print("\n--- Inserir Plano ---")
    listar("Plano", "id_plano")
    id_p = input_int("id_plano: ")
    tipo = input("tipo: ").strip()
    valor = input_decimal("valor_mensal: ")
    beneficios = input("beneficios: ").strip()
    executar(
        "INSERT INTO Plano VALUES (:id, :tipo, :valor, :ben)",
        {"id": id_p, "tipo": tipo, "valor": valor, "ben": beneficios}
    )

def atualizar_plano():
    print("\n--- Atualizar Plano ---")
    listar("Plano", "id_plano")
    id_p = input_int("id_plano a atualizar: ")
    tipo = input("Novo tipo (Enter para manter): ").strip()
    valor = input("Novo valor_mensal (Enter para manter): ").strip()
    beneficios = input("Novos beneficios (Enter para manter): ").strip()
    if tipo:
        executar("UPDATE Plano SET tipo=:v WHERE id_plano=:id", {"v": tipo, "id": id_p})
    if valor:
        executar("UPDATE Plano SET valor_mensal=:v WHERE id_plano=:id", {"v": float(valor), "id": id_p})
    if beneficios:
        executar("UPDATE Plano SET beneficios=:v WHERE id_plano=:id", {"v": beneficios, "id": id_p})

def excluir_plano():
    print("\n--- Excluir Plano ---")
    listar("Plano", "id_plano")
    id_p = input_int("id_plano a excluir: ")
    executar("DELETE FROM Plano WHERE id_plano=:id", {"id": id_p})

def consultar_plano():
    print("\n--- Consultar Planos ---")
    listar("Plano", "id_plano")

def inserir_usuario():
    print("\n--- Inserir Usuário ---")
    listar("Plano", "id_plano")
    id_u = input_int("id_usuario: ")
    id_p = input_int("id_plano: ")
    data_cad = input_data("data_cadastro")
    nome = input("nome: ").strip()
    cpf = input("cpf (11 dígitos): ").strip()
    status = ""
    while status not in ("ATIVA", "INATIVA", "SUSPENSA"):
        status = input("status_conta (ATIVA/INATIVA/SUSPENSA): ").strip().upper()
    executar(
        "INSERT INTO Usuario VALUES (:id, :plano, :data, :nome, :cpf, :status)",
        {"id": id_u, "plano": id_p, "data": data_cad, "nome": nome, "cpf": cpf, "status": status}
    )

def atualizar_usuario():
    print("\n--- Atualizar Usuário ---")
    listar("Usuario", "id_usuario")
    id_u = input_int("id_usuario a atualizar: ")
    nome = input("Novo nome (Enter para manter): ").strip()
    status = input("Novo status_conta (ATIVA/INATIVA/SUSPENSA) (Enter para manter): ").strip().upper()
    id_p = input("Novo id_plano (Enter para manter): ").strip()
    if nome:
        executar("UPDATE Usuario SET nome=:v WHERE id_usuario=:id", {"v": nome, "id": id_u})
    if status in ("ATIVA", "INATIVA", "SUSPENSA"):
        executar("UPDATE Usuario SET status_conta=:v WHERE id_usuario=:id", {"v": status, "id": id_u})
    if id_p.isdigit():
        executar("UPDATE Usuario SET id_plano=:v WHERE id_usuario=:id", {"v": int(id_p), "id": id_u})

def excluir_usuario():
    print("\n--- Excluir Usuário ---")
    listar("Usuario", "id_usuario")
    id_u = input_int("id_usuario a excluir: ")
    executar("DELETE FROM Usuario WHERE id_usuario=:id", {"id": id_u})

def consultar_usuario_tabela():
    print("\n--- Consultar Usuários ---")
    listar("Usuario", "id_usuario")

def inserir_artista():
    print("\n--- Inserir Artista ---")
    id_a = input_int("id_artista: ")
    nome = input("nome_artistico: ").strip()
    bio = input("bio: ").strip()
    executar(
        "INSERT INTO Artista VALUES (:id, :bio, :nome)",
        {"id": id_a, "bio": bio, "nome": nome}
    )

def atualizar_artista():
    print("\n--- Atualizar Artista ---")
    listar("Artista", "id_artista")
    id_a = input_int("id_artista a atualizar: ")
    nome = input("Novo nome_artistico (Enter para manter): ").strip()
    bio = input("Nova bio (Enter para manter): ").strip()
    if nome:
        executar("UPDATE Artista SET nome_artistico=:v WHERE id_artista=:id", {"v": nome, "id": id_a})
    if bio:
        executar("UPDATE Artista SET bio=:v WHERE id_artista=:id", {"v": bio, "id": id_a})

def excluir_artista():
    print("\n--- Excluir Artista ---")
    listar("Artista", "id_artista")
    id_a = input_int("id_artista a excluir: ")
    executar("DELETE FROM Artista WHERE id_artista=:id", {"id": id_a})

def consultar_artista_tabela():
    print("\n--- Consultar Artistas ---")
    listar("Artista", "id_artista")

def inserir_album():
    print("\n--- Inserir Álbum ---")
    listar("Artista", "id_artista")
    id_al = input_int("id_album: ")
    id_ar = input_int("id_artista: ")
    titulo = input("titulo: ").strip()
    data_lanc = input_data("data_lancamento")
    executar(
        "INSERT INTO Album VALUES (:id, :artista, :titulo, :data)",
        {"id": id_al, "artista": id_ar, "titulo": titulo, "data": data_lanc}
    )

def atualizar_album():
    print("\n--- Atualizar Álbum ---")
    listar("Album", "id_album")
    id_al = input_int("id_album a atualizar: ")
    titulo = input("Novo titulo (Enter para manter): ").strip()
    data_lanc = input("Nova data_lancamento (AAAA-MM-DD) (Enter para manter): ").strip()
    if titulo:
        executar("UPDATE Album SET titulo=:v WHERE id_album=:id", {"v": titulo, "id": id_al})
    if len(data_lanc) == 10:
        executar("UPDATE Album SET data_lancamento=:v WHERE id_album=:id", {"v": data_lanc, "id": id_al})

def excluir_album():
    print("\n--- Excluir Álbum ---")
    listar("Album", "id_album")
    id_al = input_int("id_album a excluir: ")
    executar("DELETE FROM Album WHERE id_album=:id", {"id": id_al})

def consultar_album():
    print("\n--- Consultar Álbuns ---")
    listar("Album", "id_album")

def inserir_genero():
    print("\n--- Inserir Gênero ---")
    id_g = input_int("id_genero: ")
    nome = input("nome: ").strip()
    desc = input("descricao: ").strip()
    executar(
        "INSERT INTO Genero VALUES (:id, :nome, :desc)",
        {"id": id_g, "nome": nome, "desc": desc}
    )

def atualizar_genero():
    print("\n--- Atualizar Gênero ---")
    listar("Genero", "id_genero")
    id_g = input_int("id_genero a atualizar: ")
    nome = input("Novo nome (Enter para manter): ").strip()
    desc = input("Nova descricao (Enter para manter): ").strip()
    if nome:
        executar("UPDATE Genero SET nome=:v WHERE id_genero=:id", {"v": nome, "id": id_g})
    if desc:
        executar("UPDATE Genero SET descricao=:v WHERE id_genero=:id", {"v": desc, "id": id_g})

def excluir_genero():
    print("\n--- Excluir Gênero ---")
    listar("Genero", "id_genero")
    id_g = input_int("id_genero a excluir: ")
    executar("DELETE FROM Genero WHERE id_genero=:id", {"id": id_g})

def consultar_genero_tabela():
    print("\n--- Consultar Gêneros ---")
    listar("Genero", "id_genero")

def inserir_musica():
    print("\n--- Inserir Música ---")
    listar("Album", "id_album")
    listar("Genero", "id_genero")
    id_m = input_int("id_musica: ")
    titulo = input("titulo: ").strip()
    duracao = input_int("duracao_segundos: ")
    id_al = input_int("id_album: ")
    id_g = input_int("id_genero: ")
    executar(
        "INSERT INTO Musica VALUES (:id, :titulo, :dur, :album, :genero)",
        {"id": id_m, "titulo": titulo, "dur": duracao, "album": id_al, "genero": id_g}
    )

def atualizar_musica():
    print("\n--- Atualizar Música ---")
    listar("Musica", "id_musica")
    id_m = input_int("id_musica a atualizar: ")
    titulo = input("Novo titulo (Enter para manter): ").strip()
    duracao = input("Nova duracao_segundos (Enter para manter): ").strip()
    if titulo:
        executar("UPDATE Musica SET titulo=:v WHERE id_musica=:id", {"v": titulo, "id": id_m})
    if duracao.isdigit():
        executar("UPDATE Musica SET duracao_segundos=:v WHERE id_musica=:id", {"v": int(duracao), "id": id_m})

def excluir_musica():
    print("\n--- Excluir Música ---")
    listar("Musica", "id_musica")
    id_m = input_int("id_musica a excluir: ")
    executar("DELETE FROM Musica WHERE id_musica=:id", {"id": id_m})

def consultar_musica():
    print("\n--- Consultar Músicas ---")
    listar("Musica", "id_musica")

def inserir_humor():
    print("\n--- Inserir Humor ---")
    listar("Usuario", "id_usuario")
    id_h = input_int("id_humor: ")
    id_u = input_int("id_usuario: ")
    data_req = input_datetime("data_requisicao")
    desc = input("descricao: ").strip()
    executar(
        "INSERT INTO Humor VALUES (:id, :usuario, :data, :desc)",
        {"id": id_h, "usuario": id_u, "data": data_req, "desc": desc}
    )

def atualizar_humor():
    print("\n--- Atualizar Humor ---")
    listar("Humor", "id_humor")
    id_h = input_int("id_humor a atualizar: ")
    desc = input("Nova descricao (Enter para manter): ").strip()
    if desc:
        executar("UPDATE Humor SET descricao=:v WHERE id_humor=:id", {"v": desc, "id": id_h})

def excluir_humor():
    print("\n--- Excluir Humor ---")
    listar("Humor", "id_humor")
    id_h = input_int("id_humor a excluir: ")
    executar("DELETE FROM Humor WHERE id_humor=:id", {"id": id_h})

def consultar_humor():
    print("\n--- Consultar Humores ---")
    listar("Humor", "id_humor")

def inserir_playlist():
    print("\n--- Inserir Playlist ---")
    listar("Humor", "id_humor")
    id_pl = input_int("id_playlist: ")
    id_h = input_int("id_humor: ")
    nome = input("nome: ").strip()
    data_cri = input_data("data_criacao")
    ia = input_bool("gerada_por_ia")
    executar(
        "INSERT INTO Playlist VALUES (:id, :humor, :nome, :data, :ia)",
        {"id": id_pl, "humor": id_h, "nome": nome, "data": data_cri, "ia": ia}
    )

def atualizar_playlist():
    print("\n--- Atualizar Playlist ---")
    listar("Playlist", "id_playlist")
    id_pl = input_int("id_playlist a atualizar: ")
    nome = input("Novo nome (Enter para manter): ").strip()
    if nome:
        executar("UPDATE Playlist SET nome=:v WHERE id_playlist=:id", {"v": nome, "id": id_pl})

def excluir_playlist():
    print("\n--- Excluir Playlist ---")
    listar("Playlist", "id_playlist")
    id_pl = input_int("id_playlist a excluir: ")
    executar("DELETE FROM Playlist WHERE id_playlist=:id", {"id": id_pl})

def consultar_playlist():
    print("\n--- Consultar Playlists ---")
    listar("Playlist", "id_playlist")

def inserir_pagamento():
    print("\n--- Inserir Pagamento ---")
    listar("Usuario", "id_usuario")
    id_pg = input_int("id_pagamento: ")
    id_u = input_int("id_usuario: ")
    valor = input_decimal("valor_pago: ")
    data_pg = input_data("data_pagamento")
    status = input("status: ").strip()
    executar(
        "INSERT INTO Pagamento VALUES (:id, :usuario, :valor, :data, :status)",
        {"id": id_pg, "usuario": id_u, "valor": valor, "data": data_pg, "status": status}
    )

def atualizar_pagamento():
    print("\n--- Atualizar Pagamento ---")
    listar("Pagamento", "id_pagamento")
    id_pg = input_int("id_pagamento a atualizar: ")
    status = input("Novo status (Enter para manter): ").strip()
    valor = input("Novo valor_pago (Enter para manter): ").strip()
    if status:
        executar("UPDATE Pagamento SET status=:v WHERE id_pagamento=:id", {"v": status, "id": id_pg})
    if valor:
        executar("UPDATE Pagamento SET valor_pago=:v WHERE id_pagamento=:id", {"v": float(valor), "id": id_pg})

def excluir_pagamento():
    print("\n--- Excluir Pagamento ---")
    listar("Pagamento", "id_pagamento")
    id_pg = input_int("id_pagamento a excluir: ")
    executar("DELETE FROM Pagamento WHERE id_pagamento=:id", {"id": id_pg})

def consultar_pagamento():
    print("\n--- Consultar Pagamentos ---")
    listar("Pagamento", "id_pagamento")

def inserir_reproducao():
    print("\n--- Inserir Histórico de Reprodução ---")
    listar("Musica", "id_musica")
    listar("Usuario", "id_usuario")
    id_r = input_int("id_reproducao: ")
    id_m = input_int("id_musica: ")
    id_u = input_int("id_usuario: ")
    data_hr = input_datetime("data_hora")
    executar(
        "INSERT INTO Hist_Reproducao VALUES (:id, :data, :musica, :usuario)",
        {"id": id_r, "data": data_hr, "musica": id_m, "usuario": id_u}
    )

def atualizar_reproducao():
    print("\n--- Atualizar Histórico de Reprodução ---")
    listar("Hist_Reproducao", "id_reproducao")
    id_r = input_int("id_reproducao a atualizar: ")
    data_hr = input("Nova data_hora (AAAA-MM-DD HH:MM:SS) (Enter para manter): ").strip()
    if len(data_hr) >= 19:
        executar("UPDATE Hist_Reproducao SET data_hora=:v WHERE id_reproducao=:id", {"v": data_hr, "id": id_r})

def excluir_reproducao():
    print("\n--- Excluir Histórico de Reprodução ---")
    listar("Hist_Reproducao", "id_reproducao")
    id_r = input_int("id_reproducao a excluir: ")
    executar("DELETE FROM Hist_Reproducao WHERE id_reproducao=:id", {"id": id_r})

def consultar_reproducao():
    print("\n--- Consultar Histórico de Reprodução ---")
    listar("Hist_Reproducao", "id_reproducao")

def inserir_contem():
    print("\n--- Inserir Música em Playlist ---")
    listar("Musica", "id_musica")
    listar("Playlist", "id_playlist")
    id_m = input_int("id_musica: ")
    id_pl = input_int("id_playlist: ")
    executar(
        "INSERT INTO contem VALUES (:musica, :playlist)",
        {"musica": id_m, "playlist": id_pl}
    )

def excluir_contem():
    print("\n--- Remover Música de Playlist ---")
    listar("contem")
    id_m = input_int("id_musica: ")
    id_pl = input_int("id_playlist: ")
    executar(
        "DELETE FROM contem WHERE id_musica=:m AND id_playlist=:pl",
        {"m": id_m, "pl": id_pl}
    )

def consultar_contem():
    print("\n--- Músicas em Playlists ---")
    listar("contem")

def inserir_colabora():
    print("\n--- Inserir Colaborador em Playlist ---")
    listar("Playlist", "id_playlist")
    listar("Usuario", "id_usuario")
    id_pl = input_int("id_playlist: ")
    id_u = input_int("id_usuario: ")
    executar(
        "INSERT INTO colabora VALUES (:playlist, :usuario)",
        {"playlist": id_pl, "usuario": id_u}
    )

def excluir_colabora():
    print("\n--- Remover Colaborador de Playlist ---")
    listar("colabora")
    id_pl = input_int("id_playlist: ")
    id_u = input_int("id_usuario: ")
    executar(
        "DELETE FROM colabora WHERE id_playlist=:pl AND id_usuario=:u",
        {"pl": id_pl, "u": id_u}
    )

def consultar_colabora():
    print("\n--- Colaboradores em Playlists ---")
    listar("colabora")

def inserir_visualiza():
    print("\n--- Inserir Visualização de Anúncio ---")
    listar("Anuncio", "id_anuncio")
    listar("Usuario", "id_usuario")
    id_an = input_int("id_anuncio: ")
    id_u = input_int("id_usuario: ")
    data_v = input_data("data_visualizacao")
    executar(
        "INSERT INTO visualiza VALUES (:anuncio, :usuario, :data)",
        {"anuncio": id_an, "usuario": id_u, "data": data_v}
    )

def excluir_visualiza():
    print("\n--- Excluir Visualização de Anúncio ---")
    listar("visualiza")
    id_an = input_int("id_anuncio: ")
    id_u = input_int("id_usuario: ")
    data_v = input_data("data_visualizacao")
    executar(
        "DELETE FROM visualiza WHERE id_anuncio=:a AND id_usuario=:u AND data_vizualizacao=:d",
        {"a": id_an, "u": id_u, "d": data_v}
    )

def consultar_visualiza():
    print("\n--- Visualizações de Anúncios ---")
    listar("visualiza")

# CONSULTA 1 — Reproduções por Gênero

def consulta_genero():
    query = """
    SELECT
        g.nome AS genero,
        COUNT(hr.id_reproducao) AS total_reproducoes
    FROM Genero g
    JOIN Musica m
        ON g.id_genero = m.id_genero
    JOIN Hist_Reproducao hr
        ON m.id_musica = hr.id_musica
    GROUP BY g.nome
    ORDER BY total_reproducoes DESC
    """
    df = pd.read_sql(query, engine)
    print("\nResultado — Reproduções por Gênero:")
    print(df.to_string(index=False))

    plt.figure(figsize=(8, 5))
    plt.bar(df["genero"], df["total_reproducoes"], color="steelblue")
    plt.title("Reproduções por Gênero")
    plt.xlabel("Gênero")
    plt.ylabel("Total de Reproduções")
    plt.tight_layout()
    plt.show()

# CONSULTA 2 — Músicas por Artista

def consulta_artista():
    query = """
    SELECT
        a.nome_artistico,
        COUNT(m.id_musica) AS qtd_musicas
    FROM Artista a
    JOIN Album al
        ON a.id_artista = al.id_artista
    JOIN Musica m
        ON al.id_album = m.id_album
    GROUP BY a.nome_artistico
    ORDER BY qtd_musicas DESC
    """
    df = pd.read_sql(query, engine)
    print("\nResultado — Músicas por Artista:")
    print(df.to_string(index=False))

    plt.figure(figsize=(8, 5))
    plt.bar(df["nome_artistico"], df["qtd_musicas"], color="coral")
    plt.title("Músicas por Artista")
    plt.xlabel("Artista")
    plt.ylabel("Quantidade de Músicas")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

# CONSULTA 3 — Reproduções por Usuário

def consulta_usuario():
    query = """
    SELECT
        u.nome,
        COUNT(hr.id_reproducao) AS total_reproducoes
    FROM Usuario u
    JOIN Hist_Reproducao hr
        ON u.id_usuario = hr.id_usuario
    JOIN Musica m
        ON hr.id_musica = m.id_musica
    GROUP BY u.nome
    ORDER BY total_reproducoes DESC
    """
    df = pd.read_sql(query, engine)
    print("\nResultado — Reproduções por Usuário:")
    print(df.to_string(index=False))

    plt.figure(figsize=(8, 5))
    plt.barh(df["nome"], df["total_reproducoes"], color="mediumseagreen")
    plt.title("Reproduções por Usuário")
    plt.xlabel("Total de Reproduções")
    plt.ylabel("Usuário")
    plt.tight_layout()
    plt.show()

# MENUS

def menu_anuncio():
    while True:
        print("""
--- ANÚNCIO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_anuncio()
        elif op == "2": consultar_anuncio()
        elif op == "3": atualizar_anuncio()
        elif op == "4": excluir_anuncio()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_plano():
    while True:
        print("""
--- PLANO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_plano()
        elif op == "2": consultar_plano()
        elif op == "3": atualizar_plano()
        elif op == "4": excluir_plano()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_usuario():
    while True:
        print("""
--- USUÁRIO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_usuario()
        elif op == "2": consultar_usuario_tabela()
        elif op == "3": atualizar_usuario()
        elif op == "4": excluir_usuario()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_artista():
    while True:
        print("""
--- ARTISTA ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_artista()
        elif op == "2": consultar_artista_tabela()
        elif op == "3": atualizar_artista()
        elif op == "4": excluir_artista()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_album():
    while True:
        print("""
--- ÁLBUM ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_album()
        elif op == "2": consultar_album()
        elif op == "3": atualizar_album()
        elif op == "4": excluir_album()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_genero():
    while True:
        print("""
--- GÊNERO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_genero()
        elif op == "2": consultar_genero_tabela()
        elif op == "3": atualizar_genero()
        elif op == "4": excluir_genero()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_musica():
    while True:
        print("""
--- MÚSICA ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_musica()
        elif op == "2": consultar_musica()
        elif op == "3": atualizar_musica()
        elif op == "4": excluir_musica()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_humor():
    while True:
        print("""
--- HUMOR ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_humor()
        elif op == "2": consultar_humor()
        elif op == "3": atualizar_humor()
        elif op == "4": excluir_humor()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_playlist():
    while True:
        print("""
--- PLAYLIST ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_playlist()
        elif op == "2": consultar_playlist()
        elif op == "3": atualizar_playlist()
        elif op == "4": excluir_playlist()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_pagamento():
    while True:
        print("""
--- PAGAMENTO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_pagamento()
        elif op == "2": consultar_pagamento()
        elif op == "3": atualizar_pagamento()
        elif op == "4": excluir_pagamento()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_reproducao():
    while True:
        print("""
--- HISTÓRICO DE REPRODUÇÃO ---
1 - Inserir
2 - Consultar
3 - Atualizar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_reproducao()
        elif op == "2": consultar_reproducao()
        elif op == "3": atualizar_reproducao()
        elif op == "4": excluir_reproducao()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_contem():
    while True:
        print("""
--- MÚSICAS EM PLAYLIST (contem) ---
1 - Inserir
2 - Consultar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_contem()
        elif op == "2": consultar_contem()
        elif op == "4": excluir_contem()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_colabora():
    while True:
        print("""
--- COLABORADORES DE PLAYLIST (colabora) ---
1 - Inserir
2 - Consultar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_colabora()
        elif op == "2": consultar_colabora()
        elif op == "4": excluir_colabora()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_visualiza():
    while True:
        print("""
--- VISUALIZAÇÕES DE ANÚNCIO (visualiza) ---
1 - Inserir
2 - Consultar
4 - Excluir
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": inserir_visualiza()
        elif op == "2": consultar_visualiza()
        elif op == "4": excluir_visualiza()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

def menu_consultas():
    while True:
        print("""
1 - Reproduções por Gênero
2 - Músicas por Artista
3 - Reproduções por Usuário
0 - Voltar""")
        op = input("Escolha: ")
        if op == "1": consulta_genero()
        elif op == "2": consulta_artista()
        elif op == "3": consulta_usuario()
        elif op == "0": break
        else: print("Opção inválida.")
        pressione_enter()

# MENU PRINCIPAL

while True:
    print("""
====================================
         VELVTUNE
====================================
TABELAS
  1  - Anúncio
  2  - Plano
  3  - Usuário
  4  - Artista
  5  - Álbum
  6  - Gênero
  7  - Música
  8  - Humor
  9  - Playlist
  10 - Pagamento
  11 - Histórico de Reprodução
  12 - Músicas em Playlist
  13 - Colaboradores de Playlist
  14 - Visualizações de Anúncio
  15 - Consultas com Gráficos
  16 - Apagar Banco
  17 - Recriar Banco
  18 - Integração com LLM

  0  - Sair
""")
    op = input("Escolha: ").strip()

    if op == "1":   menu_anuncio()
    elif op == "2": menu_plano()
    elif op == "3": menu_usuario()
    elif op == "4": menu_artista()
    elif op == "5": menu_album()
    elif op == "6": menu_genero()
    elif op == "7": menu_musica()
    elif op == "8": menu_humor()
    elif op == "9": menu_playlist()
    elif op == "10": menu_pagamento()
    elif op == "11": menu_reproducao()
    elif op == "12": menu_contem()
    elif op == "13": menu_colabora()
    elif op == "14": menu_visualiza()
    elif op == "15": menu_consultas()
    elif op == "16": apagar_banco()
    elif op == "17": recriar_banco()
    elif op == "18": llm_ia()
    elif op == "0":
        print("Encerrando...")
        break
    else:
        print("Opção inválida.")
