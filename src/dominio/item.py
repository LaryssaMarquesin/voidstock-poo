"""Item de estoque.

Demonstra: ENCAPSULAMENTO. A `quantidade_atual` é privada e NÃO pode ser
alterada livremente de fora — só através de `registrar_entrada` /
`registrar_saida`, que mantêm a regra de negócio (estoque nunca negativo).
Isso espelha o trigger `aplicar_movimentacao` do banco original.
"""
from src.dominio.categoria import Categoria
from src.dominio.entidade import Entidade
from src.dominio.local import Local


class Item(Entidade):
    def __init__(
        self,
        nome: str,
        estoque_minimo: int = 0,
        categoria: Categoria | None = None,
        local: Local | None = None,
        descricao: str | None = None,
    ) -> None:
        super().__init__()
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
        self._nome = nome.strip()
        self._descricao = descricao
        self._categoria = categoria
        self._local = local
        self._quantidade_atual = 0  # estado controlado: começa zerado
        self._estoque_minimo = estoque_minimo

    # ---- Leitura (propriedades) ----
    @property
    def nome(self) -> str:
        return self._nome

    @property
    def descricao(self) -> str | None:
        return self._descricao

    @property
    def categoria(self) -> Categoria | None:
        return self._categoria

    @property
    def local(self) -> Local | None:
        return self._local

    @property
    def quantidade_atual(self) -> int:
        return self._quantidade_atual

    @property
    def estoque_minimo(self) -> int:
        return self._estoque_minimo

    # ---- Comportamento (regras de negócio) ----
    def registrar_entrada(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade de entrada deve ser positiva")
        self._quantidade_atual += quantidade

    def registrar_saida(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade de saída deve ser positiva")
        if quantidade > self._quantidade_atual:
            raise ValueError(
                f"Estoque insuficiente de '{self._nome}': "
                f"disponível {self._quantidade_atual}, solicitado {quantidade}"
            )
        self._quantidade_atual -= quantidade

    def esta_critico(self) -> bool:
        """Verdadeiro quando o estoque atingiu o mínimo (precisa repor)."""
        return self._quantidade_atual <= self._estoque_minimo

    def definir_local(self, local: Local | None) -> None:
        self._local = local

    def __str__(self) -> str:
        cat = self._categoria.nome if self._categoria else "sem categoria"
        return f"{self._nome} [{cat}] — {self._quantidade_atual} un."
