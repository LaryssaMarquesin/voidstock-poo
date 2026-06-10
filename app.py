"""VoidStock — Front visual em Streamlit (tema oficial roxo/laranja).

Camada FINA de apresentação sobre o modelo OO (src/). Toda a regra de
negócio vive nas classes; aqui só montamos a interface e chamamos os métodos
do `Inventario`. Deploy gratuito no Streamlit Community Cloud direto do GitHub.

Execução local:  python -m streamlit run app.py
"""
import base64
from pathlib import Path

import streamlit as st

from src.dominio.item import Item
from src.seed import criar_inventario_demo

# ---- Marca VoidStock ----
ROXO = "#7e2a90"
ROXO_FUNDO = "#4a1556"
LARANJA = "#f26722"
GRAD = f"linear-gradient(135deg, {ROXO} 0%, {LARANJA} 100%)"

st.set_page_config(page_title="VoidStock", page_icon="📦", layout="wide")


def _logo_b64() -> str:
    p = Path(__file__).parent / "assets" / "voidstock-logo.png"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return ""


LOGO = _logo_b64()

# ---- CSS: replica os tokens reais do VoidStock ----
st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

      .stApp {{
        background-color: #14101c;
        background-image:
          radial-gradient(ellipse 60% 40% at 15% 0%, rgba(126,42,144,0.28), transparent 60%),
          radial-gradient(ellipse 50% 40% at 95% 12%, rgba(242,103,34,0.14), transparent 60%),
          radial-gradient(ellipse 70% 50% at 50% 100%, rgba(74,21,86,0.30), transparent 60%);
        background-attachment: fixed;
        color: #ececf1;
        font-family: 'Inter', sans-serif;
      }}
      header[data-testid="stHeader"] {{ background: transparent; }}
      #MainMenu, footer {{ visibility: hidden; }}

      h1,h2,h3,h4 {{ font-family: 'Space Grotesk', sans-serif; letter-spacing:-0.02em; color:#fff; }}

      section[data-testid="stSidebar"] {{
        background: #1a1424; border-right: 1px solid rgba(255,255,255,0.06);
      }}

      /* Hero */
      .vs-hero {{
        display:flex; align-items:center; gap:16px;
        padding: 22px 26px; border-radius: 20px; margin-bottom: 22px;
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 20px 60px -20px rgba(126,42,144,0.55);
      }}
      .vs-hero img {{ height: 40px; }}
      .vs-hero .sub {{ color:#a9a3bd; font-size:0.9rem; margin-top:2px; }}
      .vs-badge {{
        margin-left:auto; font-size:0.7rem; font-weight:700; letter-spacing:0.08em;
        text-transform:uppercase; color:#fff; padding:6px 12px; border-radius:8px;
        background:{GRAD};
      }}
      .grad-text {{
        background:{GRAD}; -webkit-background-clip:text; background-clip:text;
        color:transparent; font-weight:700;
      }}

      /* Cards de métrica */
      .vs-cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:8px; }}
      .vs-card {{
        border-radius:16px; padding:18px 20px;
        border:1px solid rgba(255,255,255,0.07);
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
      }}
      .vs-card.roxo {{ background:linear-gradient(180deg, rgba(126,42,144,0.16), rgba(126,42,144,0.04)); border-color:rgba(126,42,144,0.30); }}
      .vs-card.laranja {{ background:linear-gradient(180deg, rgba(242,103,34,0.16), rgba(242,103,34,0.04)); border-color:rgba(242,103,34,0.30); }}
      .vs-card .v {{ font-family:'Space Grotesk'; font-size:2rem; font-weight:700; color:#fff; }}
      .vs-card .l {{ font-size:0.78rem; color:#a9a3bd; margin-top:4px; }}

      /* Tabela */
      .vs-table {{ width:100%; border-collapse:separate; border-spacing:0; margin-top:6px; }}
      .vs-table th {{
        text-align:left; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em;
        color:#a9a3bd; padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.08);
      }}
      .vs-table td {{ padding:12px 14px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:0.9rem; }}
      .vs-table tr:hover td {{ background:rgba(255,255,255,0.03); }}
      .pill {{ font-size:0.72rem; font-weight:600; padding:3px 10px; border-radius:999px; }}
      .pill.ok {{ background:rgba(77,212,160,0.15); color:#5fe3b0; }}
      .pill.crit {{ background:rgba(242,103,34,0.18); color:#ffa14a; }}

      /* Botões */
      .stButton button, .stFormSubmitButton button {{
        background:{GRAD}; color:#fff; border:0; border-radius:10px; font-weight:600;
        box-shadow:0 12px 30px -12px rgba(126,42,144,0.6);
      }}
      .stButton button:hover {{ opacity:0.93; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Estado ----
if "inv" not in st.session_state:
    st.session_state.inv = criar_inventario_demo()
inv = st.session_state.inv

# ---- Hero ----
logo_html = f'<img src="data:image/png;base64,{LOGO}" alt="VoidStock"/>' if LOGO else '<span class="grad-text" style="font-size:1.6rem">VoidStock</span>'
st.markdown(
    f"""
    <div class="vs-hero">
      <div>{logo_html}</div>
      <div>
        <div style="font-family:'Space Grotesk';font-weight:700;font-size:1.15rem;">Painel de estoque</div>
        <div class="sub">Controle inteligente para equipes técnicas · versão POO</div>
      </div>
      <span class="vs-badge">ao vivo</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Sidebar: usuário + navegação ----
with st.sidebar:
    st.markdown('<div class="grad-text" style="font-size:1.3rem;margin-bottom:8px;">VoidStock</div>', unsafe_allow_html=True)
    usuarios = inv.usuarios()
    nomes = {f"{u.nome} · {u.papel.value}": u for u in usuarios}
    sel = st.selectbox("Logado como", list(nomes.keys()))
    usuario_atual = nomes[sel]
    pode_gerir = usuario_atual.pode_gerenciar()
    st.caption(("✅ Coordenador — pode gerenciar" if pode_gerir else "🔒 Usuário — só movimenta"))
    st.divider()
    pagina = st.radio("Navegação", ["Dashboard", "Inventário", "Movimentações", "Cadastrar item"])


def card(valor, rotulo, tom=""):
    return f'<div class="vs-card {tom}"><div class="v">{valor}</div><div class="l">{rotulo}</div></div>'


# ---- Dashboard ----
if pagina == "Dashboard":
    r = inv.relatorio()
    st.markdown(
        '<div class="vs-cards">'
        + card(r["total_itens"], "Itens cadastrados", "roxo")
        + card(r["itens_criticos"], "Itens críticos", "laranja")
        + card(r["total_unidades"], "Unidades em estoque", "roxo")
        + card(r["total_movimentacoes"], "Movimentações", "laranja")
        + "</div>",
        unsafe_allow_html=True,
    )

    criticos = inv.itens_criticos()
    st.markdown("### Itens que precisam de reposição")
    if criticos:
        linhas = "".join(
            f"<tr><td>{i.nome}</td><td>{i.local.nome if i.local else '—'}</td>"
            f"<td>{i.quantidade_atual}</td><td>{i.estoque_minimo}</td>"
            f'<td><span class="pill crit">repor</span></td></tr>'
            for i in criticos
        )
        st.markdown(
            f'<table class="vs-table"><tr><th>Item</th><th>Local</th><th>Atual</th><th>Mínimo</th><th>Status</th></tr>{linhas}</table>',
            unsafe_allow_html=True,
        )
    else:
        st.success("Nenhum item crítico. 🎉")

# ---- Inventário ----
elif pagina == "Inventário":
    st.markdown("### Inventário")
    itens = inv.itens()
    if itens:
        linhas = ""
        for i in itens:
            critico = i.esta_critico()
            pill = '<span class="pill crit">crítico</span>' if critico else '<span class="pill ok">ok</span>'
            linhas += (
                f"<tr><td><b>{i.nome}</b></td><td>{i.categoria.nome if i.categoria else '—'}</td>"
                f"<td>{i.local.nome if i.local else '—'}</td><td>{i.quantidade_atual}</td>"
                f"<td>{i.estoque_minimo}</td><td>{pill}</td></tr>"
            )
        st.markdown(
            f'<table class="vs-table"><tr><th>Item</th><th>Categoria</th><th>Local</th>'
            f"<th>Qtd.</th><th>Mín.</th><th>Status</th></tr>{linhas}</table>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Nenhum item cadastrado.")

# ---- Movimentações ----
elif pagina == "Movimentações":
    st.markdown("### Registrar movimentação")
    itens = inv.itens()
    if not itens:
        st.info("Cadastre um item primeiro.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        item_nome = c1.selectbox("Item", [i.nome for i in itens])
        item = next(i for i in itens if i.nome == item_nome)
        tipo = c2.radio("Tipo", ["Entrada", "Saída"])
        qtd = c3.number_input("Quantidade", min_value=1, value=1, step=1)
        st.caption(f"Estoque atual de **{item.nome}**: {item.quantidade_atual} un.")
        motivo = st.text_input("Motivo (opcional)")
        if st.button("Registrar movimentação"):
            try:
                if tipo == "Entrada":
                    inv.registrar_entrada(item, int(qtd), usuario_atual, motivo or None)
                else:
                    inv.registrar_saida(item, int(qtd), usuario_atual, motivo or None)
                st.success(f"{tipo} registrada. {item.nome} agora: {item.quantidade_atual} un.")
                st.rerun()
            except (ValueError, PermissionError) as e:
                st.error(str(e))

    movs = inv.movimentacoes()
    if movs:
        st.markdown("### Histórico")
        linhas = "".join(
            f"<tr><td>{m.criado_em.strftime('%d/%m %H:%M')}</td>"
            f'<td><span class="pill {"ok" if m.tipo.value=="entrada" else "crit"}">{m.tipo.value}</span></td>'
            f"<td>{m.item.nome}</td><td>{m.quantidade}</td><td>{m.usuario.nome}</td>"
            f"<td>{m.motivo or '—'}</td></tr>"
            for m in movs
        )
        st.markdown(
            f'<table class="vs-table"><tr><th>Quando</th><th>Tipo</th><th>Item</th>'
            f"<th>Qtd.</th><th>Por</th><th>Motivo</th></tr>{linhas}</table>",
            unsafe_allow_html=True,
        )

# ---- Cadastrar item ----
elif pagina == "Cadastrar item":
    st.markdown("### Cadastrar item")
    if not pode_gerir:
        st.error("🔒 Acesso restrito a coordenadores. Troque o usuário na barra lateral.")
    else:
        nome = st.text_input("Nome do item")
        cats = inv.categorias()
        cat_nome = st.selectbox("Categoria", ["—"] + [c.nome for c in cats])
        categoria = next((c for c in cats if c.nome == cat_nome), None)

        local_sug, motivo = inv.sugerir_local(categoria)
        if local_sug:
            st.info(f"💡 Local sugerido: **{local_sug.nome}** — {motivo}")

        c1, c2 = st.columns(2)
        minimo = c1.number_input("Estoque mínimo", min_value=0, value=0, step=1)
        qtd_ini = c2.number_input("Quantidade inicial", min_value=0, value=0, step=1)

        if st.button("Cadastrar item"):
            if not nome.strip():
                st.error("Informe o nome do item.")
            else:
                try:
                    item = Item(nome, estoque_minimo=int(minimo), categoria=categoria, local=local_sug)
                    inv.cadastrar_item(item, usuario_atual, quantidade_inicial=int(qtd_ini))
                    st.success(f"Item '{nome}' cadastrado.")
                    st.rerun()
                except (ValueError, PermissionError) as e:
                    st.error(str(e))
