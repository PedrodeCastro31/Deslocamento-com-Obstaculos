# Deslocamento com Obstáculos

Trabalho Computacional — **GAAL** (Geometria Analítica e Álgebra Linear) — PUC Minas  
**Professor:** João Ricardo  

Simulação em Python de uma corrida entre **dois competidores** no plano cartesiano $\mathbb{R}^2$ rumo a um **mesmo ponto de chegada**, desviando de **obstáculos poligonais pré-definidos** (triângulos e quadrados sorteados a cada partida) e movendo-se exclusivamente dentro de um **setor circular** exibido e validado a cada turno.

---

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
python main.py
```

Para executar a suíte de validação geométrica e gerar o gráfico de demonstração:

```bash
python validar.py
```

---

## Estrutura

| Arquivo | Função |
|---------|--------|
| `geometria.py` | Pontos e vetores em $\mathbb{R}^2$, norma euclidiana, produto escalar, ângulo entre vetores, determinante $2\times 2$, interseção de segmentos e ponto em polígono convexo |
| `obstaculos.py` | Catálogo pré-definido de triângulos (3 vértices) e quadrados (4 vértices), sorteio por partida e detecção de colisão com segmentos de movimento |
| `partida.py` | Estado da corrida, competidores, geração e validação do setor circular, execução das jogadas e simulação automática |
| `visualizacao.py` | Renderização `matplotlib` do plano cartesiano, obstáculos, trajetórias, chegada e setor circular (raio $R$ e abertura $\theta$) |
| `main.py` | Menu principal (partida interativa passo a passo, simulação automática e demonstração de validações) |
| `validar.py` | Testes determinísticos da álgebra linear, colisões, setor circular e geração de gráfico |
| `graficos/` | PNGs gerados (`simulacao_partida.png`, `turno_atual.png`, `jogada_invalida.png`) |

---

## Conceitos de GAAL aplicados

### 1. Pontos, Vetores e Norma Euclidiana (Raio do Setor e Chegada)
Um deslocamento da posição atual $C = (x_c, y_c)$ até o ponto escolhido $P = (x_p, y_p)$ é representado pelo vetor $\vec{d} = P - C = (x_p - x_c, y_p - y_c)$. O comprimento do movimento é dado pela **norma euclidiana**:

$$\|\vec{d}\| = \sqrt{(x_p - x_c)^2 + (y_p - y_c)^2}$$

- **Limite de raio do setor:** a jogada exige $0 < \|\vec{d}\| \le R$.
- **Critério de chegada:** o competidor vence ao atingir distância $\|\vec{p}_{\text{atual}} - \vec{p}_{\text{chegada}}\| \le r_{\text{chegada}}$.

### 2. Produto Escalar e Ângulo entre Vetores (Abertura do Setor Circular)
O setor circular é orientado pelo vetor direção central $\vec{u}$ (apontando de $C$ ao ponto de chegada) e possui abertura total $\theta$ (meia-abertura $\theta / 2$). Pelo **produto escalar** em $\mathbb{R}^2$:

$$\vec{d} \cdot \vec{u} = d_x u_x + d_y u_y = \|\vec{d}\| \|\vec{u}\| \cos\alpha \implies \alpha = \arccos\left(\frac{\vec{d} \cdot \vec{u}}{\|\vec{d}\| \|\vec{u}\|}\right)$$

O destino pertence à abertura angular do setor se, e somente se, $\alpha \le \frac{\theta}{2}$.

### 3. Determinante $2\times 2$, Interseção de Segmentos e Polígonos Convexos (Colisão)
Dados dois vetores $\vec{u} = (u_x, u_y)$ e $\vec{v} = (v_x, v_y)$, o determinante $2\times 2$:

$$\det[\vec{u}, \vec{v}] = u_x v_y - u_y v_x$$

fornece a orientação relativa no plano (sentido anti-horário quando positivo, horário quando negativo e colinear quando nulo):
- **Ponto no interior de triângulo/quadrado convexo:** um ponto $P$ pertence ao obstáculo convexo de vértices $V_0, \dots, V_{k-1}$ se o determinante $\det(V_{i+1} - V_i, P - V_i)$ mantém o mesmo sinal para todas as arestas.
- **Interseção de segmentos:** o segmento de deslocamento $CP$ atravessa uma aresta $AB$ do obstáculo quando $C$ e $P$ estão em semiplanos opostos de $AB$ e $A$ e $B$ estão em semiplanos opostos de $CP$ (sinais opostos dos determinantes correspondentes).

---

## Modos do programa

1. **Partida interativa (2 competidores)** — sorteia triângulos e quadrados, gera o setor circular a cada turno, aceita coordenadas cartesianas $(x, y)$ ou polares $(r, \theta)$, rejeita jogadas inválidas explicando o motivo e atualiza o gráfico passo a passo.
2. **Simulação automática** — executa uma partida completa entre os 2 competidores desviando dos obstáculos sorteados e salva o painel visual em `graficos/simulacao_partida.png`.
3. **Demonstração de validações (GAAL)** — executa casos de teste explícitos (fora do raio, fora do ângulo, colisão com obstáculo e jogada válida).
