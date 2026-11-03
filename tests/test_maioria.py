import math

import pytest

from dados import CONTA_SUSPEITA, Cartao, TestadorEquivalencia, gerar_cartoes
from maioria import conta_majoritaria, maioria_forca_bruta


def _resolver(funcao, cartoes):
    testador = TestadorEquivalencia()
    return funcao(cartoes, testador), testador.chamadas


def test_lista_vazia_nao_tem_maioria():
    assert conta_majoritaria([], TestadorEquivalencia()) is None
    assert maioria_forca_bruta([], TestadorEquivalencia()) is None


def test_um_cartao_e_maioria_sozinho():
    cartao = Cartao(0, conta=5)
    assert conta_majoritaria([cartao], TestadorEquivalencia()) == (cartao, 1)


def test_todos_da_mesma_conta():
    cartoes = [Cartao(i, conta=3) for i in range(17)]
    representante, quantidade = conta_majoritaria(cartoes, TestadorEquivalencia())
    assert representante.conta == 3
    assert quantidade == 17


@pytest.mark.parametrize("n", [2, 10, 100])
def test_exatamente_metade_nao_e_maioria(n):
    # n/2 cartões na conta 0 e cada um dos outros numa conta própria
    cartoes = [Cartao(i, conta=0 if i < n // 2 else i + 1) for i in range(n)]
    assert conta_majoritaria(cartoes, TestadorEquivalencia()) is None


@pytest.mark.parametrize("n", [2, 10, 100])
def test_metade_mais_um_e_maioria(n):
    cartoes = [Cartao(i, conta=0 if i <= n // 2 else i + 1) for i in range(n)]
    representante, quantidade = conta_majoritaria(cartoes, TestadorEquivalencia())
    assert representante.conta == 0
    assert quantidade == n // 2 + 1


def test_contas_todas_diferentes_nao_tem_maioria():
    cartoes = [Cartao(i, conta=i) for i in range(50)]
    assert conta_majoritaria(cartoes, TestadorEquivalencia()) is None


def test_maioria_concentrada_numa_metade_so():
    # A conta 0 ocupa toda a metade direita e nada da esquerda: ainda é maioria
    cartoes = [Cartao(i, conta=i + 1) for i in range(4)] + [Cartao(4 + i, conta=0) for i in range(5)]
    representante, quantidade = conta_majoritaria(cartoes, TestadorEquivalencia())
    assert (representante.conta, quantidade) == (0, 5)


@pytest.mark.parametrize("fracao", [0.3, 0.5, 0.51, 0.7, 1.0])
@pytest.mark.parametrize("semente", [1, 2, 3])
def test_igual_a_forca_bruta(fracao, semente):
    for n in range(1, 81):
        cartoes = gerar_cartoes(n, fracao_suspeita=fracao, semente=semente)
        dc, _ = _resolver(conta_majoritaria, cartoes)
        bruta, _ = _resolver(maioria_forca_bruta, cartoes)
        if bruta is None:
            assert dc is None
        else:
            assert dc is not None
            assert TestadorEquivalencia()(dc[0], bruta[0])  # mesma conta
            assert dc[1] == bruta[1]


def test_encontra_a_conta_suspeita_nos_dados_gerados():
    representante, quantidade = conta_majoritaria(gerar_cartoes(1001), TestadorEquivalencia())
    assert representante.conta == CONTA_SUSPEITA
    assert quantidade == round(1001 * 0.6)


def test_numero_de_chamadas_e_n_log_n():
    n = 1000
    cartoes = gerar_cartoes(n)
    _, chamadas_dc = _resolver(conta_majoritaria, cartoes)
    _, chamadas_bruta = _resolver(maioria_forca_bruta, cartoes)

    limite = 2 * n * math.ceil(math.log2(n)) + 2 * n
    assert chamadas_dc <= limite
    assert chamadas_bruta == n * n
    assert chamadas_bruta > 10 * limite
