from collections import defaultdict
from math import hypot

import pytest

from dados import (
    ATRASO_DUPLICADA,
    CONTA_SUSPEITA,
    FRAUDE_MINIMA,
    Cartao,
    TestadorEquivalencia,
    gerar_cartoes,
    gerar_transacoes,
)


def _pares_duplicados(transacoes):
    """Pares (mesmo cartão, mesmo valor) separados por exatamente ATRASO_DUPLICADA segundos."""
    grupos = defaultdict(list)
    for t in transacoes:
        grupos[(t.cartao_id, t.valor)].append(t)
    pares = []
    for grupo in grupos.values():
        for i, a in enumerate(grupo):
            for b in grupo[i + 1:]:
                if round(abs(b.minuto - a.minuto) * 60) == ATRASO_DUPLICADA:
                    pares.append((a, b))
    return pares


def test_mesma_semente_gera_os_mesmos_dados():
    assert gerar_cartoes(500) == gerar_cartoes(500)
    assert gerar_transacoes(500) == gerar_transacoes(500)


def test_sementes_diferentes_geram_dados_diferentes():
    assert gerar_cartoes(500, semente=1) != gerar_cartoes(500, semente=2)
    assert gerar_transacoes(500, semente=1) != gerar_transacoes(500, semente=2)


@pytest.mark.parametrize("n", [1, 10, 100, 1001])
def test_tamanho_e_ids_dos_cartoes(n):
    cartoes = gerar_cartoes(n)
    assert len(cartoes) == n
    assert sorted(c.id for c in cartoes) == list(range(n))


@pytest.mark.parametrize("n", [3, 10, 100, 1000])
def test_tamanho_e_ids_das_transacoes(n):
    transacoes = gerar_transacoes(n)
    assert len(transacoes) == n
    assert [t.id for t in transacoes] == list(range(n))


@pytest.mark.parametrize("fracao", [0.0, 0.3, 0.5, 0.51, 0.6, 1.0])
def test_conta_suspeita_tem_a_fracao_pedida(fracao):
    n = 1001
    cartoes = gerar_cartoes(n, fracao_suspeita=fracao)
    assert sum(c.conta == CONTA_SUSPEITA for c in cartoes) == round(n * fracao)


def test_testador_compara_contas_e_conta_chamadas():
    testador = TestadorEquivalencia()
    a, b, c = Cartao(0, conta=7), Cartao(1, conta=7), Cartao(2, conta=8)
    assert testador(a, b)
    assert not testador(a, c)
    assert testador.chamadas == 2


def test_transacoes_em_ordem_de_horario_dentro_do_dia():
    transacoes = gerar_transacoes(1000)
    minutos = [t.minuto for t in transacoes]
    assert minutos == sorted(minutos)
    assert all(0 <= m < 24 * 60 for m in minutos)


@pytest.mark.parametrize("n", [3, 100, 1000, 5000])
def test_existe_exatamente_uma_cobranca_duplicada(n):
    assert len(_pares_duplicados(gerar_transacoes(n))) == 1


@pytest.mark.parametrize("n", [100, 1000])
def test_duplicada_e_o_par_mais_proximo_ate_mil_transacoes(n):
    # Garante que o par mais próximo em (minuto, valor) é a duplicada plantada
    # nos tamanhos usados no main. Varredura simples por minuto, só para conferir.
    transacoes = gerar_transacoes(n)
    melhor = None
    for i, a in enumerate(transacoes):
        for b in transacoes[i + 1:]:
            if melhor and b.minuto - a.minuto >= melhor[0]:
                break
            d = hypot(a.minuto - b.minuto, a.valor - b.valor)
            if melhor is None or d < melhor[0]:
                melhor = (d, a, b)
    assert (melhor[1], melhor[2]) == _pares_duplicados(transacoes)[0]


@pytest.mark.parametrize("n", [3, 100, 1000, 5000])
def test_um_por_cento_de_fraudes_de_valor(n):
    transacoes = gerar_transacoes(n)
    fraudes = [t for t in transacoes if t.valor >= FRAUDE_MINIMA]
    assert len(fraudes) == max(1, round(n * 0.01))
    assert all(t.valor > 0 for t in transacoes)


def test_menos_de_tres_transacoes_da_erro():
    with pytest.raises(ValueError):
        gerar_transacoes(2)
