"""Hierarquia de usuários.

Demonstra: HERANÇA, ABSTRAÇÃO (classe abstrata) e POLIMORFISMO.
`Usuario` é abstrata e define o contrato; `Administrador` e `UsuarioComum`
implementam o mesmo método `pode_gerenciar()` de formas diferentes — quem
chama não precisa saber qual subclasse está usando.
"""
from abc import ABC, abstractmethod

from src.dominio.entidade import Entidade
from src.dominio.tipos import Papel


class Usuario(Entidade, ABC):
    """Usuário abstrato do sistema."""

    def __init__(self, nome: str, email: str) -> None:
        super().__init__()
        self._nome = nome.strip()
        self._email = email.strip().lower()

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    @property
    @abstractmethod
    def papel(self) -> Papel:
        """Papel do usuário — definido por cada subclasse."""

    @abstractmethod
    def pode_gerenciar(self) -> bool:
        """Indica se o usuário pode cadastrar/editar/remover itens."""

    def __str__(self) -> str:
        return f"{self._nome} ({self.papel.value})"


class Administrador(Usuario):
    """Coordenador: tem permissão total de gestão."""

    @property
    def papel(self) -> Papel:
        return Papel.ADMIN

    def pode_gerenciar(self) -> bool:
        return True


class UsuarioComum(Usuario):
    """Usuário comum: registra movimentações, mas não gerencia o catálogo."""

    @property
    def papel(self) -> Papel:
        return Papel.USUARIO

    def pode_gerenciar(self) -> bool:
        return False


def criar_usuario(nome: str, email: str, papel: Papel) -> Usuario:
    """Fábrica polimórfica: o papel determina a subclasse instanciada."""
    if papel == Papel.ADMIN:
        return Administrador(nome, email)
    return UsuarioComum(nome, email)
