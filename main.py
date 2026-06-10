"""VoidStock — Console (CLI).

App de console SEM dependências externas: roda em qualquer Python 3.10+,
inclusive no Replit ou Google Colab. Demonstra o modelo orientado a objetos
em funcionamento, com menu interativo.

Execução:  python main.py
"""
from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.seed import criar_inventario_demo
from src.servicos.inventario import Inventario


def escolher(titulo: str, opcoes: list) -> object | None:
    if not opcoes:
        print("  (nenhum cadastrado)")
        return None
    print(titulo)
    for i, op in enumerate(opcoes, 1):
        print(f"  {i}. {op}")
    try:
        idx = int(input("  Escolha o número: ")) - 1
        return opcoes[idx] if 0 <= idx < len(opcoes) else None
    except (ValueError, IndexError):
        return None


def mostrar_dashboard(inv: Inventario) -> None:
    r = inv.relatorio()
    print("\n=== DASHBOARD VOIDSTOCK ===")
    print(f"  Itens cadastrados : {r['total_itens']}")
    print(f"  Unidades em estoque: {r['total_unidades']}")
    print(f"  Itens críticos    : {r['itens_criticos']}")
    print(f"  Movimentações     : {r['total_movimentacoes']}")
    criticos = inv.itens_criticos()
    if criticos:
        print("  !  Repor:")
        for i in criticos:
            print(f"     - {i.nome} ({i.quantidade_atual}/{i.estoque_minimo} mín.)")


def listar_itens(inv: Inventario) -> None:
    print("\n=== INVENTÁRIO ===")
    for i in inv.itens():
        flag = " ! CRÍTICO" if i.esta_critico() else ""
        local = i.local.nome if i.local else "sem local"
        print(f"  - {i.nome:35} {i.quantidade_atual:>4} un.  @ {local}{flag}")


def fluxo_movimentacao(inv: Inventario, entrada: bool) -> None:
    item = escolher("\nSelecione o item:", inv.itens())
    if not item:
        print("  Item inválido."); return
    usuario = escolher("Selecione o usuário:", inv.usuarios())
    if not usuario:
        print("  Usuário inválido."); return
    try:
        qtd = int(input("  Quantidade: "))
        if entrada:
            inv.registrar_entrada(item, qtd, usuario, "Movimentação via console")
        else:
            inv.registrar_saida(item, qtd, usuario, "Movimentação via console")
        print(f"  OK {item.nome} agora tem {item.quantidade_atual} un.")
    except (ValueError, PermissionError) as e:
        print(f"  X Erro: {e}")


def fluxo_cadastro(inv: Inventario) -> None:
    usuario = escolher("\nQuem está cadastrando?", inv.usuarios())
    if not usuario:
        return
    nome = input("  Nome do item: ").strip()
    categoria = escolher("Categoria:", inv.categorias())
    try:
        minimo = int(input("  Estoque mínimo: ") or "0")
        qtd = int(input("  Quantidade inicial: ") or "0")
        # Sugestão automática de local (heurística do projeto original)
        local, motivo = inv.sugerir_local(categoria if isinstance(categoria, Categoria) else None)
        print(f"  >> Local sugerido: {local.nome if local else '—'} ({motivo})")
        item = Item(nome, estoque_minimo=minimo, categoria=categoria, local=local)
        inv.cadastrar_item(item, usuario, quantidade_inicial=qtd)
        print(f"  OK '{nome}' cadastrado.")
    except (ValueError, PermissionError) as e:
        print(f"  X Erro: {e}")


def main() -> None:
    inv = criar_inventario_demo()
    menu = {
        "1": ("Dashboard", lambda: mostrar_dashboard(inv)),
        "2": ("Listar inventário", lambda: listar_itens(inv)),
        "3": ("Registrar ENTRADA", lambda: fluxo_movimentacao(inv, True)),
        "4": ("Registrar SAÍDA", lambda: fluxo_movimentacao(inv, False)),
        "5": ("Cadastrar item", lambda: fluxo_cadastro(inv)),
        "6": ("Histórico de movimentações", lambda: [print(f"  {m}") for m in inv.movimentacoes()]),
    }
    print("VoidStock — Controle de estoque para laboratórios (versão POO/console)")
    while True:
        print("\n" + "-" * 50)
        for k, (label, _) in menu.items():
            print(f"  {k}. {label}")
        print("  0. Sair")
        escolha = input("> ").strip()
        if escolha == "0":
            print("Até logo!")
            break
        acao = menu.get(escolha)
        if acao:
            acao[1]()
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    main()
