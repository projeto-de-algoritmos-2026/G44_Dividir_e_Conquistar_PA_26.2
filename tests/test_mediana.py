import random
from math import inf

import pytest

from dados import FRAUDE_MINIMA, Transacao, gerar_transacoes
from mediana import desvio_absoluto_mediano, mediana, selecionar, transacoes_atipicas


@pytest.mark.parametrize("semente", [1, 2, 3])
def test_selecionar_igual_a_ordenar(semente):
    # sorted aparece só aqui, como oráculo
    rng = random.Random(semente)
    for n in range(1, 501, 13):
        valores = [rng.uniform(-1000, 1000) for _ in range(n)]
        ordenados = sorted(valores)
        for k in {0, n // 2, n - 1, rng.randrange(n)}:
            assert selecionar(valores, k) == ordenados[k]


@pytest.mark.parametrize("semente", [1, 2, 3])
def test_selecionar_com_muitos_repetidos(semente):
    rng = random.Random(semente)
    for n in range(1, 501, 13):
        valores = [rng.randint(0, 5) for _ in range(n)]
        ordenados = sorted(valores)
        for k in range(0, n, max(1, n // 10)):
            assert selecionar(valores, k) == ordenados[k]


def test_todos_iguais():
    assert selecionar([7] * 100, 0) == 7
    assert selecionar([7] * 100, 99) == 7
    assert mediana([7] * 100) == 7


def test_um_elemento():
    assert selecionar([42], 0) == 42
    assert mediana([42]) == 42


def test_lista_ordenada_e_invertida():
    crescente = list(range(1000))
    assert selecionar(crescente, 123) == 123
    assert selecionar(crescente[::-1], 123) == 123


def test_nao_altera_a_lista_original():
    valores = [5, 3, 9, 1, 7, 2, 8, 6, 4]
    copia = list(valores)
    selecionar(valores, 4)
    assert valores == copia


def test_k_fora_do_intervalo_da_erro():
    with pytest.raises(IndexError):
        selecionar([1, 2, 3], 3)
    with pytest.raises(IndexError):
        selecionar([1, 2, 3], -1)


def test_lista_vazia_da_erro():
    with pytest.raises(IndexError):
        selecionar([], 0)
    with pytest.raises(ValueError):
        mediana([])


def test_mediana_impar_e_par():
    assert mediana([9, 1, 5]) == 5
    assert mediana([9, 1, 5, 3]) == 4  # (3 + 5) / 2


def test_mad_de_exemplo_conhecido():
    # mediana 2; desvios [1, 1, 0, 0, 2, 4, 7]; mediana dos desvios 1
    assert desvio_absoluto_mediano([1, 1, 2, 2, 4, 6, 9]) == 1


def test_outlier_puxa_a_media_mas_nao_a_mediana():
    normais = [100, 110, 120, 130, 140]
    com_outlier = normais + [1_000_000]
    media = sum(normais) / len(normais)
    media_com_outlier = sum(com_outlier) / len(com_outlier)
    assert media_com_outlier - media > 100_000
    assert mediana(com_outlier) - mediana(normais) <= 5


def test_marca_as_fraudes_plantadas_e_quase_nada_mais():
    transacoes = gerar_transacoes(1000)
    atipicas = [t for t, _ in transacoes_atipicas(transacoes)]
    fraudes = [t for t in transacoes if t.valor >= FRAUDE_MINIMA]
    assert all(t in atipicas for t in fraudes)
    assert len(atipicas) - len(fraudes) <= 0.01 * len(transacoes)


def test_atipicas_em_ordem_decrescente_de_escore():
    escores = [abs(e) for _, e in transacoes_atipicas(gerar_transacoes(1000))]
    assert escores == sorted(escores, reverse=True)


def test_mad_zero_marca_tudo_que_difere_da_mediana():
    transacoes = [Transacao(i, 0, i, 50.0) for i in range(9)] + [Transacao(9, 0, 9, 80.0)]
    atipicas = transacoes_atipicas(transacoes)
    assert atipicas == [(transacoes[9], inf)]
