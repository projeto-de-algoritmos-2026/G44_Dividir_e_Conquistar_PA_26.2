"""Par de pontos mais próximo por dividir e conquistar (Kleinberg & Tardos, seção 5.4).

Aplicação: cada transação vira o ponto (minuto, valor); a cobrança duplicada
é o par de pontos mais próximo.
"""


def par_mais_proximo(pontos):
    """Devolve (i, j, distancia) do par mais próximo, com i < j índices em pontos.

    pontos é uma lista de (x, y). O(n log n). ValueError com menos de 2 pontos.
    """
    raise NotImplementedError


def par_mais_proximo_forca_bruta(pontos):
    """Mesmo resultado de par_mais_proximo comparando todos os pares, O(n²).

    Usada só nos testes (como oráculo) e no benchmark.
    """
    raise NotImplementedError


def cobranca_duplicada(transacoes):
    """Devolve (transacao_a, transacao_b, distancia) do par mais próximo em (minuto, valor)."""
    raise NotImplementedError
