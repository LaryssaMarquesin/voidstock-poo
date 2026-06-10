"""Repositório genérico.

Demonstra: ABSTRAÇÃO + INTERFACE + GENERICS. `Repositorio[T]` define um
contrato genérico de persistência que funciona para qualquer entidade.
`RepositorioEmMemoria` é uma implementação concreta. Trocar por um
repositório de banco de dados no futuro não afeta o resto do sistema
(princípio da inversão de dependência).
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.dominio.entidade import Entidade

T = TypeVar("T", bound=Entidade)


class Repositorio(ABC, Generic[T]):
    @abstractmethod
    def adicionar(self, entidade: T) -> T: ...

    @abstractmethod
    def buscar(self, id: str) -> T | None: ...

    @abstractmethod
    def listar(self) -> list[T]: ...

    @abstractmethod
    def remover(self, id: str) -> bool: ...


class RepositorioEmMemoria(Repositorio[T]):
    """Implementação que guarda as entidades em um dicionário na memória."""

    def __init__(self) -> None:
        self._dados: dict[str, T] = {}

    def adicionar(self, entidade: T) -> T:
        self._dados[entidade.id] = entidade
        return entidade

    def buscar(self, id: str) -> T | None:
        return self._dados.get(id)

    def listar(self) -> list[T]:
        return list(self._dados.values())

    def remover(self, id: str) -> bool:
        return self._dados.pop(id, None) is not None

    def __len__(self) -> int:
        return len(self._dados)
