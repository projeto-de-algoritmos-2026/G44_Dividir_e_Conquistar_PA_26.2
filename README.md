# Detector de Fraude Bancária com Dividir e Conquistar

## Introdução

Projeto da disciplina de Projeto e Análise de Algoritmos (Trabalho 3: Dividir e Conquistar). O sistema apoia uma investigação de fraude bancária usando três algoritmos de dividir e conquistar: **maioria com testador de equivalência** (Kleinberg & Tardos, cap. 5, exercício 3), **par de pontos mais próximo** e **mediana das medianas**.

## Dupla (G44)

| Nome | Matrícula |
|---|---|
| André Ricardo Meyer de Melo | 231011097 |
| Giovanni Dornelas Ferreira  | 232002664 |

## Problema

Um banco abriu uma investigação e tem dois conjuntos de dados: os **cartões apreendidos** com um suspeito e as **transações de um dia** de uma maquininha. O sistema responde três perguntas, cada uma com um algoritmo:

```
1. Mais da metade dos cartões apreendidos é da MESMA conta?     → MAIORIA POR D&C
2. Existe cobrança duplicada (mesmo valor, quase mesmo horário)? → PAR DE PONTOS MAIS PRÓXIMO
3. Quais transações têm valor fora do padrão?                    → MEDIANA DAS MEDIANAS + MAD
```

Fluxo do sistema:

```
Cartões apreendidos → MAIORIA (só com o testador de equivalência) → conta suspeita
Transações          → PAR MAIS PRÓXIMO em (minuto, valor)         → cobrança duplicada
Transações          → MEDIANA DAS MEDIANAS + MAD                  → valores atípicos
```

Cada algoritmo também tem uma versão de força bruta, usada só nos testes (como oráculo) e no benchmark.

## Entrada

Os dados são gerados por [src/dados.py](src/dados.py) com semente fixa (44), então qualquer execução produz os mesmos dados. Os geradores plantam as fraudes que o sistema precisa encontrar.

| Entidade | Campos | Como é gerada |
|---|---|---|
| **Cartão** | `id`, `conta` | `round(n · fração)` cartões na conta suspeita (0, padrão 60%); o resto sorteado entre as contas 1..n |
| **Transação** | `id`, `cartao_id`, `minuto` (0 a 1440, resolução de 1 s), `valor` (R$) | Valores normais em torno de R$ 150 (gaussiana, desvio 40); 1% de fraudes entre R$ 3.000 e R$ 20.000; exatamente uma cobrança duplicada (mesmo cartão e valor, 3 segundos depois) |

O campo `conta` simula o dado criptografado da tarja: os algoritmos **não** o leem. A única forma de comparar cartões é o `TestadorEquivalencia`, que diz se dois cartões são da mesma conta e conta quantas vezes foi chamado.

Cada algoritmo recebe:

| Algoritmo | Entrada |
|---|---|
| Maioria | Lista de cartões e o testador de equivalência |
| Par mais próximo | Lista de transações, usando `(minuto, valor)` como ponto |
| Mediana das medianas | Lista dos valores das transações |

`python src/dados.py` grava exemplos em `data/cartoes_n{n}.csv` e `data/transacoes_n{n}.csv` (n = 100 e 1000). As assinaturas das funções estão em [docs/assinaturas.md](docs/assinaturas.md).

## Estrutura do repositório

```
G44_Dividir_e_Conquistar_2026.2/
├── src/
│   ├── dados.py         # Cartao, Transacao, TestadorEquivalencia e geradores (semente 44)
│   ├── maioria.py       # maioria por D&C (lista, ex. 3) + força bruta
│   ├── par_proximo.py   # par de pontos mais próximo + força bruta + cobrança duplicada
│   ├── mediana.py       # mediana das medianas, MAD e transações atípicas
│   ├── main.py          # fluxo completo do detector
│   └── benchmark.py     # tempos D&C x força bruta, CSV e gráfico
├── tests/               # um arquivo de teste por módulo
├── data/                # CSVs gerados (não versionados), exceto resultados_benchmark.*
├── docs/
│   └── assinaturas.md
├── requirements.txt
├── pytest.ini
└── README.md
```

## Como instalar

```bash
cd G44_Dividir_e_Conquistar_2026.2
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## Como rodar os testes

```bash
python -m pytest -q
```
