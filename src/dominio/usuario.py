"""Hierarquia de usuários.

Demonstra: HERANÇA, ABSTRAÇÃO (classe abstrata) e POLIMORFISMO.
`Usuario` é abstrata e define o contrato; `Administrador` e `UsuarioComum`
implementam o mesmo método `pode_gerenciar()` de formas diferentes — quem
chama não precisa saber qual subclasse está usando.
"""
import hashlib
import secrets
from abc import ABC, abstractmethod

from src.dominio.entidade import Entidade
from src.dominio.tipos import Papel


class Usuario(Entidade, ABC):
    """Usuário abstrato do sistema."""

    def __init__(self, nome: str, email: str, senha: str | None = None) -> None:
        super().__init__()
        self._nome = nome.strip()
        self._email = email.strip().lower()
        self._salt = ""
        self._senha_hash = ""
        if senha:
            self.definir_senha(senha)

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    # ---- Senha (encapsulada: nunca guardamos texto puro) ----
    @staticmethod
    def _hash(senha: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 100_000).hex()

    def definir_senha(self, senha: str) -> None:
        if not senha or len(senha) < 4:
            raise ValueError("Senha deve ter ao menos 4 caracteres")
        self._salt = secrets.token_hex(16)
        self._senha_hash = self._hash(senha, self._salt)

    def verificar_senha(self, senha: str) -> bool:
        if not self._senha_hash:
            return False
        return secrets.compare_digest(self._senha_hash, self._hash(senha or "", self._salt))

    def copiar_senha(self, outro: "Usuario") -> None:
        """Preserva as credenciais ao recriar o usuário (ex.: troca de papel)."""
        self._salt = outro._salt
        self._senha_hash = outro._senha_hash

    def atualizar_dados(self, nome: str, email: str) -> None:
        if not nome.strip():
            raise ValueError("Nome é obrigatório")
        if "@" not in email:
            raise ValueError("E-mail inválido")
        self._nome = nome.strip()
        self._email = email.strip().lower()

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


def criar_usuario(nome: str, email: str, papel: Papel, senha: str | None = None) -> Usuario:
    """Fábrica polimórfica: o papel determina a subclasse instanciada."""
    if papel == Papel.ADMIN:
        return Administrador(nome, email, senha)
    return UsuarioComum(nome, email, senha)
