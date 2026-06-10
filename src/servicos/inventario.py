"""Serviço de Inventário — o agregado central do sistema.

Demonstra: COMPOSIÇÃO (o Inventário é composto por repositórios) e
encapsulamento das regras de negócio. Reúne a lógica que, no projeto
original, estava espalhada entre server functions e triggers SQL:
controle de permissão, aplicação de movimentações, itens críticos,
relatório e a sugestão automática de local.
"""
from collections import Counter

from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.dominio.movimentacao import Entrada, Movimentacao, Saida
from src.dominio.usuario import Usuario
from src.repositorio.repositorio import RepositorioEmMemoria


class Inventario:
    def __init__(self) -> None:
        self._itens: RepositorioEmMemoria[Item] = RepositorioEmMemoria()
        self._categorias: RepositorioEmMemoria[Categoria] = RepositorioEmMemoria()
        self._locais: RepositorioEmMemoria[Local] = RepositorioEmMemoria()
        self._usuarios: RepositorioEmMemoria[Usuario] = RepositorioEmMemoria()
        self._movimentacoes: list[Movimentacao] = []

    # ---- Catálogo ----
    def adicionar_categoria(self, categoria: Categoria) -> Categoria:
        return self._categorias.adicionar(categoria)

    def adicionar_local(self, local: Local) -> Local:
        return self._locais.adicionar(local)

    def adicionar_usuario(self, usuario: Usuario) -> Usuario:
        return self._usuarios.adicionar(usuario)

    def categorias(self) -> list[Categoria]:
        return self._categorias.listar()

    def locais(self) -> list[Local]:
        return self._locais.listar()

    def usuarios(self) -> list[Usuario]:
        return self._usuarios.listar()

    def itens(self) -> list[Item]:
        return sorted(self._itens.listar(), key=lambda i: i.nome.lower())

    def movimentacoes(self) -> list[Movimentacao]:
        return sorted(self._movimentacoes, key=lambda m: m.criado_em, reverse=True)

    # ---- Itens (exige permissão de gestão) ----
    def cadastrar_item(
        self, item: Item, solicitante: Usuario, quantidade_inicial: int = 0
    ) -> Item:
        """Cadastra um item. Só quem `pode_gerenciar()` tem permissão.

        Usa polimorfismo: chama `solicitante.pode_gerenciar()` sem saber se é
        Administrador ou UsuarioComum.
        """
        self._exigir_gestor(solicitante)
        self._itens.adicionar(item)
        if quantidade_inicial > 0:
            self.registrar_entrada(item, quantidade_inicial, solicitante, "Cadastro inicial")
        return item

    def remover_item(self, item: Item, solicitante: Usuario) -> bool:
        self._exigir_gestor(solicitante)
        return self._itens.remover(item.id)

    # ---- Movimentações (qualquer usuário autenticado) ----
    def registrar_entrada(
        self, item: Item, quantidade: int, usuario: Usuario, motivo: str | None = None
    ) -> Entrada:
        mov = Entrada(item, quantidade, usuario, motivo)
        self._aplicar(mov)
        return mov

    def registrar_saida(
        self, item: Item, quantidade: int, usuario: Usuario, motivo: str | None = None
    ) -> Saida:
        mov = Saida(item, quantidade, usuario, motivo)
        self._aplicar(mov)
        return mov

    def _aplicar(self, mov: Movimentacao) -> None:
        mov.aplicar()  # polimorfismo: Entrada e Saida se comportam diferente
        self._movimentacoes.append(mov)

    # ---- Consultas / relatórios ----
    def itens_criticos(self) -> list[Item]:
        return [i for i in self.itens() if i.esta_critico()]

    def relatorio(self) -> dict:
        itens = self.itens()
        return {
            "total_itens": len(itens),
            "total_unidades": sum(i.quantidade_atual for i in itens),
            "itens_criticos": len(self.itens_criticos()),
            "total_movimentacoes": len(self._movimentacoes),
            "total_locais": len(self._locais),
            "total_categorias": len(self._categorias),
        }

    def sugerir_local(self, categoria: Categoria | None) -> tuple[Local | None, str]:
        """Sugere onde guardar um item novo.

        Regra (igual à do projeto original):
        1. Se há itens da mesma categoria, sugere o local mais usado por eles.
        2. Senão, sugere o local com menos itens (mais livre).
        """
        locais = self.locais()
        if not locais:
            return None, "Nenhum local cadastrado"

        itens = self.itens()

        if categoria is not None:
            mesmos = [
                i for i in itens
                if i.categoria is not None and i.categoria.id == categoria.id and i.local
            ]
            if mesmos:
                contagem = Counter(i.local.id for i in mesmos)
                melhor_id, _ = contagem.most_common(1)[0]
                local = next((l for l in locais if l.id == melhor_id), None)
                if local:
                    return local, f"Outros itens de '{categoria.nome}' estão em {local.nome}"

        # Local mais livre
        ocupacao = Counter()
        for l in locais:
            ocupacao[l.id] = 0
        for i in itens:
            if i.local:
                ocupacao[i.local.id] += 1
        mais_livre_id = min(ocupacao, key=ocupacao.get)
        local = next((l for l in locais if l.id == mais_livre_id), None)
        return local, f"{local.nome} é o local mais livre" if local else "—"

    # ---- Apoio ----
    @staticmethod
    def _exigir_gestor(usuario: Usuario) -> None:
        if not usuario.pode_gerenciar():
            raise PermissionError("Acesso restrito a coordenadores (administradores)")
