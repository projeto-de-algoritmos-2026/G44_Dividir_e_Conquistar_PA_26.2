"""Maioria por dividir e conquistar (Kleinberg & Tardos, cap. 5, exercício 3).

Entre n cartões apreendidos, existe uma conta com mais de n/2 cartões? A conta
não pode ser lida: a única operação permitida é o testador de equivalência,
que diz se dois cartões são da mesma conta. Objetivo: O(n log n) chamadas.
"""


def conta_majoritaria(cartoes, testador):
    """Devolve (representante, quantidade) da conta com mais de n/2 cartões, ou None.

    Dividir e conquistar, com O(n log n) chamadas ao testador.
    """
    raise NotImplementedError


def maioria_forca_bruta(cartoes, testador):
    """Mesmo resultado de conta_majoritaria, com O(n²) chamadas ao testador.

    Usada só nos testes (como oráculo) e no benchmark.
    """
    raise NotImplementedError
