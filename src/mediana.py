"""Mediana das medianas: seleção do k-ésimo menor valor em tempo linear.

Aplicação: mediana e MAD (mediana dos desvios absolutos) dos valores das
transações, que não são puxados pelas fraudes como a média e o desvio padrão.
"""

from math import copysign, inf

LIMIAR_ATIPICO = 3.5
TAMANHO_GRUPO = 5
CONSTANTE_ESCORE = 0.6745  # faz o MAD equivaler ao desvio padrão numa distribuição normal


def _selecionar(valores, k):
    """k-ésimo menor de uma lista não vazia, com 0 <= k < len(valores)."""
    if len(valores) <= TAMANHO_GRUPO:
        return sorted(valores)[k]

    # Grupos de 5 e a mediana de cada um. Ordenar 5 elementos custa uma
    # constante, então este passo é O(n).
    medianas = []
    for inicio in range(0, len(valores), TAMANHO_GRUPO):
        grupo = sorted(valores[inicio:inicio + TAMANHO_GRUPO])
        medianas.append(grupo[(len(grupo) - 1) // 2])

    # Pivô: a mediana das medianas, achada recursivamente em ~n/5 valores.
    # Ela garante que pelo menos 3n/10 valores ficam de cada lado.
    pivo = _selecionar(medianas, (len(medianas) - 1) // 2)

    # Partição em três: os iguais ao pivô ficam à parte, então a recursão
    # sempre diminui, mesmo com muitos valores repetidos.
    menores, maiores = [], []
    iguais = 0
    for valor in valores:
        if valor < pivo:
            menores.append(valor)
        elif valor > pivo:
            maiores.append(valor)
        else:
            iguais += 1

    # Só um dos lados contém a posição k: a recursão desce apenas nele.
    if k < len(menores):
        return _selecionar(menores, k)
    if k < len(menores) + iguais:
        return pivo
    return _selecionar(maiores, k - len(menores) - iguais)


def selecionar(valores, k):
    """k-ésimo menor valor (k começa em 0) em O(n) no pior caso."""
    if not 0 <= k < len(valores):
        raise IndexError(f"k = {k} fora do intervalo [0, {len(valores)})")
    return _selecionar(list(valores), k)


def mediana(valores):
    """Valor do meio (n ímpar) ou média dos dois do meio (n par). ValueError se vazia."""
    n = len(valores)
    if n == 0:
        raise ValueError("a lista não pode ser vazia")
    if n % 2 == 1:
        return selecionar(valores, n // 2)
    return (selecionar(valores, n // 2 - 1) + selecionar(valores, n // 2)) / 2


def desvio_absoluto_mediano(valores):
    """MAD: mediana de |v - mediana(valores)|. São duas seleções lineares, então O(n)."""
    centro = mediana(valores)
    return mediana([abs(valor - centro) for valor in valores])


def transacoes_atipicas(transacoes, limiar=LIMIAR_ATIPICO):
    """Lista de (transacao, escore) com |escore robusto| > limiar, do maior para o menor |escore|.

    Escore robusto: 0.6745 · (valor - mediana) / MAD. Se MAD = 0, toda transação
    com valor diferente da mediana é atípica (escore ±infinito).
    """
    valores = [t.valor for t in transacoes]
    centro = mediana(valores)
    mad = mediana([abs(valor - centro) for valor in valores])

    atipicas = []
    for transacao in transacoes:
        desvio = transacao.valor - centro
        if mad == 0:
            escore = copysign(inf, desvio) if desvio != 0 else 0.0
        else:
            escore = CONSTANTE_ESCORE * desvio / mad
        if abs(escore) > limiar:
            atipicas.append((transacao, escore))

    # Ordena só as atípicas, que são poucas; o cálculo acima continua O(n).
    atipicas.sort(key=lambda par: abs(par[1]), reverse=True)
    return atipicas
