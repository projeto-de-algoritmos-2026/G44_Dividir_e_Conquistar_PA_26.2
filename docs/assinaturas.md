# Assinaturas das funções

Interface de cada módulo em `src/`.

## `src/dados.py`

```python
SEMENTE = 44

@dataclass(frozen=True)
class Cartao:
    id: int
    conta: int   # simula o dado criptografado da tarja: os algoritmos NÃO leem este campo, só o testador

@dataclass(frozen=True)
class Transacao:
    id: int
    cartao_id: int
    minuto: float   # minutos desde 00:00 (0 a 1440), com resolução de 1 segundo
    valor: float    # reais, 2 casas

class TestadorEquivalencia:
    """Equipamento do banco: diz se dois cartões são da mesma conta e conta as chamadas."""
    def __init__(self): self.chamadas = 0
    def __call__(self, a: Cartao, b: Cartao) -> bool: ...

def gerar_cartoes(n: int, fracao_suspeita: float = 0.6, semente: int = SEMENTE) -> list[Cartao]
def gerar_transacoes(n: int, semente: int = SEMENTE) -> list[Transacao]   # n >= 3, em ordem de horário
def salvar_csv(registros, caminho) -> None
```

- `gerar_cartoes`: `round(n · fracao_suspeita)` cartões na conta 0 (suspeita); o resto sorteado entre as contas 1..n; lista embaralhada.
- `gerar_transacoes`: valores normais `max(5.0, gauss(150, 40))`; 1% (pelo menos 1) de fraudes de valor entre R$ 3.000 e R$ 20.000; exatamente uma cobrança duplicada (mesmo cartão e valor, 3 segundos depois). Até n = 1000, a duplicada é o par mais próximo em (minuto, valor).

## `src/maioria.py`

```python
def conta_majoritaria(cartoes, testador) -> tuple[Cartao, int] | None     # (representante, quantidade)
def maioria_forca_bruta(cartoes, testador) -> tuple[Cartao, int] | None
```

## `src/par_proximo.py`

```python
def par_mais_proximo(pontos: list[tuple[float, float]]) -> tuple[int, int, float]   # (i, j, distância), i < j
def par_mais_proximo_forca_bruta(pontos) -> tuple[int, int, float]
def cobranca_duplicada(transacoes) -> tuple[Transacao, Transacao, float]
```

## `src/mediana.py`

```python
LIMIAR_ATIPICO = 3.5
def selecionar(valores, k) -> float                  # k-ésimo menor, k começa em 0
def mediana(valores) -> float
def desvio_absoluto_mediano(valores) -> float        # MAD
def transacoes_atipicas(transacoes, limiar=LIMIAR_ATIPICO) -> list[tuple[Transacao, float]]   # (transação, escore)
```

## `src/main.py`

```python
N_CARTOES = 1001
N_TRANSACOES = 1000
LIMIAR_DUPLICADA = 1.0
def analisar(cartoes, transacoes) -> dict
def executar(n_cartoes=N_CARTOES, n_transacoes=N_TRANSACOES) -> None
```

## `src/benchmark.py`

```python
TAMANHOS = [100, 500, 1_000, 2_000, 5_000, 10_000, 50_000]
LIMITE_FORCA_BRUTA = 5_000
REPETICOES = 3
def medir(funcao, repeticoes=REPETICOES) -> float    # mediana dos tempos
def executar_benchmark() -> list[dict]
def salvar_csv(resultados, caminho) -> None
def salvar_grafico(resultados, caminho) -> None
```
