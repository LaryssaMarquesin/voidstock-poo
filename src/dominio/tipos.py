"""Enumerações do domínio.

Demonstra: uso de Enum para representar conjuntos fechados de valores,
substituindo "strings mágicas" por tipos seguros.
"""
from enum import Enum


class TipoMovimentacao(Enum):
    """Tipo de uma movimentação de estoque."""

    ENTRADA = "entrada"
    SAIDA = "saida"


class Papel(Enum):
    """Papel (permissão) de um usuário no sistema."""

    ADMIN = "admin"
    USUARIO = "user"
