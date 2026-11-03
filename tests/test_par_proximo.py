import random
from math import isclose, sqrt

import pytest

from dados import ATRASO_DUPLICADA, gerar_transacoes
from par_proximo import cobranca_duplicada, par_mais_proximo, par_mais_proximo_forca_bruta


def _confere_com_forca_bruta(pontos):
    i, j, d = par_mais_proximo(pontos)
    _, _, d_bruta = par_mais_proximo_forca_bruta(pontos)
    assert i < j
    assert isclose(d, d_bruta, abs_tol=1e-12)
    # os índices devolvidos são mesmo um par com essa distância
    (x1, y1), (x2, y2) = pontos[i], pontos[j]
    assert isclose(d, sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2), abs_tol=1e-12)


def test_dois_pontos():
    assert par_mais_proximo([(0, 0), (3, 4)]) == (0, 1, 5.0)


def test_tres_pontos():
    i, j, d = par_mais_proximo([(0, 0), (10, 10), (1, 1)])
    assert (i, j) == (0, 2)
    assert isclose(d, sqrt(2))


def test_pontos_colineares():
    pontos = [(x, 2 * x) for x in (0, 5, 9, 20, 21, 40, 55)]
    i, j, d = par_mais_proximo(pontos)
    assert (i, j) == (3, 4)
    assert isclose(d, sqrt(5))


def test_pontos_repetidos_tem_distancia_zero():
    pontos = [(1, 1), (5, 5), (9, 2), (5, 5), (7, 3)]
    assert par_mais_proximo(pontos) == (1, 3, 0.0)


def test_todos_com_o_mesmo_x():
    pontos = [(4, y) for y in (0, 10, 3, 25, 11.5, 40, 7)]
    i, j, d = par_mais_proximo(pontos)
    assert {pontos[i][1], pontos[j][1]} == {10, 11.5}
    assert isclose(d, 1.5)


def test_par_que_cruza_a_linha_divisoria():
    # Dentro de cada metade os pontos estão longe; o par mais próximo tem um
    # ponto de cada lado da linha.
    esquerda = [(0, 0), (0, 20), (1, 40), (4.9, 10)]
    direita = [(5.1, 10.1), (9, 0), (9, 20), (10, 40)]
    pontos = esquerda + direita
    i, j, d = par_mais_proximo(pontos)
    assert (i, j) == (3, 4)
    assert isclose(d, sqrt(0.2 ** 2 + 0.1 ** 2))


def test_menos_de_dois_pontos_da_erro():
    with pytest.raises(ValueError):
        par_mais_proximo([])
    with pytest.raises(ValueError):
        par_mais_proximo([(1, 2)])


@pytest.mark.parametrize("semente", [1, 2, 3])
def test_igual_a_forca_bruta_com_pontos_reais(semente):
    rng = random.Random(semente)
    for n in range(2, 301, 7):
        _confere_com_forca_bruta([(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)])


@pytest.mark.parametrize("semente", [1, 2, 3])
def test_igual_a_forca_bruta_com_muitos_empates(semente):
    # Grade pequena de inteiros: muitos x iguais, pontos repetidos e pontos
    # exatamente na linha divisória.
    rng = random.Random(semente)
    for n in range(2, 301, 7):
        _confere_com_forca_bruta([(rng.randint(0, 6), rng.randint(0, 30)) for _ in range(n)])


def test_encontra_a_cobranca_duplicada_plantada():
    a, b, d = cobranca_duplicada(gerar_transacoes(1000))
    assert a.cartao_id == b.cartao_id
    assert a.valor == b.valor
    assert round(abs(b.minuto - a.minuto) * 60) == ATRASO_DUPLICADA
    assert isclose(d, ATRASO_DUPLICADA / 60)
