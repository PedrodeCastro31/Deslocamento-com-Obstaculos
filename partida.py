from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from geometria import (
    EPSILON,
    Ponto,
    Vetor,
    angulo_entre_vetores_graus,
    distancia_euclidiana,
    vetor_por_polar,
)
from obstaculos import Obstaculo, sortear_obstaculos, verificar_colisao_obstaculos


@dataclass(frozen=True)
class SetorCircular:
    """
    Setor circular de movimentos validos a partir da posicao atual do competidor.
    Definido por:
    - centro: posicao atual C = (x, y)
    - direcao_central: vetor que orienta a bissetriz do setor (rumo ao ponto de chegada)
    - raio: alcance maximo R > 0 da jogada (norma maxima do deslocamento)
    - abertura_graus: abertura angular total theta do setor (meia-abertura = theta / 2)
    """

    centro: Ponto
    direcao_central: Vetor
    raio: float
    abertura_graus: float

    def angulo_central_graus(self) -> float:
        return self.direcao_central.angulo_polar_graus()

    def angulo_inicial_graus(self) -> float:
        return (self.angulo_central_graus() - self.abertura_graus / 2.0) % 360.0

    def angulo_final_graus(self) -> float:
        return (self.angulo_central_graus() + self.abertura_graus / 2.0) % 360.0

    def validar_ponto(self, destino: Ponto) -> Tuple[bool, str, float, float]:
        """
        Valida se o ponto destino pertence ao setor circular usando GAAL:
        1) Norma euclidiana: 0 < ||d|| <= R
        2) Angulo via produto escalar: arccos((d . u) / (||d|| ||u||)) <= abertura / 2
        Retorna (valido, mensagem, distancia, desvio_angular_graus).
        """
        deslocamento = self.centro.vetor_ate(destino)
        distancia = deslocamento.norma()

        if distancia < 1e-6:
            return (
                False,
                "Deslocamento nulo: escolha um ponto diferente da posicao atual.",
                distancia,
                0.0,
            )

        if distancia > self.raio + 1e-7:
            return (
                False,
                f"Fora do raio do setor: ||d|| = {distancia:.2f} > R = {self.raio:.2f}.",
                distancia,
                0.0,
            )

        desvio = angulo_entre_vetores_graus(deslocamento, self.direcao_central)
        meia_abertura = self.abertura_graus / 2.0

        if desvio > meia_abertura + 1e-6:
            return (
                False,
                f"Fora do angulo do setor: desvio = {desvio:.2f} graus > limite = {meia_abertura:.2f} graus.",
                distancia,
                desvio,
            )

        return (
            True,
            f"Dentro do setor (||d|| = {distancia:.2f} <= {self.raio:.2f}, desvio = {desvio:.2f} graus <= {meia_abertura:.2f} graus).",
            distancia,
            desvio,
        )


@dataclass
class Competidor:
    """Representa um dos dois competidores na corrida."""

    indice: int
    nome: str
    cor: str
    posicao_inicial: Ponto
    posicao_atual: Ponto
    trajetoria: List[Ponto] = field(default_factory=list)
    venceu: bool = False

    def __post_init__(self) -> None:
        if not self.trajetoria:
            self.trajetoria.append(self.posicao_inicial)


@dataclass
class ResultadoJogada:
    """Registro detalhado da validacao e execucao de uma jogada."""

    turno: int
    competidor: str
    origem: Ponto
    destino: Ponto
    setor: SetorCircular
    valida: bool
    motivo: str
    distancia_percorrida: float
    desvio_angular_graus: float
    distancia_restante_chegada: float
    atingiu_chegada: bool


@dataclass
class EstadoPartida:
    """Mantem o estado completo de uma partida de Deslocamento com Obstaculos."""

    largura_plano: float = 100.0
    altura_plano: float = 70.0
    ponto_chegada: Ponto = Ponto(92.0, 35.0)
    raio_chegada: float = 4.0
    competidores: List[Competidor] = field(default_factory=list)
    obstaculos: List[Obstaculo] = field(default_factory=list)
    historico_jogadas: List[ResultadoJogada] = field(default_factory=list)
    turno_atual: int = 1
    indice_da_vez: int = 0
    vencedor: Optional[Competidor] = None
    setor_atual: Optional[SetorCircular] = None

    def ForaDosLimites(self, ponto: Ponto) -> bool:
        return (
            ponto.x < 0.0
            or ponto.x > self.largura_plano
            or ponto.y < 0.0
            or ponto.y > self.altura_plano
        )


def criar_partida_padrao(
    semente: Optional[int] = None,
    quantidade_triangulos: int = 2,
    quantidade_quadrados: int = 2,
) -> EstadoPartida:
    """
    Inicializa o plano cartesiano (100x70), os 2 competidores nas posicoes iniciais,
    o ponto de chegada comum e sorteia os obstaculos (triangulos e quadrados).
    """
    inicio_1 = Ponto(8.0, 18.0)
    inicio_2 = Ponto(8.0, 52.0)
    chegada = Ponto(92.0, 35.0)

    competidores = [
        Competidor(
            indice=1,
            nome="Competidor 1",
            cor="#1f77b4",
            posicao_inicial=inicio_1,
            posicao_atual=inicio_1,
        ),
        Competidor(
            indice=2,
            nome="Competidor 2",
            cor="#d62728",
            posicao_inicial=inicio_2,
            posicao_atual=inicio_2,
        ),
    ]

    obstaculos = sortear_obstaculos(
        quantidade_triangulos=quantidade_triangulos,
        quantidade_quadrados=quantidade_quadrados,
        semente=semente,
    )

    return EstadoPartida(
        ponto_chegada=chegada,
        competidores=competidores,
        obstaculos=obstaculos,
    )


def gerar_setor_turno(
    partida: EstadoPartida,
    competidor: Competidor,
    gerador: Optional[random.Random] = None,
    raio_fixo: Optional[float] = None,
    abertura_fixa_graus: Optional[float] = None,
) -> SetorCircular:
    """
    Gera o setor circular do turno atual centrado na posicao do competidor e
    orientado na direcao do ponto de chegada (com raio e abertura definidos).
    """
    rng = gerador or random
    vetor_meta = competidor.posicao_atual.vetor_ate(partida.ponto_chegada)
    if vetor_meta.norma() < EPSILON:
        direcao = Vetor(1.0, 0.0)
    else:
        direcao = vetor_meta.unitario()

    raio = raio_fixo if raio_fixo is not None else round(rng.uniform(18.0, 26.0), 1)
    abertura = (
        abertura_fixa_graus
        if abertura_fixa_graus is not None
        else float(rng.choice([70, 80, 90, 100, 110]))
    )

    setor = SetorCircular(
        centro=competidor.posicao_atual,
        direcao_central=direcao,
        raio=raio,
        abertura_graus=abertura,
    )
    partida.setor_atual = setor
    return setor


def destino_por_deslocamento_polar(
    origem: Ponto,
    distancia: float,
    angulo_graus: float,
) -> Ponto:
    """Converte uma entrada polar (distancia, angulo em graus) em ponto destino (x, y)."""
    deslocamento = vetor_por_polar(distancia, angulo_graus)
    return origem.transladar(deslocamento)


def avaliar_e_executar_jogada(
    partida: EstadoPartida,
    competidor: Competidor,
    setor: SetorCircular,
    destino: Ponto,
) -> ResultadoJogada:
    """
    Valida a jogada segundo todas as regras de GAAL:
    1) Destino dentro dos limites do plano cartesiano;
    2) Destino contido no setor circular (norma <= R e angulo via produto escalar <= theta/2);
    3) Segmento origem -> destino sem intersecao/colisao com triangulos e quadrados;
    4) Verifica se atingiu o ponto de chegada (distancia <= raio_chegada ou segmento passa pela chegada).
    Se valida, atualiza a posicao e a trajetoria do competidor.
    """
    origem = competidor.posicao_atual

    if partida.ForaDosLimites(destino):
        dist_chegada = distancia_euclidiana(origem, partida.ponto_chegada)
        resultado = ResultadoJogada(
            turno=partida.turno_atual,
            competidor=competidor.nome,
            origem=origem,
            destino=destino,
            setor=setor,
            valida=False,
            motivo=(
                f"Ponto {destino.formatar()} fora dos limites do plano "
                f"[0, {partida.largura_plano:.0f}] x [0, {partida.altura_plano:.0f}]."
            ),
            distancia_percorrida=0.0,
            desvio_angular_graus=0.0,
            distancia_restante_chegada=dist_chegada,
            atingiu_chegada=False,
        )
        partida.historico_jogadas.append(resultado)
        return resultado

    ok_setor, msg_setor, distancia, desvio = setor.validar_ponto(destino)
    if not ok_setor:
        dist_chegada = distancia_euclidiana(origem, partida.ponto_chegada)
        resultado = ResultadoJogada(
            turno=partida.turno_atual,
            competidor=competidor.nome,
            origem=origem,
            destino=destino,
            setor=setor,
            valida=False,
            motivo=msg_setor,
            distancia_percorrida=distancia,
            desvio_angular_graus=desvio,
            distancia_restante_chegada=dist_chegada,
            atingiu_chegada=False,
        )
        partida.historico_jogadas.append(resultado)
        return resultado

    obstaculo_colidido = verificar_colisao_obstaculos(origem, destino, partida.obstaculos)
    if obstaculo_colidido is not None:
        dist_chegada = distancia_euclidiana(origem, partida.ponto_chegada)
        resultado = ResultadoJogada(
            turno=partida.turno_atual,
            competidor=competidor.nome,
            origem=origem,
            destino=destino,
            setor=setor,
            valida=False,
            motivo=(
                f"Colisao detectada com o obstaculo {obstaculo_colidido.nome} "
                f"({obstaculo_colidido.tipo})."
            ),
            distancia_percorrida=distancia,
            desvio_angular_graus=desvio,
            distancia_restante_chegada=dist_chegada,
            atingiu_chegada=False,
        )
        partida.historico_jogadas.append(resultado)
        return resultado

    # Jogada valida: atualiza posicao e trajetoria
    competidor.posicao_atual = destino
    competidor.trajetoria.append(destino)

    dist_chegada = distancia_euclidiana(destino, partida.ponto_chegada)
    atingiu = dist_chegada <= partida.raio_chegada + 1e-7
    if atingiu:
        competidor.venceu = True
        partida.vencedor = competidor

    motivo_final = msg_setor + " Caminho livre de obstaculos."
    if atingiu:
        motivo_final += f" {competidor.nome} atingiu o ponto de chegada!"

    resultado = ResultadoJogada(
        turno=partida.turno_atual,
        competidor=competidor.nome,
        origem=origem,
        destino=destino,
        setor=setor,
        valida=True,
        motivo=motivo_final,
        distancia_percorrida=distancia,
        desvio_angular_graus=desvio,
        distancia_restante_chegada=dist_chegada,
        atingiu_chegada=atingiu,
    )
    partida.historico_jogadas.append(resultado)
    return resultado


def escolher_jogada_inteligente(
    partida: EstadoPartida,
    competidor: Competidor,
    setor: SetorCircular,
) -> Optional[Ponto]:
    """
    Busca dentro do setor circular um ponto valido (sem colisao com obstaculos)
    que minimize a distancia euclidiana ate o ponto de chegada.
    Usado no modo de simulacao automatica / demonstracao.
    """
    # Se a propria chegada estiver dentro do setor e sem colisao, vai direto para ela
    ok_meta, _, _, _ = setor.validar_ponto(partida.ponto_chegada)
    if ok_meta and verificar_colisao_obstaculos(
        competidor.posicao_atual, partida.ponto_chegada, partida.obstaculos
    ) is None:
        return partida.ponto_chegada

    ang_central = setor.angulo_central_graus()
    meia = setor.abertura_graus / 2.0

    melhor_ponto: Optional[Ponto] = None
    menor_distancia = float("inf")

    fracoes_raio = [0.98, 0.85, 0.70, 0.55, 0.40]
    passos_angulo = 19  # testa desvios de -meia ate +meia

    for fracao in fracoes_raio:
        r = setor.raio * fracao
        for i in range(passos_angulo):
            fator = -1.0 + 2.0 * (i / (passos_angulo - 1))
            ang = ang_central + fator * (meia * 0.96)
            candidato = destino_por_deslocamento_polar(competidor.posicao_atual, r, ang)

            if partida.ForaDosLimites(candidato):
                continue

            ok, _, _, _ = setor.validar_ponto(candidato)
            if not ok:
                continue

            if verificar_colisao_obstaculos(
                competidor.posicao_atual, candidato, partida.obstaculos
            ) is not None:
                continue

            d_meta = distancia_euclidiana(candidato, partida.ponto_chegada)
            if d_meta < menor_distancia:
                menor_distancia = d_meta
                melhor_ponto = candidato

    return melhor_ponto


def simular_partida_completa(
    semente: Optional[int] = 42,
    max_turnos: int = 30,
) -> EstadoPartida:
    """
    Executa uma corrida automatica entre os 2 competidores ate que um atinja
    o ponto de chegada (ou atinja o limite de turnos).
    """
    rng = random.Random(semente)
    partida = criar_partida_padrao(semente=semente)

    for turno in range(1, max_turnos + 1):
        partida.turno_atual = turno
        competidor = partida.competidores[(turno - 1) % len(partida.competidores)]
        setor = gerar_setor_turno(partida, competidor, gerador=rng)

        destino = escolher_jogada_inteligente(partida, competidor, setor)
        if destino is None:
            continue

        resultado = avaliar_e_executar_jogada(partida, competidor, setor, destino)
        if resultado.atingiu_chegada:
            break

    return partida
