# VoidStock — POO

Sistema de **controle de estoque para laboratórios técnicos**, reescrito em
**Python orientado a objetos**. Versão acadêmica (Programação Orientada a
Objetos) do projeto VoidStock — equipes técnicas registram, localizam e
controlam componentes (sensores, microcontroladores, ferramentas).

Roda de três formas:

- **Web fiel (FastAPI):** `python -m uvicorn web_app:app --reload` →
  http://localhost:8000 — recria o layout do app original (sidebar, hero,
  KPIs, tabelas) com o CSS de marca. **Recomendado para apresentar.**
- **Console (CLI):** `python main.py` — zero dependências, roda em qualquer
  Python 3.10+ (Replit, Colab, terminal).
- **Web simples (Streamlit):** `python -m streamlit run app.py` — alternativa
  rápida de deploy.

---

## Pilares de OO demonstrados

| Pilar | Onde |
|---|---|
| **Abstração** | `Entidade` (base), `Movimentacao` e `Usuario` como classes abstratas (`ABC`) |
| **Encapsulamento** | `Item.quantidade_atual` é privada; só muda via `registrar_entrada/saida` (estoque nunca negativo) |
| **Herança** | `Administrador`/`UsuarioComum` herdam de `Usuario`; `Entrada`/`Saida` herdam de `Movimentacao` |
| **Polimorfismo** | `mov.aplicar()` se comporta diferente em `Entrada` vs `Saida`; `usuario.pode_gerenciar()` por subclasse |
| **Interface + Generics** | `Repositorio[T]` (contrato genérico) com `RepositorioEmMemoria` |
| **Composição** | `Inventario` é composto por repositórios e orquestra as regras |

---

## Estrutura

```
voidstock-poo/
├── main.py                  # App de console (CLI)
├── app.py                   # Front web (Streamlit)
├── requirements.txt
└── src/
    ├── dominio/
    │   ├── entidade.py      # Entidade base (id único)
    │   ├── tipos.py         # Enums: TipoMovimentacao, Papel
    │   ├── categoria.py
    │   ├── local.py
    │   ├── usuario.py       # Usuario (ABC) -> Administrador, UsuarioComum
    │   ├── item.py          # Encapsula a quantidade em estoque
    │   └── movimentacao.py  # Movimentacao (ABC) -> Entrada, Saida
    ├── repositorio/
    │   └── repositorio.py   # Repositorio[T] (ABC) + RepositorioEmMemoria
    ├── servicos/
    │   └── inventario.py    # Agregado central (regras de negócio)
    └── seed.py              # Dados de exemplo
```

---

## Como rodar

### Console
```bash
python main.py
```

### Web (local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Web (online, grátis, sem servidor)
1. Suba este repositório no GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte sua conta GitHub.
3. Aponte para este repo, arquivo principal `app.py` → **Deploy**.
4. Pronto: você recebe um link público que roda na nuvem.

---

## Reconhecimento de itens por imagem (IA)

O "coração" do projeto: na tela **Cadastrar item**, envie a foto de um
componente e a IA preenche **nome, categoria e descrição** automaticamente.

- Implementado em `src/servicos/reconhecimento.py` com a API oficial do
  **Google Gemini** (`gemini-2.5-flash`), atrás de uma interface OO abstrata
  (`Reconhecedor`) — trocar de provedor não afeta o resto do app.
- Requer a variável de ambiente **`GEMINI_API_KEY`** (chave grátis em
  https://aistudio.google.com/apikey). Sem ela, o cadastro manual segue
  funcionando e a tela avisa que a IA está indisponível.

No Render: **Environment → Add Environment Variable** → `GEMINI_API_KEY`.
Local: defina no shell antes de rodar (`$env:GEMINI_API_KEY="..."` no PowerShell).

## Dashboard e relatórios

- **Dashboard** com gráficos (Chart.js): movimentação diária (30 dias), saúde
  do estoque, itens por categoria, entradas vs saídas por semana e top itens.
- **Relatórios** com gráficos + tabela completa e **exportação CSV**.
- Dados gerados a partir de ~30 dias de movimentações no seed.

## Modelo de domínio (resumo)

- **Item** — nome, categoria, local, estoque mínimo e quantidade atual (encapsulada).
- **Movimentacao** (abstrata) → **Entrada** / **Saida**, que aplicam o efeito no item.
- **Usuario** (abstrata) → **Administrador** (gerencia o catálogo) / **UsuarioComum** (só movimenta).
- **Inventario** — reúne tudo e implementa: itens críticos, relatório e a
  **sugestão automática de local** (mesma categoria → local mais usado; senão → local mais livre).
