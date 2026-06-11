"""Serviço de Inventário — o agregado central do sistema.

Demonstra: COMPOSIÇÃO (o Inventário é composto por repositórios) e
encapsulamento das regras de negócio. Reúne a lógica que, no projeto
original, estava espalhada entre server functions e triggers SQL:
controle de permissão, aplicação de movimentações, itens críticos,
relatório e a sugestão automática de local.
"""
import csv
import io
from collections import Counter
from datetime import datetime, timedelta

from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.dominio.movimentacao import Entrada, Movimentacao, Saida
from src.dominio.tipos import Papel
from src.dominio.usuario import Usuario, criar_usuario
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

    def buscar_usuario(self, user_id: str) -> Usuario | None:
        return self._usuarios.buscar(user_id)

    def criar_usuario(self, nome: str, email: str, papel: Papel, solicitante: Usuario) -> Usuario:
        """Cria um usuário (admin ou comum). Só coordenadores podem."""
        self._exigir_gestor(solicitante)
        if not nome.strip():
            raise ValueError("Nome é obrigatório")
        email = email.strip().lower()
        if "@" not in email:
            raise ValueError("E-mail inválido")
        if any(u.email == email for u in self._usuarios.listar()):
            raise ValueError("Já existe um usuário com este e-mail")
        return self._usuarios.adicionar(criar_usuario(nome, email, papel))

    def alterar_papel(self, usuario: Usuario, papel: Papel, solicitante: Usuario) -> Usuario:
        """Troca o papel de um usuário. Como o papel é a subclasse, recria a
        instância correta preservando a identidade (id)."""
        self._exigir_gestor(solicitante)
        if usuario.papel == papel:
            return usuario
        if usuario.papel == Papel.ADMIN and self._contar_admins() <= 1:
            raise ValueError("Não é possível rebaixar o último coordenador")
        novo = criar_usuario(usuario.nome, usuario.email, papel)
        novo.restaurar_id(usuario.id)
        return self._usuarios.adicionar(novo)  # mesma chave id -> substitui

    def remover_usuario(self, usuario: Usuario, solicitante: Usuario) -> bool:
        self._exigir_gestor(solicitante)
        if usuario.id == solicitante.id:
            raise ValueError("Você não pode remover o próprio usuário")
        if usuario.papel == Papel.ADMIN and self._contar_admins() <= 1:
            raise ValueError("Não é possível remover o último coordenador")
        return self._usuarios.remover(usuario.id)

    def _contar_admins(self) -> int:
        return sum(1 for u in self._usuarios.listar() if u.papel == Papel.ADMIN)

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

    def atualizar_item(
        self, item: Item, solicitante: Usuario, nome: str, estoque_minimo: int,
        categoria: Categoria | None, local: Local | None, descricao: str | None,
        imagem_url: str | None = None,
    ) -> Item:
        """Edita um item existente. Só quem `pode_gerenciar()` tem permissão."""
        self._exigir_gestor(solicitante)
        item.atualizar(nome, estoque_minimo, categoria, local, descricao)
        if imagem_url is not None:
            item.definir_imagem(imagem_url or None)
        return item

    def buscar_item(self, item_id: str) -> Item | None:
        return self._itens.buscar(item_id)

    def remover_item(self, item: Item, solicitante: Usuario) -> bool:
        self._exigir_gestor(solicitante)
        return self._itens.remover(item.id)

    # ---- Movimentações (qualquer usuário autenticado) ----
    def registrar_entrada(
        self, item: Item, quantidade: int, usuario: Usuario,
        motivo: str | None = None, data: datetime | None = None,
    ) -> Entrada:
        mov = Entrada(item, quantidade, usuario, motivo, data)
        self._aplicar(mov)
        return mov

    def registrar_saida(
        self, item: Item, quantidade: int, usuario: Usuario,
        motivo: str | None = None, data: datetime | None = None,
    ) -> Saida:
        mov = Saida(item, quantidade, usuario, motivo, data)
        self._aplicar(mov)
        return mov

    def _aplicar(self, mov: Movimentacao) -> None:
        mov.aplicar()  # polimorfismo: Entrada e Saida se comportam diferente
        self._movimentacoes.append(mov)

    # ---- Consultas / relatórios ----
    def itens_criticos(self) -> list[Item]:
        return [i for i in self.itens() if i.esta_critico()]

    def relatorio(self) -> dict:
        from src.dominio.tipos import TipoMovimentacao

        itens = self.itens()
        entradas = sum(1 for m in self._movimentacoes if m.tipo == TipoMovimentacao.ENTRADA)
        saidas = sum(1 for m in self._movimentacoes if m.tipo == TipoMovimentacao.SAIDA)
        return {
            "total_itens": len(itens),
            "total_unidades": sum(i.quantidade_atual for i in itens),
            "itens_criticos": len(self.itens_criticos()),
            "total_movimentacoes": len(self._movimentacoes),
            "total_entradas": entradas,
            "total_saidas": saidas,
            "total_locais": len(self._locais),
            "total_categorias": len(self._categorias),
        }

    def itens_por_categoria(self) -> list[tuple[str, int]]:
        contagem = Counter()
        for i in self.itens():
            contagem[i.categoria.nome if i.categoria else "Sem categoria"] += 1
        return sorted(contagem.items(), key=lambda x: -x[1])

    def distribuicao_por_local(self) -> list[dict]:
        resultado = []
        for l in self.locais():
            itens = [i for i in self.itens() if i.local and i.local.id == l.id]
            resultado.append(
                {
                    "nome": l.nome,
                    "itens": len(itens),
                    "unidades": sum(i.quantidade_atual for i in itens),
                }
            )
        return sorted(resultado, key=lambda x: -x["unidades"])

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

    # ---- Séries para gráficos (dashboard / relatórios) ----
    def serie_diaria(self, dias: int = 30, ate: datetime | None = None) -> dict:
        """Entradas e saídas agregadas por dia nos últimos `dias`."""
        from src.dominio.tipos import TipoMovimentacao

        fim = (ate or datetime.now()).date()
        inicio = fim - timedelta(days=dias - 1)
        labels, entradas, saidas = [], [], []
        for n in range(dias):
            dia = inicio + timedelta(days=n)
            labels.append(dia.strftime("%d/%m"))
            ent = sum(
                m.quantidade for m in self._movimentacoes
                if m.criado_em.date() == dia and m.tipo == TipoMovimentacao.ENTRADA
            )
            sai = sum(
                m.quantidade for m in self._movimentacoes
                if m.criado_em.date() == dia and m.tipo == TipoMovimentacao.SAIDA
            )
            entradas.append(ent)
            saidas.append(sai)
        return {"labels": labels, "entradas": entradas, "saidas": saidas}

    def serie_semanal(self, semanas: int = 4, ate: datetime | None = None) -> dict:
        """Entradas e saídas por semana (últimas `semanas` semanas)."""
        from src.dominio.tipos import TipoMovimentacao

        fim = (ate or datetime.now()).date()
        labels, entradas, saidas = [], [], []
        for s in range(semanas - 1, -1, -1):
            ini = fim - timedelta(days=(s + 1) * 7 - 1)
            fim_sem = fim - timedelta(days=s * 7)
            labels.append(f"Sem {semanas - s}")
            ent = sum(
                m.quantidade for m in self._movimentacoes
                if ini <= m.criado_em.date() <= fim_sem and m.tipo == TipoMovimentacao.ENTRADA
            )
            sai = sum(
                m.quantidade for m in self._movimentacoes
                if ini <= m.criado_em.date() <= fim_sem and m.tipo == TipoMovimentacao.SAIDA
            )
            entradas.append(ent)
            saidas.append(sai)
        return {"labels": labels, "entradas": entradas, "saidas": saidas}

    def top_itens_movimentados(self, limite: int = 7, dias: int = 30) -> list[tuple[str, int]]:
        limite_data = (datetime.now() - timedelta(days=dias)).date()
        contagem = Counter()
        for m in self._movimentacoes:
            if m.criado_em.date() >= limite_data:
                contagem[m.item.nome] += m.quantidade
        return contagem.most_common(limite)

    def saude_estoque(self) -> dict:
        """Classifica itens em Saudável / Atenção / Crítico."""
        saudavel = atencao = critico = 0
        for i in self.itens():
            if i.quantidade_atual <= i.estoque_minimo:
                critico += 1
            elif i.quantidade_atual <= i.estoque_minimo * 1.5:
                atencao += 1
            else:
                saudavel += 1
        return {"Saudável": saudavel, "Atenção": atencao, "Crítico": critico}

    def exportar_csv(self) -> str:
        """Gera um relatório CSV do inventário."""
        buffer = io.StringIO()
        escritor = csv.writer(buffer)
        escritor.writerow(
            ["Item", "Categoria", "Local", "Quantidade", "Estoque mínimo", "Status"]
        )
        for i in self.itens():
            escritor.writerow([
                i.nome,
                i.categoria.nome if i.categoria else "",
                i.local.nome if i.local else "",
                i.quantidade_atual,
                i.estoque_minimo,
                "Crítico" if i.esta_critico() else "OK",
            ])
        return buffer.getvalue()

    # ---- Apoio ----
    @staticmethod
    def _exigir_gestor(usuario: Usuario) -> None:
        if not usuario.pode_gerenciar():
            raise PermissionError("Acesso restrito a coordenadores (administradores)")
