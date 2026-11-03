"""Experimentos de tempo: dividir e conquistar x força bruta nos três algoritmos.

Gera data/resultados_benchmark.csv e data/resultados_benchmark.png.
"""

TAMANHOS = [100, 500, 1_000, 2_000, 5_000, 10_000, 50_000]
LIMITE_FORCA_BRUTA = 5_000  # acima disso a força bruta O(n²) demora demais
REPETICOES = 3


def medir(funcao, repeticoes=REPETICOES):
    """Mediana dos tempos (em segundos) de repeticoes execuções de funcao()."""
    raise NotImplementedError


def executar_benchmark():
    """Mede os três algoritmos para cada n em TAMANHOS e devolve uma lista de dicionários."""
    raise NotImplementedError


def salvar_csv(resultados, caminho):
    """Grava os resultados do benchmark em CSV."""
    raise NotImplementedError


def salvar_grafico(resultados, caminho):
    """Gráfico log-log de D&C x força bruta, com curvas de referência."""
    raise NotImplementedError


if __name__ == "__main__":
    executar_benchmark()
