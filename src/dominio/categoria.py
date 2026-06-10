"""Categoria de um item (ex.: Sensores, Ferramentas)."""
from src.dominio.entidade import Entidade


class Categoria(Entidade):
    def __init__(self, nome: str, descricao: str | None = None) -> None:
        super().__init__()
        self._nome = nome.strip()
        self._descricao = descricao

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def descricao(self) -> str | None:
        return self._descricao

    def __str__(self) -> str:
        return self._nome
