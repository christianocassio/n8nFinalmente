#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de RPA para extração de clientes e disparo para o Webhook do N8N.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Garante compatibilidade de encoding UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env caso exista
load_dotenv()

DEFAULT_REMOTE_URL = (
    "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"
)
LOCAL_FALLBACK_FILE = Path(__file__).resolve().parent.parent / "docs" / "index.html"


def parse_saldo_numerico(saldo_str: str) -> float:
    """Converte string de moeda (ex: 'R$ 12.500,00') para float (12500.0)."""
    try:
        limpo = (
            saldo_str.replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        return float(limpo)
    except Exception:
        return 0.0


def extrair_clientes_de_html(html_content: str) -> List[Dict[str, Any]]:
    """Extrai registros da tabela #clientes do HTML fornecido."""
    soup = BeautifulSoup(html_content, "html.parser")
    linhas = soup.select("#clientes tbody tr")

    clientes: List[Dict[str, Any]] = []

    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) < 4:
            continue

        nome = colunas[0].get_text(strip=True)
        email = colunas[1].get_text(strip=True)
        saldo_formatado = colunas[2].get_text(strip=True)
        perfil = colunas[3].get_text(strip=True)

        cliente = {
            "nome": nome,
            "email": email,
            "saldo": saldo_formatado,
            "saldo_numerico": parse_saldo_numerico(saldo_formatado),
            "perfil": perfil,
        }
        clientes.append(cliente)

    return clientes


def obter_html(url: str, usar_arquivo_local: Optional[str] = None) -> str:
    """Obtém o conteúdo HTML da URL remota ou de um arquivo local."""
    if usar_arquivo_local:
        caminho = Path(usar_arquivo_local)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo local não encontrado: {caminho}")
        print(f"[ARQUIVO] Lendo dados locais: {caminho}")
        return caminho.read_text(encoding="utf-8")

    try:
        print(f"[REDE] Conectando a URL remota: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"[AVISO] Falha ao acessar URL remota ({exc}).")
        if LOCAL_FALLBACK_FILE.exists():
            print(f"[FALLBACK] Usando arquivo local: {LOCAL_FALLBACK_FILE}")
            return LOCAL_FALLBACK_FILE.read_text(encoding="utf-8")
        raise exc


def enviar_para_n8n(webhook_url: str, clientes: List[Dict[str, Any]]) -> bool:
    """Dispara a lista de clientes para o Webhook do N8N via POST."""
    print(f"\n[ENVIO] Disparando {len(clientes)} clientes para o N8N: {webhook_url}")
    payload = {"clientes": clientes}

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        print(f"[STATUS] Codigo HTTP: {response.status_code}")
        if response.ok:
            print("[SUCESSO] Dados enviados com sucesso ao N8N!")
            if response.text:
                print(f"[RESPOSTA] Retorno do workflow: {response.text[:300]}")
            return True
        else:
            print(f"[ERRO] Falha do N8N: {response.text}")
            return False
    except requests.exceptions.RequestException as err:
        print(f"[ERRO] Erro de conexao com o Webhook do N8N: {err}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="RPA: Extrai clientes e envia para o Webhook N8N."
    )
    parser.add_argument(
        "--url",
        default=os.getenv("CLIENTES_URL", DEFAULT_REMOTE_URL),
        help="URL da página web de clientes",
    )
    parser.add_argument(
        "--webhook-url",
        default=os.getenv("N8N_WEBHOOK_URL", ""),
        help="URL do Webhook do N8N",
    )
    parser.add_argument(
        "--local-file",
        default=None,
        help="Caminho para arquivo HTML local de clientes (opcional)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa apenas a extração e exibe os dados sem enviar para o N8N",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Assistente de Investimentos - RPA de Extracao de Clientes")
    print("=" * 60)

    try:
        html = obter_html(args.url, usar_arquivo_local=args.local_file)
        clientes = extrair_clientes_de_html(html)

        print(f"\nTotal de clientes extraidos: {len(clientes)}")
        print("-" * 60)
        for i, c in enumerate(clientes, 1):
            print(
                f"[{i:02d}] {c['nome']:<18} | {c['perfil']:<11} | Saldo: {c['saldo']:<12} | {c['email']}"
            )
        print("-" * 60)

        if args.dry_run:
            print("\n[INFO] Modo --dry-run ativo. Nenhuma requisicao enviada ao N8N.")
            return

        webhook_url = args.webhook_url
        if not webhook_url:
            print("\n[AVISO] N8N_WEBHOOK_URL nao configurada no .env ou via --webhook-url.")
            print("Dica: Crie o workflow no N8N e execute:")
            print("   python rpa/extrair_clientes.py --webhook-url <SUA_URL_DO_N8N>")
            return

        sucesso = enviar_para_n8n(webhook_url, clientes)
        if not sucesso:
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERRO] Falha durante a execucao: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
