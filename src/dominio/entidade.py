"""Classe base de todas as entidades.

Demonstra: ABSTRAÇÃO e HERANÇA. Toda entidade do domínio possui uma
identidade única (id). Centralizar isso evita repetição e permite que o
Repositório genérico trabalhe com qualquer entidade de forma uniforme.
"""
import uuid


class Entidade:
    """Entidade base: fornece um identificador único e igualdade por id."""

    def __init__(self) -> None:
        # ENCAPSULAMENTO: o id é privado e só pode ser lido, nunca alterado.
        self._id: str = str(uuid.uuid4())

    @property
    def id(self) -> str:
        return self._id

    def restaurar_id(self, id: str) -> None:
        """Preserva a identidade ao reconstruir a entidade (ex.: troca de papel
        de um usuário, que troca a subclasse mas mantém o mesmo id)."""
        self._id = id

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, Entidade) and outro._id == self._id

    def __hash__(self) -> int:
        return hash(self._id)
