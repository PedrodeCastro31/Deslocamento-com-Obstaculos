"""Testes de corretude para a algebra linear, geometria, obstaculos e partida."""

from __future__ import annotations

import math

from geometria import (
    Ponto,
    Vetor,
    angulo_entre_vetores_graus,
    determinante_2x2,
    distancia_euclidiana,
    ponto_em_poligono_convexo,
    produto_escalar,
    segmentos_se_intersectam,
)
from obstaculos import Obstaculo, sortear_obstaculos
from partida import (
    SetorCircular,
    avaliar_e_executar_jogada,
    criar_partida_padrao,
    gerar_setor_turno,
    simular_partida_completa,
)
from visualizacao import exibir_estado_partida


def testar_vetores_e_norma() -> bool:
    a = Ponto(1.0, 2.0)
    b = Ponto(4.0, 6.0)
    v = a.vetor_ate(b)
    ok_norma = abs(v.norma() - 5.0) < 1e-9
    ok_dist = abs(distancia_euclidiana(a, b) - 5.0) < 1e-9
    ok_esc = abs(produto_escalar(Vetor(2.0, 3.0), Vetor(4.0, -1.0)) - 5.0) < 1e-9
    ok_ang = abs(angulo_entre_vetores_graus(Vetor(1.0, 0.0), Vetor(0.0, 1.0)) - 90.0) < 1e-9
    ok_det = abs(determinante_2x2(Vetor(1.0, 0.0), Vetor(0.0, 1.0)) - 1.0) < 1e-9
    return ok_norma and ok_dist and ok_esc and ok_ang and ok_det


def testar_intersecao_e_poligonos() -> bool:
    # Cruzamento em X
    cruzam = segmentos_se_intersectam(
        Ponto(0.0, 0.0), Ponto(4.0, 4.0), Ponto(0.0, 4.0), Ponto(4.0, 0.0)
    )
    # Segmentos paralelos disjuntos
    nao_cruzam = not segmentos_se_intersectam(
        Ponto(0.0, 0.0), Ponto(4.0, 0.0), Ponto(0.0, 2.0), Ponto(4.0, 2.0)
    )

    triangulo = (Ponto(0.0, 0.0), Ponto(6.0, 0.0), Ponto(3.0, 6.0))
    dentro_t = ponto_em_poligono_convexo(Ponto(3.0, 2.0), triangulo)
    fora_t = not ponto_em_poligono_convexo(Ponto(6.0, 5.0), triangulo)

    quadrado = (Ponto(10.0, 10.0), Ponto(20.0, 10.0), Ponto(20.0, 20.0), Ponto(10.0, 20.0))
    dentro_q = ponto_em_poligono_convexo(Ponto(15.0, 15.0), quadrado)
    fora_q = not ponto_em_poligono_convexo(Ponto(25.0, 15.0), quadrado)

    obs_q = Obstaculo(nome="Q_teste", tipo="quadrado", vertices=quadrado)
    atravessa = obs_q.intercepta_segmento(Ponto(5.0, 15.0), Ponto(25.0, 15.0))
    desvia = not obs_q.intercepta_segmento(Ponto(5.0, 5.0), Ponto(25.0, 5.0))

    return (
        cruzam
        and nao_cruzam
        and dentro_t
        and fora_t
        and dentro_q
        and fora_q
        and atravessa
        and desvia
    )


def testar_setor_circular() -> bool:
    setor = SetorCircular(
        centro=Ponto(0.0, 0.0),
        direcao_central=Vetor(1.0, 0.0),
        raio=10.0,
        abertura_graus=60.0,  # [-30°, +30°]
    )
    ok_dentro, _, _, _ = setor.validar_ponto(Ponto(8.0, 2.0))
    ok_fora_raio, _, _, _ = setor.validar_ponto(Ponto(12.0, 0.0))
    ok_fora_angulo, _, _, _ = setor.validar_ponto(Ponto(5.0, 6.0))  # ~50.2° > 30°
    return ok_dentro and (not ok_fora_raio) and (not ok_fora_angulo)


def testar_sorteio_e_partida() -> bool:
    sorteados = sortear_obstaculos(quantidade_triangulos=2, quantidade_quadrados=2, semente=42)
    qtd_t = sum(1 for o in sorteados if o.tipo == "triangulo")
    qtd_q = sum(1 for o in sorteados if o.tipo == "quadrado")
    if qtd_t != 2 or qtd_q != 2:
        return False

    partida = criar_partida_padrao(semente=10)
    comp = partida.competidores[0]
    setor = gerar_setor_turno(partida, comp, raio_fixo=20.0, abertura_fixa_graus=90.0)

    # Tenta jogada invalida fora do raio
    invalida = avaliar_e_executar_jogada(partida, comp, setor, Ponto(60.0, 18.0))
    if invalida.valida or comp.posicao_atual != comp.posicao_inicial:
        return False

    # Executa simulacao completa e garante vencedor + geracao de grafico
    partida_sim = simular_partida_completa(semente=42, max_turnos=30)
    if partida_sim.vencedor is None:
        return False

    caminho_grafico = exibir_estado_partida(
        partida_sim,
        setor_destaque=partida_sim.setor_atual,
        competidor_da_vez=partida_sim.vencedor,
        nome_arquivo="simulacao_partida.png",
        titulo="GAAL - Simulacao Completa: Deslocamento com Obstaculos",
    )
    return caminho_grafico.exists()


def main() -> None:
    testes = [
        ("Vetores, norma, produto escalar, angulo e determinante 2x2", testar_vetores_e_norma),
        ("Intersecao de segmentos e colisao com triangulo/quadrado", testar_intersecao_e_poligonos),
        ("Validacao de setor circular (raio R e abertura θ)", testar_setor_circular),
        ("Sorteio de obstaculos, partida completa e grafico matplotlib", testar_sorteio_e_partida),
    ]

    erros = 0
    print("Executando suite de validacao (GAAL - Deslocamento com Obstaculos)\n")
    for descricao, funcao in testes:
        ok = funcao()
        status = "OK" if ok else "ERRO"
        print(f"[{status}] {descricao}")
        if not ok:
            erros += 1

    print(f"\nTotal de baterias: {len(testes)} | Erros: {erros}")
    if erros == 0:
        print("Validacao concluida com sucesso.")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
