# VoidStock — POO

Sistema de **controle de estoque para laboratórios técnicos**, reescrito em
**Python orientado a objetos**. Versão acadêmica (Programação Orientada a
Objetos) do projeto VoidStock — equipes técnicas registram, localizam e
controlam componentes (sensores, microcontroladores, ferramentas).

Roda de duas formas:

- **Console (CLI):** `python main.py` — zero dependências, roda em qualquer
  Python 3.10+ (Replit, Colab, terminal).
- **Web (visual):** `streamlit run app.py` — interface com a identidade
  visual do VoidStock (roxo/laranja). Deploy gratuito no Streamlit Cloud.

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

## Modelo de domínio (resumo)

- **Item** — nome, categoria, local, estoque mínimo e quantidade atual (encapsulada).
- **Movimentacao** (abstrata) → **Entrada** / **Saida**, que aplicam o efeito no item.
- **Usuario** (abstrata) → **Administrador** (gerencia o catálogo) / **UsuarioComum** (só movimenta).
- **Inventario** — reúne tudo e implementa: itens críticos, relatório e a
  **sugestão automática de local** (mesma categoria → local mais usado; senão → local mais livre).
