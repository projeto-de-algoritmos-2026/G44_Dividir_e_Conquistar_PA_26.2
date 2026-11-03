"""Par de pontos mais próximo por dividir e conquistar (Kleinberg & Tardos, seção 5.4).

Aplicação: cada transação vira o ponto (minuto, valor); a cobrança duplicada
é o par de pontos mais próximo.
"""

from math import hypot, inf


def _distancia(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])


def _melhor(a, b):
    """Entre dois candidatos (distância, i, j), fica com o de menor distância."""
    return a if a[0] <= b[0] else b


def _mesclar_por_y(esquerda, direita):
    """Merge de duas listas já ordenadas por y, em O(n)."""
    mesclados = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i][1] <= direita[j][1]:
            mesclados.append(esquerda[i])
            i += 1
        else:
            mesclados.append(direita[j])
            j += 1
    mesclados.extend(esquerda[i:])
    mesclados.extend(direita[j:])
    return mesclados


def _recursivo(por_x):
    """Recebe pontos (x, y, indice) ordenados por x.

    Devolve o melhor par (distância, i, j) e os mesmos pontos ordenados por y.
    """
    n = len(por_x)
    if n <= 3:
        melhor = (inf, -1, -1)
        for a in range(n):
            for b in range(a + 1, n):
                p, q = por_x[a], por_x[b]
                melhor = _melhor(melhor, (_distancia(p, q), p[2], q[2]))
        return melhor, sorted(por_x, key=lambda p: p[1])

    # Dividir pela linha vertical x = x_linha: metade dos pontos de cada lado.
    meio = n // 2
    x_linha = por_x[meio][0]
    melhor_esquerda, esquerda_y = _recursivo(por_x[:meio])
    melhor_direita, direita_y = _recursivo(por_x[meio:])
    melhor = _melhor(melhor_esquerda, melhor_direita)

    # Cada metade já volta ordenada por y; o merge mantém isso em O(n) em vez
    # de reordenar a faixa a cada nível, o que daria O(n log² n).
    por_y = _mesclar_por_y(esquerda_y, direita_y)

    # Combinar: um par que cruza a linha com distância < δ tem os dois pontos
    # a menos de δ da linha. Na faixa, em ordem de y, cada ponto só precisa ser
    # comparado com os seguintes enquanto a diferença em y for menor que δ;
    # pelo argumento das caixas δ/2 × δ/2, são no máximo 7 vizinhos.
    delta = melhor[0]
    faixa = [p for p in por_y if abs(p[0] - x_linha) < delta]
    for a, p in enumerate(faixa):
        b = a + 1
        while b < len(faixa) and faixa[b][1] - p[1] < melhor[0]:
            q = faixa[b]
            melhor = _melhor(melhor, (_distancia(p, q), p[2], q[2]))
            b += 1

    return melhor, por_y


def par_mais_proximo(pontos):
    """Devolve (i, j, distancia) do par mais próximo, com i < j índices em pontos.

    pontos é uma lista de (x, y). O(n log n). ValueError com menos de 2 pontos.
    """
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")

    # Ordena por x uma única vez, guardando o índice original de cada ponto.
    por_x = sorted((x, y, indice) for indice, (x, y) in enumerate(pontos))
    (distancia, i, j), _ = _recursivo(por_x)
    return min(i, j), max(i, j), distancia


def par_mais_proximo_forca_bruta(pontos):
    """Mesmo resultado de par_mais_proximo comparando todos os pares, O(n²).

    Usada só nos testes (como oráculo) e no benchmark.
    """
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")

    melhor = (inf, -1, -1)
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            melhor = _melhor(melhor, (_distancia(pontos[i], pontos[j]), i, j))
    distancia, i, j = melhor
    return i, j, distancia


def cobranca_duplicada(transacoes):
    """Devolve (transacao_a, transacao_b, distancia) do par mais próximo em (minuto, valor).

    Na distância, 1 minuto equivale a R$ 1: os dois eixos ficam na mesma ordem
    de grandeza para diferenças pequenas, que são as que importam aqui.
    """
    pontos = [(t.minuto, t.valor) for t in transacoes]
    i, j, distancia = par_mais_proximo(pontos)
    return transacoes[i], transacoes[j], distancia
