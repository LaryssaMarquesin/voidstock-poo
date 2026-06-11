"""Persistência em PostgreSQL.

Implementa o que a docstring do `repositorio.py` antecipava: trocar o
armazenamento em memória por um banco de dados real, sem afetar o modelo
orientado a objetos. Aqui usamos a estratégia de *snapshot* do agregado
`Inventario`: o modelo OO continua sendo a fonte da verdade em tempo de
execução e esta camada apenas o grava/recarrega no Postgres, de forma que
os dados sobrevivam a reinícios (resolve o problema do estado em memória).

Se a variável de ambiente `DATABASE_URL` não estiver definida, a classe
fica em modo "indisponível" e o sistema volta a funcionar 100% em memória —
ou seja, o banco é opcional e o app nunca quebra por falta dele.
"""
from __future__ import annotations

import os

try:  # psycopg é opcional: sem ele, caímos no modo em memória.
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None  # type: ignore

from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.dominio.movimentacao import Entrada, Movimentacao, Saida
from src.dominio.tipos import Papel, TipoMovimentacao
from src.dominio.usuario import criar_usuario
from src.servicos.inventario import Inventario

_SCHEMA = """
CREATE TABLE IF NOT EXISTS categorias (
    id        TEXT PRIMARY KEY,
    nome      TEXT NOT NULL,
    descricao TEXT
);
CREATE TABLE IF NOT EXISTS locais (
    id        TEXT PRIMARY KEY,
    nome      TEXT NOT NULL,
    descricao TEXT
);
CREATE TABLE IF NOT EXISTS usuarios (
    id         TEXT PRIMARY KEY,
    nome       TEXT NOT NULL,
    email      TEXT NOT NULL,
    papel      TEXT NOT NULL,
    salt       TEXT NOT NULL DEFAULT '',
    senha_hash TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS itens (
    id              TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    descricao       TEXT,
    estoque_minimo  INTEGER NOT NULL DEFAULT 0,
    quantidade      INTEGER NOT NULL DEFAULT 0,
    imagem_url      TEXT,
    categoria_id    TEXT REFERENCES categorias(id) ON DELETE SET NULL,
    local_id        TEXT REFERENCES locais(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS movimentacoes (
    id          TEXT PRIMARY KEY,
    tipo        TEXT NOT NULL,
    quantidade  INTEGER NOT NULL,
    motivo      TEXT,
    criado_em   TIMESTAMP NOT NULL,
    item_id     TEXT,
    item_nome   TEXT NOT NULL,
    usuario_id  TEXT
);
"""


class PersistenciaPostgres:
    """Grava e recarrega o `Inventario` inteiro em um banco PostgreSQL."""

    def __init__(self, dsn: str | None = None) -> None:
        dsn = dsn or os.environ.get("DATABASE_URL", "")
        # Render entrega a URL como `postgres://...`; psycopg quer `postgresql://`.
        if dsn.startswith("postgres://"):
            dsn = "postgresql://" + dsn[len("postgres://"):]
        self._dsn = dsn

    @property
    def disponivel(self) -> bool:
        """True só quando há driver instalado e DATABASE_URL configurada."""
        return bool(psycopg and self._dsn)

    def _conectar(self):
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def criar_schema(self) -> None:
        with self._conectar() as conn:
            conn.execute(_SCHEMA)
            conn.commit()

    # ---- Gravação (snapshot completo, em uma transação) ----
    def salvar(self, inv: Inventario) -> None:
        if not self.disponivel:
            return
        with self._conectar() as conn:
            with conn.cursor() as cur:
                # Limpa e regrava — o volume é pequeno e garante consistência.
                cur.execute(
                    "TRUNCATE movimentacoes, itens, usuarios, locais, categorias"
                )
                for c in inv.categorias():
                    cur.execute(
                        "INSERT INTO categorias (id, nome, descricao) VALUES (%s, %s, %s)",
                        (c.id, c.nome, c.descricao),
                    )
                for l in inv.locais():
                    cur.execute(
                        "INSERT INTO locais (id, nome, descricao) VALUES (%s, %s, %s)",
                        (l.id, l.nome, l.descricao),
                    )
                for u in inv.usuarios():
                    cur.execute(
                        "INSERT INTO usuarios (id, nome, email, papel, salt, senha_hash) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (u.id, u.nome, u.email, u.papel.value,
                         u.exportar_salt(), u.exportar_hash()),
                    )
                for i in inv.itens():
                    cur.execute(
                        "INSERT INTO itens (id, nome, descricao, estoque_minimo, "
                        "quantidade, imagem_url, categoria_id, local_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (i.id, i.nome, i.descricao, i.estoque_minimo,
                         i.quantidade_atual, i.imagem_url,
                         i.categoria.id if i.categoria else None,
                         i.local.id if i.local else None),
                    )
                for m in inv.movimentacoes():
                    cur.execute(
                        "INSERT INTO movimentacoes (id, tipo, quantidade, motivo, "
                        "criado_em, item_id, item_nome, usuario_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (m.id, m.tipo.value, m.quantidade, m.motivo,
                         m.criado_em, m.item.id, m.item.nome,
                         m.usuario.id if m.usuario else None),
                    )
            conn.commit()

    # ---- Leitura (reconstrói o agregado a partir das tabelas) ----
    def carregar(self) -> Inventario | None:
        """Reconstrói o `Inventario`. Retorna None se o banco estiver vazio."""
        if not self.disponivel:
            return None
        with self._conectar() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) AS n FROM usuarios")
            if cur.fetchone()["n"] == 0:
                return None  # banco ainda não populado -> caller faz o seed

            inv = Inventario()

            cur.execute("SELECT * FROM categorias")
            categorias = {}
            for row in cur.fetchall():
                c = Categoria(row["nome"], row["descricao"])
                c.restaurar_id(row["id"])
                inv.adicionar_categoria(c)
                categorias[c.id] = c

            cur.execute("SELECT * FROM locais")
            locais = {}
            for row in cur.fetchall():
                l = Local(row["nome"], row["descricao"])
                l.restaurar_id(row["id"])
                inv.adicionar_local(l)
                locais[l.id] = l

            cur.execute("SELECT * FROM usuarios")
            usuarios = {}
            for row in cur.fetchall():
                papel = Papel.ADMIN if row["papel"] == Papel.ADMIN.value else Papel.USUARIO
                u = criar_usuario(row["nome"], row["email"], papel)
                u.restaurar_id(row["id"])
                u.restaurar_credenciais(row["salt"], row["senha_hash"])
                inv.adicionar_usuario(u)
                usuarios[u.id] = u

            cur.execute("SELECT * FROM itens")
            itens = {}
            for row in cur.fetchall():
                item = Item(
                    row["nome"], estoque_minimo=row["estoque_minimo"],
                    categoria=categorias.get(row["categoria_id"]),
                    local=locais.get(row["local_id"]),
                    descricao=row["descricao"], imagem_url=row["imagem_url"],
                )
                item.restaurar_id(row["id"])
                # Reidrata a quantidade respeitando o encapsulamento do Item.
                if row["quantidade"] > 0:
                    item.registrar_entrada(row["quantidade"])
                inv.carregar_item(item)
                itens[item.id] = item

            cur.execute("SELECT * FROM movimentacoes ORDER BY criado_em")
            for row in cur.fetchall():
                item = itens.get(row["item_id"])
                if item is None:  # item já removido; recria um stub para o histórico
                    item = Item(row["item_nome"])
                usuario = usuarios.get(row["usuario_id"])
                Mov = Entrada if row["tipo"] == TipoMovimentacao.ENTRADA.value else Saida
                mov: Movimentacao = Mov(
                    item, row["quantidade"], usuario, row["motivo"], row["criado_em"],
                )
                mov.restaurar_id(row["id"])
                inv.adicionar_movimentacao_historica(mov)  # histórico, sem reaplicar

            return inv
