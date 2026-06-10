"""Dados de exemplo para demonstração.

Cria um Inventário já populado com categorias, locais, usuários e itens —
útil tanto para o console quanto para o front Streamlit.
"""
from src.dominio.categoria import Categoria
from src.dominio.item import Item
from src.dominio.local import Local
from src.dominio.usuario import Administrador, UsuarioComum
from src.servicos.inventario import Inventario


def criar_inventario_demo() -> Inventario:
    inv = Inventario()

    # Usuários
    coord = inv.adicionar_usuario(Administrador("Robson Coordenador", "robson@pilhadigital.com.br"))
    inv.adicionar_usuario(UsuarioComum("Helen Ribeiro", "helen@artcont.com.br"))

    # Categorias
    sensores = inv.adicionar_categoria(Categoria("Sensores"))
    microcontroladores = inv.adicionar_categoria(Categoria("Microcontroladores"))
    ferramentas = inv.adicionar_categoria(Categoria("Ferramentas"))
    cabos = inv.adicionar_categoria(Categoria("Cabos"))

    # Locais
    gaveta_b3 = inv.adicionar_local(Local("Gaveta B3"))
    armario_1 = inv.adicionar_local(Local("Armário 1"))
    bancada = inv.adicionar_local(Local("Bancada Central"))

    # Itens (cadastrados pelo coordenador, com estoque inicial)
    inv.cadastrar_item(
        Item("Sensor ultrassônico HC-SR04", estoque_minimo=5, categoria=sensores, local=gaveta_b3),
        coord, quantidade_inicial=12,
    )
    inv.cadastrar_item(
        Item("Sensor de temperatura DHT22", estoque_minimo=4, categoria=sensores, local=gaveta_b3),
        coord, quantidade_inicial=3,  # abaixo do mínimo -> crítico
    )
    inv.cadastrar_item(
        Item("Arduino Uno R3", estoque_minimo=3, categoria=microcontroladores, local=armario_1),
        coord, quantidade_inicial=8,
    )
    inv.cadastrar_item(
        Item("ESP32 DevKit", estoque_minimo=3, categoria=microcontroladores, local=armario_1),
        coord, quantidade_inicial=2,  # crítico
    )
    inv.cadastrar_item(
        Item("Multímetro digital", estoque_minimo=2, categoria=ferramentas, local=bancada),
        coord, quantidade_inicial=5,
    )
    inv.cadastrar_item(
        Item("Jumper macho-macho (40un)", estoque_minimo=10, categoria=cabos, local=gaveta_b3),
        coord, quantidade_inicial=25,
    )

    return inv
