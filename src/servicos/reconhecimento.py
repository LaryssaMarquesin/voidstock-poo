"""Reconhecimento de itens por imagem (IA).

Demonstra: ABSTRAÇÃO de um serviço externo atrás de uma interface OO. O
`Reconhecedor` é abstrato; `ReconhecedorGemini` implementa a chamada à API
oficial do Google Gemini. Trocar de provedor de IA não afeta o resto do app
— basta outra implementação de `Reconhecedor`.

É o "coração" do projeto: o usuário fotografa um componente e o sistema
sugere nome, categoria e descrição automaticamente.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass

CATEGORIAS_VALIDAS = [
    "Componentes Eletrônicos", "Sensores", "Atuadores", "Cabos",
    "Ferramentas", "Mecânica", "Microcontroladores", "Outros",
]

_PROMPT = (
    "Você identifica componentes técnicos (eletrônica, mecânica, ferramentas de "
    "laboratório). Responda SEMPRE em JSON estrito no formato "
    '{"nome":"string curta","categoria":"string","descricao":"string"}. '
    "Categoria deve ser uma de: " + ", ".join(CATEGORIAS_VALIDAS) + ". "
    "Sem texto fora do JSON."
)


@dataclass
class ItemReconhecido:
    nome: str
    categoria: str
    descricao: str


class ErroReconhecimento(Exception):
    """Erro amigável para exibir ao usuário."""


class Reconhecedor(ABC):
    """Contrato de um serviço de reconhecimento de imagem."""

    @abstractmethod
    def identificar(self, data_url: str) -> ItemReconhecido: ...


class ReconhecedorGemini(Reconhecedor):
    """Implementação usando a API oficial do Google Gemini.

    Tenta uma lista de modelos em ordem: o primeiro é o mais estável; se ele
    estiver sobrecarregado (503), cai para o próximo automaticamente.
    """

    MODELOS = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")

    @property
    def disponivel(self) -> bool:
        return bool(self._api_key)

    def identificar(self, data_url: str) -> ItemReconhecido:
        if not self._api_key:
            raise ErroReconhecimento("Chave de IA ausente (defina GEMINI_API_KEY).")

        match = re.match(r"^data:(.+?);base64,(.+)$", data_url, re.S)
        if not match:
            raise ErroReconhecimento("Formato de imagem inválido.")
        mime_type, base64_data = match.group(1), match.group(2)

        corpo = {
            "system_instruction": {"parts": [{"text": _PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "Identifique este item de laboratório e responda em JSON."},
                        {"inline_data": {"mime_type": mime_type, "data": base64_data}},
                    ],
                }
            ],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        dados_req = json.dumps(corpo).encode()
        resultado = None
        ultimo_erro: ErroReconhecimento | None = None
        for modelo in self.MODELOS:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{modelo}:generateContent"
            )
            try:
                resultado = self._chamar_com_retry(url, dados_req)
                break
            except ErroReconhecimento as e:
                ultimo_erro = e
                print(f"[IA] modelo {modelo} falhou: {e}", file=sys.stderr)
                continue
        if resultado is None:
            raise ultimo_erro or ErroReconhecimento("Falha no reconhecimento.")

        texto = (
            resultado.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "{}")
        )
        try:
            dados = json.loads(texto)
        except json.JSONDecodeError:
            dados = {}
        return ItemReconhecido(
            nome=dados.get("nome", ""),
            categoria=dados.get("categoria", ""),
            descricao=dados.get("descricao", ""),
        )

    def _chamar_com_retry(self, url: str, corpo: bytes, tentativas: int = 3) -> dict:
        """Chama o Gemini com retry em limite (429) e sobrecarga (500/503)."""
        ultimo = ""
        for n in range(tentativas):
            req = urllib.request.Request(
                url, data=corpo,
                headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                detalhe = e.read().decode(errors="ignore")[:300]
                print(f"[IA] HTTP {e.code}: {detalhe}", file=sys.stderr)
                ultimo = f"HTTP {e.code}"
                if e.code in (429, 500, 503) and n < tentativas - 1:
                    time.sleep(2 * (n + 1))  # backoff: 2s, 4s
                    continue
                if e.code == 429:
                    raise ErroReconhecimento(
                        "Limite de requisições da IA atingido. Aguarde ~30s e tente de novo."
                    )
                if e.code in (500, 503):
                    raise ErroReconhecimento(
                        "Serviço de IA sobrecarregado no momento. Tente novamente em instantes."
                    )
                if e.code in (400, 403):
                    raise ErroReconhecimento(
                        "IA recusou a requisição (chave inválida, sem cota ou imagem não suportada)."
                    )
                raise ErroReconhecimento(f"Falha no reconhecimento ({ultimo}). Tente novamente.")
            except urllib.error.URLError as e:
                print(f"[IA] URLError: {e}", file=sys.stderr)
                ultimo = "conexão"
                if n < tentativas - 1:
                    time.sleep(2 * (n + 1))
                    continue
                raise ErroReconhecimento("Não foi possível contatar o serviço de IA.")
        raise ErroReconhecimento(f"Falha no reconhecimento ({ultimo}).")
