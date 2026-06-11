"""Dados de exemplo para demonstração.

Cria um Inventário populado com categorias, locais, usuários, itens (com
imagens) e ~30 dias de movimentações históricas, para que o dashboard e os
relatórios tenham dados realistas.
"""
from datetime import datetime, timedelta

from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.dominio.usuario import Administrador, UsuarioComum
from src.servicos.inventario import Inventario


def _img(slug: str, real: bool = False) -> str:
    """Caminho da imagem: fotos reais em /static/img, thumbnails em /static/img/gen."""
    return f"/static/img/{slug}.jpg" if real else f"/static/img/gen/{slug}.svg"


def criar_inventario_demo() -> Inventario:
    inv = Inventario()

    # Usuários
    coord = inv.adicionar_usuario(Administrador("Robson Coordenador", "robson@pilhadigital.com.br"))
    helen = inv.adicionar_usuario(UsuarioComum("Helen Ribeiro", "helen@artcont.com.br"))
    lary = inv.adicionar_usuario(UsuarioComum("Laryssa Marquesin", "lmarquesin@gmail.com"))

    # Categorias
    cat = {n: inv.adicionar_categoria(Categoria(n)) for n in [
        "Microcontroladores", "Sensores", "Atuadores", "Componentes Eletrônicos",
        "Cabos", "Ferramentas",
    ]}

    # Locais
    loc = {n: inv.adicionar_local(Local(n)) for n in [
        "Gaveta B3", "Armário 1", "Bancada Central", "Prateleira A2",
    ]}

    # (nome, categoria, local, minimo, qtd_inicial, slug, foto_real)
    catalogo = [
        ("Arduino Uno R3", "Microcontroladores", "Armário 1", 4, 14, "arduino-uno", True),
        ("ESP32 DevKit V1", "Microcontroladores", "Armário 1", 4, 3, "esp32", True),
        ("Raspberry Pi 4 4GB", "Microcontroladores", "Armário 1", 2, 5, "raspberry-pi", True),
        ("Multímetro Digital", "Ferramentas", "Bancada Central", 2, 6, "multimetro", True),
        ("LED RGB 5mm", "Componentes Eletrônicos", "Gaveta B3", 50, 220, "led", True),
        ("Sensor Ultrassônico HC-SR04", "Sensores", "Gaveta B3", 6, 12, "hc-sr04", False),
        ("Sensor de Temperatura DHT22", "Sensores", "Gaveta B3", 5, 2, "dht22", False),
        ("Sensor de Presença PIR", "Sensores", "Gaveta B3", 5, 9, "pir", False),
        ("Micro Servo SG90", "Atuadores", "Prateleira A2", 6, 18, "servo-sg90", False),
        ("Motor DC 6V", "Atuadores", "Prateleira A2", 4, 4, "motor-dc", False),
        ("Módulo Relé 1 Canal", "Atuadores", "Prateleira A2", 5, 11, "rele", False),
        ("Kit Resistores 1/4W", "Componentes Eletrônicos", "Gaveta B3", 20, 80, "resistores", False),
        ("Capacitores Eletrolíticos", "Componentes Eletrônicos", "Gaveta B3", 30, 25, "capacitores", False),
        ("Potenciômetro 10kΩ", "Componentes Eletrônicos", "Gaveta B3", 10, 40, "potenciometro", False),
        ("Buzzer Ativo 5V", "Componentes Eletrônicos", "Gaveta B3", 8, 15, "buzzer", False),
        ("Display LCD 16x2", "Componentes Eletrônicos", "Prateleira A2", 3, 7, "display-lcd", False),
        ("Protoboard 830 Pontos", "Componentes Eletrônicos", "Bancada Central", 5, 13, "protoboard", False),
        ("Jumpers Macho-Macho (40un)", "Cabos", "Gaveta B3", 10, 30, "jumpers", False),
        ("Ferro de Solda 60W", "Ferramentas", "Bancada Central", 2, 3, "ferro-solda", False),
    ]

    agora = datetime.now()
    itens = {}
    for nome, categoria, local, minimo, qtd, slug, real in catalogo:
        item = Item(
            nome, estoque_minimo=minimo, categoria=cat[categoria],
            local=loc[local], imagem_url=_img(slug, real),
        )
        # cadastro inicial datado ~35 dias atrás
        inv.cadastrar_item(item, coord, quantidade_inicial=0)
        inv.registrar_entrada(
            item, qtd, coord, "Cadastro inicial", data=agora - timedelta(days=35),
        )
        itens[nome] = item

    # Movimentações históricas (entradas e saídas) ao longo de ~30 dias.
    # Padrão determinístico (sem aleatoriedade) para ser reproduzível.
    usuarios = [coord, helen, lary]
    nomes = list(itens.keys())
    for d in range(30, 0, -1):
        dia = agora - timedelta(days=d)
        for k in range(3):  # 3 movimentações por dia
            item = itens[nomes[(d * 3 + k) % len(nomes)]]
            usuario = usuarios[(d + k) % len(usuarios)]
            if (d + k) % 3 == 0:
                inv.registrar_entrada(item, 2 + (k % 4), usuario, "Reposição", data=dia)
            else:
                qtd = 1 + (k % 3)
                if item.quantidade_atual >= qtd:
                    inv.registrar_saida(item, qtd, usuario, "Uso em projeto", data=dia)

    return inv
