import csv

from benchmark import COLUNAS, executar_benchmark, medir, salvar_csv, salvar_grafico


def test_medir_devolve_tempo_positivo():
    assert medir(lambda: sum(range(1000)), repeticoes=3) > 0


def test_benchmark_pequeno_gera_csv_e_grafico(tmp_path, capsys):
    resultados = executar_benchmark(tamanhos=[100, 200], repeticoes=1)
    assert [linha["n"] for linha in resultados] == [100, 200]
    assert resultados[0]["maioria_bruta_chamadas"] == 100 * 100
    assert resultados[0]["maioria_dc_chamadas"] < resultados[0]["maioria_bruta_chamadas"]

    caminho_csv = tmp_path / "resultados.csv"
    salvar_csv(resultados, caminho_csv)
    with open(caminho_csv, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert list(linhas[0]) == COLUNAS
    assert len(linhas) == 2

    caminho_grafico = tmp_path / "resultados.png"
    salvar_grafico(resultados, caminho_grafico)
    assert caminho_grafico.stat().st_size > 0
