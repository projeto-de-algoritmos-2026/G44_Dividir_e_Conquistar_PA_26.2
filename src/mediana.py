"""Mediana das medianas: seleção do k-ésimo menor valor em tempo linear.

Aplicação: mediana e MAD (mediana dos desvios absolutos) dos valores das
transações, que não são puxados pelas fraudes como a média e o desvio padrão.
"""

LIMIAR_ATIPICO = 3.5


def selecionar(valores, k):
    """k-ésimo menor valor (k começa em 0) em O(n) no pior caso."""
    raise NotImplementedError


def mediana(valores):
    """Valor do meio (n ímpar) ou média dos dois do meio (n par). ValueError se vazia."""
    raise NotImplementedError


def desvio_absoluto_mediano(valores):
    """MAD: mediana de |v - mediana(valores)|. Continua O(n)."""
    raise NotImplementedError


def transacoes_atipicas(transacoes, limiar=LIMIAR_ATIPICO):
    """Lista de (transacao, escore) com |escore robusto| > limiar, do maior para o menor |escore|.

    Escore robusto: 0.6745 · (valor - mediana) / MAD.
    """
    raise NotImplementedError
