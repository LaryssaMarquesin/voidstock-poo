"""VoidStock — Front visual em Streamlit.

Camada FINA de apresentação sobre o modelo OO (src/). Toda a regra de
negócio vive nas classes; aqui só montamos a interface e chamamos os métodos
do `Inventario`. Deploy gratuito no Streamlit Community Cloud direto do GitHub.

Execução local:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.seed import criar_inventario_demo

# ---- Marca VoidStock (roxo + laranja) ----
ROXO = "#7E2A90"
LARANJA = "#F26722"

st.set_page_config(page_title="VoidStock", page_icon="📦", layout="wide")

st.markdown(
    f"""
    <style>
      .stApp {{ background: #0e0b14; color: #ececf1; }}
      h1, h2, h3 {{ color: #fff; }}
      div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, rgba(126,42,144,0.25), rgba(242,103,34,0.18));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 16px;
      }}
      .stButton button {{
        background: linear-gradient(135deg, {ROXO}, {LARANJA});
        color: white; border: 0; border-radius: 10px; font-weight: 600;
      }}
      .marca {{ font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, {ROXO}, {LARANJA});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Estado: um único Inventário vive durante a sessão ----
if "inv" not in st.session_state:
    st.session_state.inv = criar_inventario_demo()
inv = st.session_state.inv

# ---- Cabeçalho + escolha de usuário (mostra o controle de permissão) ----
st.markdown('<div class="marca">VoidStock</div>', unsafe_allow_html=True)
st.caption("Controle de estoque inteligente para equipes técnicas — versão POO")

usuarios = inv.usuarios()
nomes = {f"{u.nome} ({u.papel.value})": u for u in usuarios}
sel = st.sidebar.selectbox("Logado como", list(nomes.keys()))
usuario_atual = nomes[sel]
pode_gerir = usuario_atual.pode_gerenciar()
st.sidebar.write("Permissão de gestão:", "✅ sim" if pode_gerir else "🔒 não")

pagina = st.sidebar.radio(
    "Navegação", ["Dashboard", "Inventário", "Movimentações", "Cadastrar item"]
)

# ---- Dashboard ----
if pagina == "Dashboard":
    st.subheader("Dashboard")
    r = inv.relatorio()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Itens cadastrados", r["total_itens"])
    c2.metric("Unidades em estoque", r["total_unidades"])
    c3.metric("Itens críticos", r["itens_criticos"])
    c4.metric("Movimentações", r["total_movimentacoes"])

    criticos = inv.itens_criticos()
    if criticos:
        st.warning("Itens que precisam de reposição:")
        st.table(
            pd.DataFrame(
                [
                    {"Item": i.nome, "Atual": i.quantidade_atual, "Mínimo": i.estoque_minimo}
                    for i in criticos
                ]
            )
        )
    else:
        st.success("Nenhum item crítico. 🎉")

# ---- Inventário ----
elif pagina == "Inventário":
    st.subheader("Inventário")
    itens = inv.itens()
    if itens:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Item": i.nome,
                        "Categoria": i.categoria.nome if i.categoria else "—",
                        "Local": i.local.nome if i.local else "—",
                        "Qtd.": i.quantidade_atual,
                        "Mínimo": i.estoque_minimo,
                        "Status": "⚠ Crítico" if i.esta_critico() else "OK",
                    }
                    for i in itens
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum item cadastrado.")

# ---- Movimentações ----
elif pagina == "Movimentações":
    st.subheader("Registrar movimentação")
    itens = inv.itens()
    if not itens:
        st.info("Cadastre um item primeiro.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            item_nome = st.selectbox("Item", [i.nome for i in itens])
            item = next(i for i in itens if i.nome == item_nome)
            st.caption(f"Estoque atual: {item.quantidade_atual} un.")
        with col2:
            tipo = st.radio("Tipo", ["Entrada", "Saída"], horizontal=True)
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
        motivo = st.text_input("Motivo (opcional)")
        if st.button("Registrar"):
            try:
                if tipo == "Entrada":
                    inv.registrar_entrada(item, int(qtd), usuario_atual, motivo or None)
                else:
                    inv.registrar_saida(item, int(qtd), usuario_atual, motivo or None)
                st.success(f"{tipo} registrada. {item.nome} agora: {item.quantidade_atual} un.")
                st.rerun()
            except (ValueError, PermissionError) as e:
                st.error(str(e))

    st.divider()
    st.subheader("Histórico")
    movs = inv.movimentacoes()
    if movs:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Quando": m.criado_em.strftime("%d/%m %H:%M"),
                        "Tipo": m.tipo.value,
                        "Item": m.item.nome,
                        "Qtd.": m.quantidade,
                        "Por": m.usuario.nome,
                        "Motivo": m.motivo or "—",
                    }
                    for m in movs
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sem movimentações ainda.")

# ---- Cadastrar item (exige permissão) ----
elif pagina == "Cadastrar item":
    st.subheader("Cadastrar item")
    if not pode_gerir:
        st.error("🔒 Acesso restrito a coordenadores. Troque o usuário na barra lateral.")
    else:
        nome = st.text_input("Nome do item")
        cats = inv.categorias()
        cat_nome = st.selectbox("Categoria", ["—"] + [c.nome for c in cats])
        categoria = next((c for c in cats if c.nome == cat_nome), None)

        # Sugestão automática de local (heurística do projeto original)
        local_sug, motivo = inv.sugerir_local(categoria)
        if local_sug:
            st.info(f"💡 Local sugerido: **{local_sug.nome}** — {motivo}")

        col1, col2 = st.columns(2)
        minimo = col1.number_input("Estoque mínimo", min_value=0, value=0, step=1)
        qtd_ini = col2.number_input("Quantidade inicial", min_value=0, value=0, step=1)

        if st.button("Cadastrar"):
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
