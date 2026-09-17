# Deslocamento com Obstáculos

Trabalho para a disciplina de **GAAL** (Geometria Analítica e Álgebra Linear) da PUC Minas.

Este projeto aplica conceitos de geometria analítica e álgebra linear em uma **pista de obstáculos** no plano cartesiano: dois competidores disputam quem chega primeiro a um mesmo destino, desviando de obstáculos e movendo-se apenas dentro de um setor circular a cada jogada.

---

## Objetivo

Simular uma corrida entre **dois competidores** até um **mesmo ponto de chegada**, com **obstáculos** no percurso. Cada movimento é limitado a um **setor circular** (raio e ângulo definidos visualmente). O programa deve **validar** cada jogada e **exibir** a nova posição após um movimento válido.

---

## Regras do jogo

1. **Ambiente**:
   - Tudo ocorre em um **plano cartesiano**, com trajetória entre ponto(s) inicial(is) e um **ponto final** comum, passando por uma região com obstáculos.

2. **Competidores**:
   - **Dois jogadores**, cada um com **posição inicial** definida e o **mesmo ponto de chegada**.

3. **Obstáculos**
   - Formas pré-definidas: **triângulos** (3 vértices) e **quadrados** (4 vértices).
   - A cada partida, os obstáculos usados são **escolhidos aleatoriamente** entre os conjuntos pré-definidos.

4. **Jogadas**
   - A cada turno, é gerado um **setor circular** de movimentos possíveis a partir da posição atual.
   - O **raio** e o **ângulo** do setor devem ser apresentados **visualmente**.
   - O jogador escolhe um destino dentro desse setor.
   - O sistema **valida** a jogada (dentro do setor e sem colidir com obstáculos) e **mostra a nova posição**.

5. **Vitória**:
   - Vence quem **chegar primeiro** ao ponto de chegada (critério a detalhar na implementação, por exemplo distância mínima ao destino).

---

## Conceitos de GAAL envolvidos

| Conceito | Uso no projeto |
|----------|----------------|
| Pontos e vetores no plano | Posições dos jogadores, destino e vértices dos obstáculos |
| Distância euclidiana / norma | Limite de **raio** do setor circular |
| Ângulo entre vetores / setor circular | Definição e verificação do **ângulo** do setor de movimento |
| Segmentos e interseção | Trajetória do movimento versus arestas dos obstáculos |
| Polígonos convexos (triângulo, quadrado) | Modelagem dos obstáculos; testes de ponto interior e colisão |

---

## Fluxo de uma partida

1. Definir o plano cartesiano, o **ponto de chegada** e as **posições iniciais** dos dois competidores.
2. **Sortear** quais obstáculos (triângulos e quadrados pré-definidos) entram na pista.
3. **Posicionar** os dois jogadores nas coordenadas iniciais.
4. **Loop de turnos** (alternando competidores):
   - Gerar e desenhar o **setor circular** (raio e ângulo) a partir da posição atual.
   - Receber a jogada (novo ponto ou direção/distância dentro do setor).
   - **Validar** e, se válida, atualizar e **exibir** a nova posição; se inválida, solicitar nova jogada ou tratar conforme regra acordada.
5. Encerrar quando algum competidor **atingir** o ponto de chegada.

---

## Enunciado original (referência)

Transcrição do enunciado do trabalho:

- Elaborar, em um plano cartesiano, uma trajetória a ser executada (ponto inicial e ponto final) com obstáculos no percurso.
- Obstáculos: triângulo (3 pontos) e quadrados (4), previamente definidos, escolhidos aleatoriamente.
- A cada jogada deve ser gerado um setor circular de movimentos possíveis, fixando raio e ângulo visualmente. Validar a jogada e exibir nova posição.
- Dois competidores com posição inicial definida e mesmo ponto de chegada.

A imagem `image.png` no repositório contém o enunciado manuscrito original.