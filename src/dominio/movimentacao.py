"""Movimentações de estoque.

Demonstra: ABSTRAÇÃO + POLIMORFISMO. `Movimentacao` é abstrata e define o
método `aplicar()`. `Entrada` e `Saida` implementam `aplicar()` de formas
diferentes. O Inventário chama `mov.aplicar()` sem saber qual é o tipo —
isso é polimorfismo em ação (substitui o `IF tipo = 'entrada'` do SQL).
"""
from abc import ABC, abstractmethod
from datetime import datetime

from src.dominio.entidade import Entidade
from src.dominio.item import Item
from src.dominio.tipos import TipoMovimentacao
from src.dominio.usuario import Usuario


class Movimentacao(Entidade, ABC):
    def __init__(
        self,
        item: Item,
        quantidade: int,
        usuario: Usuario,
        motivo: str | None = None,
        data: datetime | None = None,
    ) -> None:
        super().__init__()
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        self._item = item
        self._quantidade = quantidade
        self._usuario = usuario
        self._motivo = motivo
        # `data` permite registrar movimentações históricas (usado no seed).
        self._criado_em = data if data is not None else datetime.now()

    @property
    def item(self) -> Item:
        return self._item

    @property
    def quantidade(self) -> int:
        return self._quantidade

    @property
    def usuario(self) -> Usuario:
        return self._usuario

    @property
    def motivo(self) -> str | None:
        return self._motivo

    @property
    def criado_em(self) -> datetime:
        return self._criado_em

    @property
    @abstractmethod
    def tipo(self) -> TipoMovimentacao:
        """Tipo da movimentação."""

    @abstractmethod
    def aplicar(self) -> None:
        """Aplica o efeito desta movimentação sobre o item."""

    def __str__(self) -> str:
        quando = self._criado_em.strftime("%d/%m/%Y %H:%M")
        return f"[{quando}] {self.tipo.value.upper()} {self._quantidade}x {self._item.nome}"


class Entrada(Movimentacao):
    @property
    def tipo(self) -> TipoMovimentacao:
        return TipoMovimentacao.ENTRADA

    def aplicar(self) -> None:
        self._item.registrar_entrada(self._quantidade)


class Saida(Movimentacao):
    @property
    def tipo(self) -> TipoMovimentacao:
        return TipoMovimentacao.SAIDA

    def aplicar(self) -> None:
        self._item.registrar_saida(self._quantidade)
