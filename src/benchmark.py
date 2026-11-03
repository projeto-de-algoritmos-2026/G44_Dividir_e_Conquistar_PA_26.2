"""Experimentos de tempo: dividir e conquistar x força bruta nos três algoritmos.

Gera data/resultados_benchmark.csv e data/resultados_benchmark.png.
"""

import csv
import gc
import os
import time
from math import log2

from dados import PASTA_DADOS, TestadorEquivalencia, gerar_cartoes, gerar_transacoes
from maioria import conta_majoritaria, maioria_forca_bruta
from mediana import mediana
from par_proximo import par_mais_proximo, par_mais_proximo_forca_bruta

TAMANHOS = [100, 500, 1_000, 2_000, 5_000, 10_000, 50_000]
LIMITE_FORCA_BRUTA = 5_000  # acima disso a força bruta O(n²) demora demais
REPETICOES = 3

CAMINHO_CSV = os.path.join(PASTA_DADOS, "resultados_benchmark.csv")
CAMINHO_GRAFICO = os.path.join(PASTA_DADOS, "resultados_benchmark.png")

COLUNAS = [
    "n",
    "maioria_dc_s", "maioria_bruta_s", "maioria_dc_chamadas", "maioria_bruta_chamadas",
    "par_dc_s", "par_bruta_s",
    "mediana_dc_s", "mediana_ordenando_s",
]


def medir(funcao, repeticoes=REPETICOES):
    """Menor tempo (em segundos) entre repeticoes execuções de funcao().

    O ruído do sistema só aumenta o tempo, então o mínimo é a estimativa mais
    estável (é o que a documentação do timeit recomenda).
    """
    tempos = []
    for _ in range(repeticoes):
        # Como no timeit: o coletor de lixo desligado tira uma fonte de ruído da medição.
        gc.disable()
        try:
            inicio = time.perf_counter()
            funcao()
            tempos.append(time.perf_counter() - inicio)
        finally:
            gc.enable()
    return min(tempos)


def _chamadas(algoritmo, cartoes):
    testador = TestadorEquivalencia()
    algoritmo(cartoes, testador)
    return testador.chamadas


def _mediana_ordenando(valores):
    """Referência: ordenar tudo (sorted, implementado em C) e pegar o meio."""
    ordenados = sorted(valores)
    n = len(ordenados)
    if n % 2 == 1:
        return ordenados[n // 2]
    return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2


def _formatar(valor):
    if valor is None:
        return "-"
    if isinstance(valor, int):
        return f"{valor:,}".replace(",", ".")
    return f"{valor:.4f}"


def executar_benchmark(tamanhos=TAMANHOS, repeticoes=REPETICOES):
    """Mede os três algoritmos para cada n em tamanhos e devolve uma lista de dicionários."""
    print(" | ".join(f"{coluna:>22}" for coluna in COLUNAS))
    resultados = []
    for n in tamanhos:
        # As entradas são geradas fora da medição.
        cartoes = gerar_cartoes(n)
        transacoes = gerar_transacoes(n)
        pontos = [(t.minuto, t.valor) for t in transacoes]
        valores = [t.valor for t in transacoes]
        com_forca_bruta = n <= LIMITE_FORCA_BRUTA

        linha = {
            "n": n,
            "maioria_dc_s": medir(lambda: conta_majoritaria(cartoes, TestadorEquivalencia()), repeticoes),
            "maioria_bruta_s": None,
            "maioria_dc_chamadas": _chamadas(conta_majoritaria, cartoes),
            "maioria_bruta_chamadas": None,
            "par_dc_s": medir(lambda: par_mais_proximo(pontos), repeticoes),
            "par_bruta_s": None,
            "mediana_dc_s": medir(lambda: mediana(valores), repeticoes),
            "mediana_ordenando_s": medir(lambda: _mediana_ordenando(valores), repeticoes),
        }
        if com_forca_bruta:
            linha["maioria_bruta_s"] = medir(
                lambda: maioria_forca_bruta(cartoes, TestadorEquivalencia()), repeticoes)
            linha["maioria_bruta_chamadas"] = _chamadas(maioria_forca_bruta, cartoes)
            linha["par_bruta_s"] = medir(lambda: par_mais_proximo_forca_bruta(pontos), repeticoes)

        resultados.append(linha)
        print(" | ".join(f"{_formatar(linha[coluna]):>22}" for coluna in COLUNAS), flush=True)
    return resultados


def salvar_csv(resultados, caminho=CAMINHO_CSV):
    """Grava os resultados do benchmark em CSV (força bruta não medida fica vazia)."""
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        for linha in resultados:
            escritor.writerow({coluna: "" if linha[coluna] is None else linha[coluna] for coluna in COLUNAS})


def _referencia(tamanhos, tempo_inicial, crescimento):
    """Curva teórica ancorada no primeiro ponto medido."""
    base = crescimento(tamanhos[0])
    return [tempo_inicial * crescimento(n) / base for n in tamanhos]


def salvar_grafico(resultados, caminho=CAMINHO_GRAFICO):
    """Gráfico log-log de D&C x força bruta, com curvas de referência."""
    import matplotlib
    matplotlib.use("Agg")  # só gera o arquivo, sem abrir janela
    import matplotlib.pyplot as plt

    cor_dc, cor_bruta, cor_referencia = "#2a78d6", "#eb6834", "#898781"
    tinta, grade, fundo = "#52514e", "#e1e0d9", "#fcfcfb"

    n_log_n = lambda n: n * log2(n)
    paineis = [
        ("Maioria (cartões)", "maioria_dc_s", "maioria_bruta_s", "Força bruta", n_log_n, "n log n"),
        ("Par mais próximo (transações)", "par_dc_s", "par_bruta_s", "Força bruta", n_log_n, "n log n"),
        ("Mediana (valores)", "mediana_dc_s", "mediana_ordenando_s", "Ordenando (sorted, em C)",
         lambda n: n, "n"),
    ]

    figura, eixos = plt.subplots(1, 3, figsize=(15, 4.8), facecolor=fundo)
    for eixo, (titulo, chave_dc, chave_outro, nome_outro, crescimento, nome_ref) in zip(eixos, paineis):
        tamanhos = [linha["n"] for linha in resultados]
        tempos_dc = [linha[chave_dc] for linha in resultados]
        medidos = [(linha["n"], linha[chave_outro]) for linha in resultados if linha[chave_outro] is not None]

        eixo.set_facecolor(fundo)
        eixo.plot(tamanhos, _referencia(tamanhos, tempos_dc[0], crescimento),
                  linestyle=":", linewidth=2, color=cor_referencia, label=f"Referência {nome_ref}")
        if chave_outro != "mediana_ordenando_s" and medidos:
            ns = [n for n, _ in medidos]
            eixo.plot(ns, _referencia(ns, medidos[0][1], lambda n: n * n),
                      linestyle="--", linewidth=1.5, color=cor_referencia, label="Referência n²")
        eixo.plot(tamanhos, tempos_dc, marker="o", markersize=7, linewidth=2, color=cor_dc,
                  label="Dividir e conquistar")
        if medidos:
            eixo.plot([n for n, _ in medidos], [t for _, t in medidos], marker="s", markersize=7,
                      linewidth=2, color=cor_bruta, label=nome_outro)

        eixo.set_xscale("log")
        eixo.set_yscale("log")
        eixo.set_title(titulo, color=tinta, fontsize=12)
        eixo.set_xlabel("n (tamanho da entrada)", color=tinta)
        eixo.set_ylabel("tempo (s)", color=tinta)
        eixo.grid(True, which="major", color=grade, linewidth=0.8)
        eixo.tick_params(colors=tinta)
        for borda in eixo.spines.values():
            borda.set_color(grade)
        eixo.legend(frameon=False, fontsize=9, labelcolor=tinta)

    figura.suptitle("Tempo medido (menor de 3 execuções), escala log-log", color=tinta, fontsize=13)
    figura.tight_layout()
    figura.savefig(caminho, dpi=120, facecolor=fundo)
    plt.close(figura)


if __name__ == "__main__":
    os.makedirs(PASTA_DADOS, exist_ok=True)
    resultados = executar_benchmark()
    salvar_csv(resultados)
    salvar_grafico(resultados)
    print(f"\nTabela salva em {CAMINHO_CSV}")
    print(f"Gráfico salvo em {CAMINHO_GRAFICO}")
