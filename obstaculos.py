from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from geometria import (
    Ponto,
    ponto_em_poligono_convexo,
    segmentos_se_intersectam,
)


@dataclass(frozen=True)
class Obstaculo:
    """
    Representa um obstaculo poligonal convexo no plano cartesiano:
    triangulo (3 vertices) ou quadrado (4 vertices).
    """

    nome: str
    tipo: str  # "triangulo" ou "quadrado"
    vertices: Tuple[Ponto, ...]

    def __post_init__(self) -> None:
        esperado = 3 if self.tipo == "triangulo" else 4
        if len(self.vertices) != esperado:
            raise ValueError(
                f"Obstaculo '{self.nome}' do tipo '{self.tipo}' deve ter {esperado} vertices."
            )

    def arestas(self) -> List[Tuple[Ponto, Ponto]]:
        """Retorna os segmentos orientados que formam a fronteira do poligono."""
        total = len(self.vertices)
        return [
            (self.vertices[i], self.vertices[(i + 1) % total])
            for i in range(total)
        ]

    def contem_ponto(self, ponto: Ponto) -> bool:
        """Verifica se um ponto cai no interior ou na borda do obstaculo."""
        return ponto_em_poligono_convexo(ponto, self.vertices)

    def intercepta_segmento(self, origem: Ponto, destino: Ponto) -> bool:
        """
        Verifica se o deslocamento retilineo origem -> destino colide com o obstaculo:
        - destino ou origem dentro do poligono;
        - ponto medio do deslocamento dentro do poligono;
        - intersecao do segmento de movimento com qualquer aresta do poligono.
        """
        if self.contem_ponto(origem) or self.contem_ponto(destino):
            return True

        ponto_medio = Ponto(
            (origem.x + destino.x) / 2.0,
            (origem.y + destino.y) / 2.0,
        )
        if self.contem_ponto(ponto_medio):
            return True

        for a, b in self.arestas():
            if segmentos_se_intersectam(origem, destino, a, b):
                return True

        return False


def catalogo_obstaculos_predefinidos() -> Tuple[List[Obstaculo], List[Obstaculo]]:
    """
    Retorna os conjuntos pre-definidos de triangulos (3 pontos) e quadrados (4 pontos)
    distribuidos na regiao central da pista (0 <= x <= 100, 0 <= y <= 70).
    """
    triangulos = [
        Obstaculo(
            nome="T1",
            tipo="triangulo",
            vertices=(Ponto(22.0, 14.0), Ponto(34.0, 14.0), Ponto(28.0, 27.0)),
        ),
        Obstaculo(
            nome="T2",
            tipo="triangulo",
            vertices=(Ponto(42.0, 40.0), Ponto(56.0, 40.0), Ponto(49.0, 54.0)),
        ),
        Obstaculo(
            nome="T3",
            tipo="triangulo",
            vertices=(Ponto(64.0, 16.0), Ponto(77.0, 20.0), Ponto(69.0, 33.0)),
        ),
        Obstaculo(
            nome="T4",
            tipo="triangulo",
            vertices=(Ponto(26.0, 45.0), Ponto(38.0, 48.0), Ponto(31.0, 60.0)),
        ),
        Obstaculo(
            nome="T5",
            tipo="triangulo",
            vertices=(Ponto(52.0, 10.0), Ponto(62.0, 10.0), Ponto(57.0, 23.0)),
        ),
    ]

    quadrados = [
        Obstaculo(
            nome="Q1",
            tipo="quadrado",
            vertices=(
                Ponto(34.0, 24.0),
                Ponto(45.0, 24.0),
                Ponto(45.0, 35.0),
                Ponto(34.0, 35.0),
            ),
        ),
        Obstaculo(
            nome="Q2",
            tipo="quadrado",
            vertices=(
                Ponto(58.0, 36.0),
                Ponto(69.0, 36.0),
                Ponto(69.0, 47.0),
                Ponto(58.0, 47.0),
            ),
        ),
        Obstaculo(
            nome="Q3",
            tipo="quadrado",
            vertices=(
                Ponto(18.0, 29.0),
                Ponto(28.0, 29.0),
                Ponto(28.0, 39.0),
                Ponto(18.0, 39.0),
            ),
        ),
        Obstaculo(
            nome="Q4",
            tipo="quadrado",
            vertices=(
                Ponto(72.0, 26.0),
                Ponto(82.0, 26.0),
                Ponto(82.0, 36.0),
                Ponto(72.0, 36.0),
            ),
        ),
        Obstaculo(
            nome="Q5",
            tipo="quadrado",
            vertices=(
                Ponto(44.0, 18.0),
                Ponto(53.0, 18.0),
                Ponto(53.0, 27.0),
                Ponto(44.0, 27.0),
            ),
        ),
    ]

    return triangulos, quadrados


def sortear_obstaculos(
    quantidade_triangulos: int = 2,
    quantidade_quadrados: int = 2,
    semente: Optional[int] = None,
) -> List[Obstaculo]:
    """
    Sorteia aleatoriamente triangulos e quadrados dentre os pre-definidos
    para compor a pista da partida.
    """
    gerador = random.Random(semente)
    triangulos, quadrados = catalogo_obstaculos_predefinidos()

    qtd_t = max(1, min(quantidade_triangulos, len(triangulos)))
    qtd_q = max(1, min(quantidade_quadrados, len(quadrados)))

    escolhidos_t = gerador.sample(triangulos, qtd_t)
    escolhidos_q = gerador.sample(quadrados, qtd_q)
    return escolhidos_t + escolhidos_q


def verificar_colisao_obstaculos(
    origem: Ponto,
    destino: Ponto,
    obstaculos: List[Obstaculo],
) -> Optional[Obstaculo]:
    """
    Retorna o primeiro obstaculo atingido pelo segmento origem -> destino,
    ou None se o caminho estiver livre.
    """
    for obstaculo in obstaculos:
        if obstaculo.intercepta_segmento(origem, destino):
            return obstaculo
    return None
