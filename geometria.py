from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

EPSILON = 1e-9


@dataclass(frozen=True)
class Ponto:
    """Representa um ponto P = (x, y) no plano cartesiano R^2."""

    x: float
    y: float

    def vetor_ate(self, destino: Ponto) -> Vetor:
        """Retorna o vetor deslocamento v = destino - self."""
        return Vetor(destino.x - self.x, destino.y - self.y)

    def transladar(self, vetor: Vetor) -> Ponto:
        """Retorna o ponto P' = P + v."""
        return Ponto(self.x + vetor.x, self.y + vetor.y)

    def formatar(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"


@dataclass(frozen=True)
class Vetor:
    """Representa um vetor livre v = (x, y) no espaco vetorial R^2."""

    x: float
    y: float

    def norma(self) -> float:
        """Norma euclidiana ||v|| = sqrt(x^2 + y^2)."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def escalar(self, fator: float) -> Vetor:
        """Multiplicacao por escalar: c * v."""
        return Vetor(self.x * fator, self.y * fator)

    def unitario(self) -> Vetor:
        """Retorna o versor v / ||v||."""
        comprimento = self.norma()
        if comprimento < EPSILON:
            raise ValueError("Nao e possivel normalizar o vetor nulo.")
        return Vetor(self.x / comprimento, self.y / comprimento)

    def angulo_polar_graus(self) -> float:
        """Angulo do vetor em relacao ao semieixo positivo X, em graus [0, 360)."""
        angulo = math.degrees(math.atan2(self.y, self.x))
        return angulo % 360.0


def vetor_por_polar(raio: float, angulo_graus: float) -> Vetor:
    """Constroi um vetor no R^2 a partir de coordenadas polares (r, theta)."""
    rad = math.radians(angulo_graus)
    return Vetor(raio * math.cos(rad), raio * math.sin(rad))


def produto_escalar(u: Vetor, v: Vetor) -> float:
    """Produto interno canonico em R^2: u . v = u_x * v_x + u_y * v_y."""
    return u.x * v.x + u.y * v.y


def determinante_2x2(u: Vetor, v: Vetor) -> float:
    """
    Determinante da matriz 2x2 formada pelos vetores u e v (produto vetorial 2D):
    det([u, v]) = u_x * v_y - u_y * v_x.
    Sinal positivo indica que v esta a esquerda de u (sentido anti-horario).
    """
    return u.x * v.y - u.y * v.x


def distancia_euclidiana(a: Ponto, b: Ponto) -> float:
    """Distancia d(A, B) = ||AB|| entre dois pontos no plano."""
    return a.vetor_ate(b).norma()


def angulo_entre_vetores_graus(u: Vetor, v: Vetor) -> float:
    """
    Calcula o angulo theta (em graus, 0 <= theta <= 180) entre dois vetores nao nulos
    pela relacao do produto escalar: cos(theta) = (u . v) / (||u|| * ||v||).
    """
    norma_u = u.norma()
    norma_v = v.norma()
    if norma_u < EPSILON or norma_v < EPSILON:
        return 0.0

    cosseno = produto_escalar(u, v) / (norma_u * norma_v)
    cosseno_limitado = max(-1.0, min(1.0, cosseno))
    return math.degrees(math.acos(cosseno_limitado))


def ponto_no_segmento(p: Ponto, a: Ponto, b: Ponto) -> bool:
    """
    Verifica se o ponto P pertence ao segmento fechado AB:
    1) AP e AB colineares: |det(AB, AP)| ~ 0
    2) Projecao dentro dos limites: 0 <= AP . AB <= ||AB||^2
    """
    ab = a.vetor_ate(b)
    ap = a.vetor_ate(p)
    if abs(determinante_2x2(ab, ap)) > 1e-7:
        return False

    esc = produto_escalar(ap, ab)
    if esc < -1e-7:
        return False

    norma_ab_quad = produto_escalar(ab, ab)
    if esc - norma_ab_quad > 1e-7:
        return False

    return True


def segmentos_se_intersectam(a: Ponto, b: Ponto, c: Ponto, d: Ponto) -> bool:
    """
    Verifica se os segmentos fechados AB e CD possuem intersecao no R^2
    usando orientacao via determinante 2x2 (produto vetorial 2D).
    """
    ab = a.vetor_ate(b)
    cd = c.vetor_ate(d)

    d1 = determinante_2x2(ab, a.vetor_ate(c))
    d2 = determinante_2x2(ab, a.vetor_ate(d))
    d3 = determinante_2x2(cd, c.vetor_ate(a))
    d4 = determinante_2x2(cd, c.vetor_ate(b))

    if ((d1 > EPSILON and d2 < -EPSILON) or (d1 < -EPSILON and d2 > EPSILON)) and (
        (d3 > EPSILON and d4 < -EPSILON) or (d3 < -EPSILON and d4 > EPSILON)
    ):
        return True

    if abs(d1) <= EPSILON and ponto_no_segmento(c, a, b):
        return True
    if abs(d2) <= EPSILON and ponto_no_segmento(d, a, b):
        return True
    if abs(d3) <= EPSILON and ponto_no_segmento(a, c, d):
        return True
    if abs(d4) <= EPSILON and ponto_no_segmento(b, c, d):
        return True

    return False


def ponto_em_poligono_convexo(ponto: Ponto, vertices: Sequence[Ponto]) -> bool:
    """
    Testa se um ponto pertence ao poligono convexo (incluindo borda).
    Para cada aresta orientada V_i -> V_{i+1}, avalia o sinal do determinante
    det(V_{i+1} - V_i, P - V_i). Se o ponto estiver sempre no mesmo semiplano
    fechado de todas as arestas, pertence ao poligono convexo.
    """
    total = len(vertices)
    if total < 3:
        raise ValueError("Um poligono precisa de pelo menos 3 vertices.")

    tem_positivo = False
    tem_negativo = False

    for i in range(total):
        atual = vertices[i]
        proximo = vertices[(i + 1) % total]
        if ponto_no_segmento(ponto, atual, proximo):
            return True

        aresta = atual.vetor_ate(proximo)
        relativo = atual.vetor_ate(ponto)
        orientacao = determinante_2x2(aresta, relativo)

        if orientacao > EPSILON:
            tem_positivo = True
        elif orientacao < -EPSILON:
            tem_negativo = True

        if tem_positivo and tem_negativo:
            return False

    return True
