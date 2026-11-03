"""Maioria por dividir e conquistar (Kleinberg & Tardos, cap. 5, exercício 3).

Entre n cartões apreendidos, existe uma conta com mais de n/2 cartões? A conta
não pode ser lida: a única operação permitida é o testador de equivalência,
que diz se dois cartões são da mesma conta. Sem ordem nem hash, a pergunta é
resolvida com O(n log n) chamadas ao testador.
"""


def _contar_equivalentes(candidato, cartoes, testador):
    return sum(1 for cartao in cartoes if testador(candidato, cartao))


def _maioria(cartoes, testador):
    n = len(cartoes)
    if n == 0:
        return None
    if n == 1:
        return cartoes[0], 1

    # Dividir ao meio e achar o candidato de cada metade. Se uma conta tem
    # maioria na lista inteira, ela tem maioria em pelo menos uma das metades:
    # com <= metade dos cartões em cada uma, teria <= n/2 no total.
    meio = n // 2
    candidatos = []
    for metade in (cartoes[:meio], cartoes[meio:]):
        resultado = _maioria(metade, testador)
        if resultado is not None:
            candidatos.append(resultado[0])

    # Combinar: no máximo 2 candidatos, cada um testado contra os n cartões.
    for candidato in candidatos:
        quantidade = _contar_equivalentes(candidato, cartoes, testador)
        if quantidade > n / 2:
            return candidato, quantidade
    return None


def conta_majoritaria(cartoes, testador):
    """Devolve (representante, quantidade) da conta com mais de n/2 cartões, ou None.

    Dividir e conquistar, com O(n log n) chamadas ao testador.
    """
    return _maioria(list(cartoes), testador)


def maioria_forca_bruta(cartoes, testador):
    """Mesmo resultado de conta_majoritaria, com O(n²) chamadas ao testador.

    Conta os equivalentes de todos os cartões (sem parar cedo), então faz
    sempre n² chamadas. Usada só nos testes (como oráculo) e no benchmark.
    """
    n = len(cartoes)
    resposta = None
    for candidato in cartoes:
        quantidade = _contar_equivalentes(candidato, cartoes, testador)
        if resposta is None and quantidade > n / 2:
            resposta = (candidato, quantidade)
    return resposta
