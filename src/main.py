"""Executa a investigação completa do detector de fraude bancária."""

from math import sqrt

from dados import SEMENTE, TestadorEquivalencia, gerar_cartoes, gerar_transacoes
from maioria import conta_majoritaria, maioria_forca_bruta
from mediana import LIMIAR_ATIPICO, desvio_absoluto_mediano, mediana, transacoes_atipicas
from par_proximo import cobranca_duplicada

N_CARTOES = 1001
N_TRANSACOES = 1000  # acima de ~5000, pares aleatórios começam a ficar mais próximos que a duplicada
LIMIAR_DUPLICADA = 1.0  # distância em (minuto, valor) abaixo da qual a cobrança é suspeita
ATIPICAS_EXIBIDAS = 5


def analisar(cartoes, transacoes):
    """Roda os três algoritmos e devolve um dicionário com os resultados (sem imprimir)."""
    testador_dc = TestadorEquivalencia()
    maioria = conta_majoritaria(cartoes, testador_dc)
    # A força bruta roda só para comparar o número de chamadas ao testador.
    testador_bruta = TestadorEquivalencia()
    maioria_forca_bruta(cartoes, testador_bruta)

    duplicada = cobranca_duplicada(transacoes)

    # Média e desvio padrão entram só como contraste com mediana e MAD.
    valores = [t.valor for t in transacoes]
    media = sum(valores) / len(valores)
    desvio_padrao = sqrt(sum((v - media) ** 2 for v in valores) / len(valores))

    return {
        "maioria": maioria,
        "chamadas_dc": testador_dc.chamadas,
        "chamadas_forca_bruta": testador_bruta.chamadas,
        "duplicada": duplicada,
        "suspeita_duplicada": duplicada[2] <= LIMIAR_DUPLICADA,
        "media": media,
        "desvio_padrao": desvio_padrao,
        "mediana": mediana(valores),
        "mad": desvio_absoluto_mediano(valores),
        "atipicas": transacoes_atipicas(transacoes),
    }


def _inteiro(n):
    return f"{n:,}".replace(",", ".")


def _decimal(valor, casas):
    return f"{valor:.{casas}f}".replace(".", ",")


def _reais(valor):
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def _horario(minuto):
    segundos = round(minuto * 60)
    return f"{segundos // 3600:02d}:{segundos // 60 % 60:02d}:{segundos % 60:02d}"


def _descrever(transacao):
    return (f"Transação {transacao.id}: cartão {transacao.cartao_id}, "
            f"{_horario(transacao.minuto)}, {_reais(transacao.valor)}")


def executar(n_cartoes=N_CARTOES, n_transacoes=N_TRANSACOES):
    """Gera os dados com a semente fixa e imprime o relatório da investigação."""
    cartoes = gerar_cartoes(n_cartoes)
    transacoes = gerar_transacoes(n_transacoes)
    resultado = analisar(cartoes, transacoes)

    print("=== Detector de Fraude Bancária ===")

    print("\n1. Dados carregados")
    print(f"   {_inteiro(n_cartoes)} cartões apreendidos e {_inteiro(n_transacoes)} "
          f"transações da maquininha (semente {SEMENTE})")

    print("\n2. Cartões apreendidos: maioria por dividir e conquistar")
    if resultado["maioria"] is None:
        print("   Nenhuma conta tem mais da metade dos cartões")
    else:
        # A conta não pode ser lida: ela é identificada pelo cartão representante.
        representante, quantidade = resultado["maioria"]
        print(f"   A conta do cartão {representante.id} tem {_inteiro(quantidade)} dos "
              f"{_inteiro(n_cartoes)} cartões ({_decimal(100 * quantidade / n_cartoes, 1)}%): "
              f"mais da metade")
    print(f"   Chamadas ao testador: {_inteiro(resultado['chamadas_dc'])} (dividir e conquistar) "
          f"x {_inteiro(resultado['chamadas_forca_bruta'])} (força bruta)")

    print("\n3. Cobrança duplicada: par de pontos mais próximo")
    transacao_a, transacao_b, distancia = resultado["duplicada"]
    print(f"   {_descrever(transacao_a)}")
    print(f"   {_descrever(transacao_b)}")
    veredito = "suspeita de cobrança duplicada" if resultado["suspeita_duplicada"] else "sem suspeita"
    print(f"   Distância = {_decimal(distancia, 3)} ({veredito})")

    print("\n4. Valores atípicos: mediana das medianas + MAD")
    print(f"   Média = {_reais(resultado['media'])} e desvio padrão = "
          f"{_reais(resultado['desvio_padrao'])} (puxados pelas fraudes)")
    print(f"   Mediana = {_reais(resultado['mediana'])} e MAD = {_reais(resultado['mad'])}")
    atipicas = resultado["atipicas"]
    print(f"   {len(atipicas)} transações atípicas (|escore| > {_decimal(LIMIAR_ATIPICO, 1)}). "
          f"As {min(ATIPICAS_EXIBIDAS, len(atipicas))} maiores:")
    for transacao, escore in atipicas[:ATIPICAS_EXIBIDAS]:
        print(f"     {_descrever(transacao)}, escore {_decimal(escore, 1)}")


if __name__ == "__main__":
    executar()
