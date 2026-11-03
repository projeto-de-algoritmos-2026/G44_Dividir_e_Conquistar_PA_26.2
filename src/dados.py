"""Dados sintéticos da investigação de fraude: cartões apreendidos e transações.

Tudo é gerado com semente fixa, então qualquer execução produz os mesmos dados.
Os geradores plantam as fraudes que os algoritmos precisam encontrar:
- uma conta suspeita dona de uma fração dos cartões apreendidos;
- uma cobrança duplicada (mesmo cartão e valor, 3 segundos depois);
- 1% de transações com valor muito acima do normal.
"""

import csv
import os
import random
from dataclasses import asdict, dataclass

SEMENTE = 44
PASTA_DADOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

CONTA_SUSPEITA = 0
CARTOES_NA_MAQUININHA = 200          # cartões distintos que passam na maquininha no dia
SEGUNDOS_NO_DIA = 24 * 60 * 60
ATRASO_DUPLICADA = 3                 # segundos entre a cobrança original e a duplicada
FRACAO_FRAUDE_VALOR = 0.01
VALOR_MEDIO, DESVIO_VALOR, VALOR_MINIMO = 150, 40, 5.0
FRAUDE_MINIMA, FRAUDE_MAXIMA = 3_000, 20_000


@dataclass(frozen=True)
class Cartao:
    id: int
    conta: int  # simula o dado criptografado da tarja: os algoritmos NÃO leem este campo, só o testador


@dataclass(frozen=True)
class Transacao:
    id: int
    cartao_id: int
    minuto: float  # minutos desde 00:00 (0 a 1440), com resolução de 1 segundo
    valor: float   # reais, 2 casas


class TestadorEquivalencia:
    """Equipamento do banco: diz se dois cartões são da mesma conta e conta as chamadas."""

    __test__ = False  # o nome começa com "Test", então o pytest tentaria coletá-la como teste

    def __init__(self):
        self.chamadas = 0

    def __call__(self, a, b):
        self.chamadas += 1
        return a.conta == b.conta


def gerar_cartoes(n, fracao_suspeita=0.6, semente=SEMENTE):
    """n cartões apreendidos; round(n · fracao_suspeita) deles são da conta suspeita (0).

    Os demais se espalham ao acaso entre as contas 1..n, então, salvo para n
    muito pequeno, só a conta suspeita pode ter maioria (> n/2).
    """
    rng = random.Random(semente)
    n_suspeita = round(n * fracao_suspeita)
    contas = [CONTA_SUSPEITA] * n_suspeita + [rng.randint(1, n) for _ in range(n - n_suspeita)]
    rng.shuffle(contas)
    return [Cartao(i, conta) for i, conta in enumerate(contas)]


def gerar_transacoes(n, semente=SEMENTE):
    """n transações de uma maquininha num dia, em ordem de horário.

    Inclui exatamente uma cobrança duplicada e 1% (pelo menos 1) de fraudes de valor.
    """
    if n < 3:
        raise ValueError("são necessárias pelo menos 3 transações (normal, duplicada e fraude)")

    rng = random.Random(semente)
    n_fraudes = max(1, round(n * FRACAO_FRAUDE_VALOR))
    n_normais = n - n_fraudes - 1  # -1: a cópia duplicada

    # Cada registro é (cartão, segundo do dia, valor). Trabalhar em segundos
    # inteiros mantém o atraso da duplicada exato, sem erro de ponto flutuante.
    registros = []
    for _ in range(n_normais):
        valor = max(VALOR_MINIMO, round(rng.gauss(VALOR_MEDIO, DESVIO_VALOR), 2))
        registros.append((rng.randrange(CARTOES_NA_MAQUININHA), rng.randrange(SEGUNDOS_NO_DIA), valor))

    candidatas = [r for r in registros if r[1] + ATRASO_DUPLICADA < SEGUNDOS_NO_DIA]
    cartao, segundo, valor = rng.choice(candidatas)
    registros.append((cartao, segundo + ATRASO_DUPLICADA, valor))

    for _ in range(n_fraudes):
        valor = round(rng.uniform(FRAUDE_MINIMA, FRAUDE_MAXIMA), 2)
        registros.append((rng.randrange(CARTOES_NA_MAQUININHA), rng.randrange(SEGUNDOS_NO_DIA), valor))

    registros.sort(key=lambda r: r[1])
    return [Transacao(i, cartao, segundo / 60, valor)
            for i, (cartao, segundo, valor) in enumerate(registros)]


def salvar_csv(registros, caminho):
    """Grava uma lista de dataclasses (Cartao ou Transacao) em CSV."""
    linhas = [asdict(r) for r in registros]
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    os.makedirs(PASTA_DADOS, exist_ok=True)
    for n in (100, 1000):
        salvar_csv(gerar_cartoes(n), os.path.join(PASTA_DADOS, f"cartoes_n{n}.csv"))
        salvar_csv(gerar_transacoes(n), os.path.join(PASTA_DADOS, f"transacoes_n{n}.csv"))
        print(f"n = {n}: data/cartoes_n{n}.csv e data/transacoes_n{n}.csv gravados")
