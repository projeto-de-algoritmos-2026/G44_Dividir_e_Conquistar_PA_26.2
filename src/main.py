"""Executa a investigação completa do detector de fraude bancária."""

N_CARTOES = 1001
N_TRANSACOES = 1000  # acima de ~5000, pares aleatórios começam a ficar mais próximos que a duplicada
LIMIAR_DUPLICADA = 1.0  # distância em (minuto, valor) abaixo da qual a cobrança é suspeita


def analisar(cartoes, transacoes):
    """Roda os três algoritmos e devolve um dicionário com os resultados (sem imprimir)."""
    raise NotImplementedError


def executar(n_cartoes=N_CARTOES, n_transacoes=N_TRANSACOES):
    """Gera os dados com a semente fixa e imprime o relatório da investigação."""
    raise NotImplementedError


if __name__ == "__main__":
    executar()
