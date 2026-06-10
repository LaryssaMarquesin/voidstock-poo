"""Local físico de armazenamento (ex.: Gaveta B3, Armário 2)."""
from src.dominio.entidade import Entidade


class Local(Entidade):
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
