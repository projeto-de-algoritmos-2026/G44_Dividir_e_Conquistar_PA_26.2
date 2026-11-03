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

## Análise dos algoritmos

### Maioria por dividir e conquistar (cartões da mesma conta)

- **Problema:** o banco apreendeu n cartões com um suspeito. Cada cartão pertence a uma conta, mas a conta está criptografada na tarja e não pode ser lida. A única operação disponível é o **testador de equivalência**, que recebe dois cartões e diz se são da mesma conta. A pergunta é se existe uma conta com **mais de n/2** cartões, o que indicaria fraude organizada em torno de uma única conta.
- **Por que não dá para ordenar nem usar hash:** as duas técnicas precisam de uma chave comparável (qual conta é "menor", ou um valor para espalhar numa tabela). O testador só responde "igual" ou "diferente". Comparar todos os pares funciona, mas custa n² chamadas. O custo que medimos é justamente o número de chamadas ao testador.
- **Estratégia** ([src/maioria.py](src/maioria.py)):
  - **Dividir:** separar os cartões em duas metades.
  - **Conquistar:** achar recursivamente a conta majoritária de cada metade, se houver. O resultado de cada metade é um *candidato*: um cartão representante.
  - **Combinar:** testar cada candidato (no máximo 2) contra todos os cartões da lista atual. Se algum aparece em mais de n/2 cartões, ele é a resposta; senão, não há maioria.
  - **Casos base:** lista vazia não tem maioria; um cartão sozinho é maioria (1 > 1/2).
- **Por que a resposta sempre está entre os candidatos:** suponha que a conta X tem mais de n/2 cartões no total. Se X tivesse no máximo metade dos cartões em cada metade, teria no máximo ⌊n/2⌋/2 + ⌈n/2⌉/2 = n/2 cartões no total, o que contradiz a hipótese. Logo X é maioria em pelo menos uma metade e volta como candidata dela. O teste no combinar descarta candidatos que são maioria só numa metade.
- **Recorrência:** T(n) = 2T(n/2) + 2n. São duas chamadas recursivas de metade do tamanho, e o combinar faz no máximo 2 candidatos × n chamadas ao testador.
- **Tempo:** pelo Teorema Mestre (a = 2, b = 2, f(n) = Θ(n), caso 2), T(n) = **O(n log n)** chamadas ao testador. Na árvore de recursão, cada um dos ⌈log₂ n⌉ níveis custa no máximo 2n chamadas.
- **Espaço:** O(n) nas sublistas de cada nível, mais a pilha de recursão de profundidade O(log n).
- **Força bruta:** para cada cartão, conta quantos cartões são equivalentes a ele: n × n = **O(n²)** chamadas. Ela é usada só como oráculo nos testes e como comparação de custo.

Chamadas ao testador nos dados gerados (conta suspeita com 60% dos cartões):

| n | Dividir e conquistar | Força bruta (n²) |
|---:|---:|---:|
| 100 | 678 | 10.000 |
| 1.000 | 9.744 | 1.000.000 |
| 10.000 | 134.014 | 100.000.000 |

- **Testes** ([tests/test_maioria.py](tests/test_maioria.py)):
  - lista vazia, um cartão e todos da mesma conta;
  - exatamente n/2 cartões da mesma conta (não é maioria) e n/2 + 1 (é maioria);
  - todas as contas diferentes;
  - maioria concentrada numa única metade;
  - mesmo resultado da força bruta para n de 1 a 80, frações 0,3, 0,5, 0,51, 0,7 e 1,0 e três sementes;
  - a conta suspeita é encontrada nos dados gerados;
  - para n = 1000, no máximo 2n⌈log₂ n⌉ + 2n chamadas, enquanto a força bruta faz n².

### Par de pontos mais próximo (cobrança duplicada)

- **Problema:** uma maquininha registrou n transações num dia. Uma cobrança duplicada (o cliente passou o cartão uma vez e foi cobrado duas) aparece como duas transações com o mesmo valor, registradas com poucos segundos de diferença. Cada transação vira um ponto **(minuto do dia, valor em R$)**, e a cobrança duplicada é o **par de pontos mais próximo**.
- **Escala:** na distância euclidiana, 1 minuto pesa o mesmo que R$ 1. As diferenças que importam são pequenas nos dois eixos (segundos e centavos), então essa escala simples basta. Normalizar pelo mínimo e máximo seria pior, porque as fraudes de valor (até R$ 20.000) esticariam o eixo e esmagariam as diferenças de centavos. Nos dados gerados, a duplicada plantada é o par mais próximo até cerca de 1.000 transações, que é o volume de uma maquininha num dia.
- **Estratégia** ([src/par_proximo.py](src/par_proximo.py)):
  - **Preparar:** ordenar os pontos por x uma única vez, guardando o índice original de cada um. Custa O(n log n).
  - **Dividir:** traçar uma linha vertical x = x_linha com metade dos pontos de cada lado.
  - **Conquistar:** achar recursivamente o par mais próximo de cada metade. Seja δ a menor das duas distâncias.
  - **Combinar:** procurar um par que cruze a linha com distância menor que δ. Só os pontos a menos de δ da linha podem formar esse par (a faixa de largura 2δ). Percorrendo a faixa em ordem de y, cada ponto só precisa ser comparado com os seguintes enquanto a diferença em y for menor que δ.
  - **Casos base:** com até 3 pontos, compara todos os pares.
- **Por que no máximo 7 vizinhos:** divida a faixa em caixas de δ/2 × δ/2. Dois pontos da mesma metade na mesma caixa estariam a menos de δ um do outro, o que contradiz a definição de δ. Logo cada caixa tem no máximo um ponto de cada metade. Um ponto a menos de δ acima de outro está nas duas linhas de caixas seguintes, que somam 8 caixas, então há no máximo 7 vizinhos a examinar. A varredura da faixa custa O(n).
- **Por que devolver a lista ordenada por y:** se cada nível reordenasse a faixa por y, o combinar custaria O(n log n) e o total seria O(n log² n). Em vez disso, cada chamada recursiva também devolve seus pontos ordenados por y, e o combinar faz o **merge** das duas listas em O(n), como no mergesort.
- **Recorrência:** T(n) = 2T(n/2) + O(n): duas metades, mais o merge por y e a varredura da faixa, ambos lineares.
- **Tempo:** pelo Teorema Mestre (caso 2), **O(n log n)**, somando a ordenação inicial por x.
- **Espaço:** O(n) nas listas de cada nível, mais a pilha de recursão de profundidade O(log n).
- **Força bruta:** comparar todos os n(n-1)/2 pares, O(n²). Usada só como oráculo nos testes e como comparação de custo.
- **Resultado nos dados gerados (n = 1000):** transações 11 e 12, ambas do cartão 126, de R$ 148,25, às 00:14:58 e 00:15:01. A distância é 0,05, que corresponde aos 3 segundos entre elas.
- **Testes** ([tests/test_par_proximo.py](tests/test_par_proximo.py)):
  - 2 e 3 pontos;
  - pontos colineares;
  - pontos repetidos (distância 0);
  - todos os pontos com o mesmo x;
  - par que cruza a linha divisória;
  - menos de 2 pontos (erro);
  - mesma distância da força bruta para n de 2 a 300, com pontos reais aleatórios e com uma grade pequena de inteiros, que força x repetidos, pontos iguais e pontos sobre a linha;
  - a cobrança duplicada plantada é encontrada.

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
