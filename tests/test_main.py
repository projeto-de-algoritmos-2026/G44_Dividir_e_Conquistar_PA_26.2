from dados import CONTA_SUSPEITA, FRAUDE_MINIMA, gerar_cartoes, gerar_transacoes
from main import analisar, executar


def test_analisar_encontra_as_tres_fraudes_plantadas():
    cartoes = gerar_cartoes(201)
    transacoes = gerar_transacoes(1000)
    resultado = analisar(cartoes, transacoes)

    # Aqui o teste pode ler .conta: é só conferência do resultado.
    representante, quantidade = resultado["maioria"]
    assert representante.conta == CONTA_SUSPEITA
    assert quantidade == round(201 * 0.6)

    a, b, _ = resultado["duplicada"]
    assert (a.cartao_id, a.valor) == (b.cartao_id, b.valor)
    assert resultado["suspeita_duplicada"]

    atipicas = [t for t, _ in resultado["atipicas"]]
    assert all(t in atipicas for t in transacoes if t.valor >= FRAUDE_MINIMA)


def test_dividir_e_conquistar_chama_menos_o_testador():
    resultado = analisar(gerar_cartoes(201), gerar_transacoes(300))
    assert resultado["chamadas_dc"] < resultado["chamadas_forca_bruta"]


def test_media_e_puxada_pelas_fraudes_e_a_mediana_nao():
    resultado = analisar(gerar_cartoes(11), gerar_transacoes(1000))
    assert resultado["media"] - resultado["mediana"] > 50
    assert resultado["desvio_padrao"] > 10 * resultado["mad"]


def test_executar_imprime_as_quatro_secoes(capsys):
    executar(n_cartoes=201, n_transacoes=300)
    saida = capsys.readouterr().out
    for titulo in ("1. Dados carregados", "2. Cartões apreendidos", "3. Cobrança duplicada",
                   "4. Valores atípicos"):
        assert titulo in saida
    assert "mais da metade" in saida
