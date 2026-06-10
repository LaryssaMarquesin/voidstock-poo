"""VoidStock — Front web fiel ao original (FastAPI + Jinja2).

Camada de apresentação que recria o layout do app React original usando o
CSS de marca. TODA a regra de negócio vem do modelo orientado a objetos em
`src/` — este arquivo só recebe requisições HTTP e chama os métodos do
`Inventario`. O backend é, ele próprio, orientado a objetos.

Execução local:  python -m uvicorn web_app:app --reload
Acesse:          http://localhost:8000
"""
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.dominio.item import Item
from src.seed import criar_inventario_demo

BASE = Path(__file__).parent
app = FastAPI(title="VoidStock POO")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

# Estado único em memória (demo). O Inventário é o agregado OO central.
inventario = criar_inventario_demo()


def usuario_atual(req: Request):
    """Resolve o usuário logado a partir do parâmetro ?user=<id>."""
    uid = req.query_params.get("user")
    usuarios = inventario.usuarios()
    return next((u for u in usuarios if u.id == uid), usuarios[0])


def ctx(req: Request, pagina: str, titulo: str, **extra) -> dict:
    base = {
        "request": req,
        "pagina": pagina,
        "titulo": titulo,
        "usuario": usuario_atual(req),
        "usuarios": inventario.usuarios(),
    }
    base.update(extra)
    return base


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    r = inventario.relatorio()
    por_categoria = inventario.itens_por_categoria()
    por_local = inventario.distribuicao_por_local()
    return templates.TemplateResponse(
        request, "dashboard.html",
        ctx(
            request, "dashboard", "Dashboard",
            r=r,
            por_categoria=por_categoria,
            max_cat=max((q for _, q in por_categoria), default=0),
            por_local=por_local,
            max_local=max((l["unidades"] for l in por_local), default=0),
            criticos=inventario.itens_criticos(),
        ),
    )


@app.get("/inventario", response_class=HTMLResponse)
def inventario_page(request: Request, q: str = "", cat: str = ""):
    itens = inventario.itens()
    ql = q.strip().lower()
    if ql:
        itens = [i for i in itens if ql in i.nome.lower()]
    if cat:
        itens = [i for i in itens if i.categoria and i.categoria.nome == cat]
    return templates.TemplateResponse(
        request, "inventario.html",
        ctx(request, "inventario", "Inventário",
            itens=itens, categorias=inventario.categorias(), q=q, cat=cat),
    )


@app.get("/movimentacoes", response_class=HTMLResponse)
def movimentacoes_page(request: Request, msg: str = "", msg_tipo: str = "ok"):
    return templates.TemplateResponse(
        request, "movimentacoes.html",
        ctx(request, "movimentacoes", "Movimentações",
            itens=inventario.itens(), movimentacoes=inventario.movimentacoes(),
            msg=msg, msg_tipo=msg_tipo),
    )


@app.post("/movimentacoes")
def registrar_mov(
    request: Request,
    item_id: str = Form(...),
    tipo: str = Form(...),
    quantidade: int = Form(...),
    motivo: str = Form(""),
):
    user = usuario_atual(request)
    item = next((i for i in inventario.itens() if i.id == item_id), None)
    try:
        if item is None:
            raise ValueError("Item inválido")
        if tipo == "entrada":
            inventario.registrar_entrada(item, quantidade, user, motivo or None)
        else:
            inventario.registrar_saida(item, quantidade, user, motivo or None)
        msg, tipo_msg = f"{tipo.capitalize()} registrada. {item.nome}: {item.quantidade_atual} un.", "ok"
    except (ValueError, PermissionError) as e:
        msg, tipo_msg = str(e), "err"
    return RedirectResponse(
        f"/movimentacoes?user={user.id}&msg={msg}&msg_tipo={tipo_msg}", status_code=303
    )


@app.get("/cadastrar", response_class=HTMLResponse)
def cadastrar_page(request: Request, msg: str = "", msg_tipo: str = "ok"):
    user = usuario_atual(request)
    sugestao = None
    if user.pode_gerenciar():
        local, motivo = inventario.sugerir_local(None)
        if local:
            sugestao = {"nome": local.nome, "motivo": motivo}
    return templates.TemplateResponse(
        request, "cadastrar.html",
        ctx(request, "cadastrar", "Cadastrar item",
            categorias=inventario.categorias(), sugestao=sugestao,
            msg=msg, msg_tipo=msg_tipo),
    )


@app.post("/cadastrar")
def cadastrar_item(
    request: Request,
    nome: str = Form(...),
    categoria: str = Form(""),
    minimo: int = Form(0),
    quantidade: int = Form(0),
):
    user = usuario_atual(request)
    try:
        cat = next((c for c in inventario.categorias() if c.nome == categoria), None)
        local, _ = inventario.sugerir_local(cat)
        item = Item(nome, estoque_minimo=minimo, categoria=cat, local=local)
        inventario.cadastrar_item(item, user, quantidade_inicial=quantidade)
        msg, tipo_msg = f"Item '{nome}' cadastrado com sucesso.", "ok"
    except (ValueError, PermissionError) as e:
        msg, tipo_msg = str(e), "err"
    return RedirectResponse(
        f"/cadastrar?user={user.id}&msg={msg}&msg_tipo={tipo_msg}", status_code=303
    )
