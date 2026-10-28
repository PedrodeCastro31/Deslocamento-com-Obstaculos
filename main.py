from __future__ import annotations

import random
from typing import Optional

from geometria import Ponto, distancia_euclidiana
from partida import (
    Competidor,
    EstadoPartida,
    SetorCircular,
    avaliar_e_executar_jogada,
    criar_partida_padrao,
    destino_por_deslocamento_polar,
    escolher_jogada_inteligente,
    gerar_setor_turno,
    simular_partida_completa,
)
from visualizacao import exibir_estado_partida


def imprimir_resumo_pista(partida: EstadoPartida) -> None:
    print("\n--- Configuracao da Pista (Plano R²) ---")
    print(f"Dimensoes do plano: [0, {partida.largura_plano:.0f}] x [0, {partida.altura_plano:.0f}]")
    print(f"Ponto de chegada:   {partida.ponto_chegada.formatar()} (raio de tolerancia = {partida.raio_chegada:.1f})")
    for comp in partida.competidores:
        print(f"{comp.nome}: inicio em {comp.posicao_inicial.formatar()}")
    print("Obstaculos sorteados:")
    for obs in partida.obstaculos:
        verts = ", ".join(v.formatar() for v in obs.vertices)
        print(f"  - {obs.nome} ({obs.tipo}): [{verts}]")


def ler_destino_turno(
    partida: EstadoPartida,
    competidor: Competidor,
    setor: SetorCircular,
) -> Optional[Ponto]:
    """
    Le a jogada do usuario aceitando:
    1) Coordenadas cartesianas (x, y)
    2) Deslocamento polar (distancia r e angulo em graus)
    3) Sugestao automatica valida dentro do setor
    Retorna None caso o jogador deseje encerrar a partida.
    """
    meia = setor.abertura_graus / 2.0
    print(
        f"\nSetor Circular gerado para {competidor.nome}:\n"
        f"  Posicao atual (centro): {setor.centro.formatar()}\n"
        f"  Raio maximo (R):        {setor.raio:.2f}\n"
        f"  Abertura angular (θ):   {setor.abertura_graus:.1f}° (±{meia:.1f}° em torno de {setor.angulo_central_graus():.1f}°)"
    )
    print(
        "Como deseja informar o movimento?\n"
        "  1 - Coordenada cartesiana (x y)\n"
        "  2 - Deslocamento polar (distancia angulo_graus)\n"
        "  3 - Jogada automatica sugerida (IA geométrica)\n"
        "  0 - Voltar ao menu principal"
    )

    while True:
        escolha = input("Modo de entrada > ").strip()
        if escolha == "0":
            return None

        if escolha == "1":
            try:
                partes = input("Digite x e y separados por espaco: ").strip().replace(",", " ").split()
                if len(partes) != 2:
                    print("Informe exatamente dois valores numericos: x y.")
                    continue
                return Ponto(float(partes[0]), float(partes[1]))
            except ValueError:
                print("Valores invalidos. Digite numeros reais (ex: 24.5 22.0).")

        elif escolha == "2":
            try:
                partes = (
                    input(
                        f"Digite distancia (<= {setor.raio:.1f}) e angulo em graus "
                        f"(eixo central {setor.angulo_central_graus():.1f}°): "
                    )
                    .strip()
                    .replace(",", " ")
                    .split()
                )
                if len(partes) != 2:
                    print("Informe exatamente dois valores: distancia angulo_graus.")
                    continue
                dist = float(partes[0])
                ang = float(partes[1])
                return destino_por_deslocamento_polar(competidor.posicao_atual, dist, ang)
            except ValueError:
                print("Valores invalidos. Digite numeros reais (ex: 18.0 25.0).")

        elif escolha == "3":
            sugerido = escolher_jogada_inteligente(partida, competidor, setor)
            if sugerido is None:
                print("Nenhum movimento automatico livre encontrado neste setor; informe manualmente.")
                continue
            print(f"Destino sugerido: {sugerido.formatar()}")
            return sugerido

        else:
            print("Opcao invalida. Escolha 1, 2, 3 ou 0.")


def modo_partida_interativa() -> None:
    print("\n=== Modo 1: Partida Interativa (2 Competidores) ===")
    entrada_seed = input("Semente aleatoria (Enter para sorteio livre): ").strip()
    semente = int(entrada_seed) if entrada_seed.isdigit() else None
    rng = random.Random(semente)

    partida = criar_partida_padrao(semente=semente)
    imprimir_resumo_pista(partida)

    turno = 1
    while partida.vencedor is None:
        partida.turno_atual = turno
        competidor = partida.competidores[(turno - 1) % len(partida.competidores)]
        dist_atual = distancia_euclidiana(competidor.posicao_atual, partida.ponto_chegada)

        print("\n" + "=" * 60)
        print(
            f"TURNO {turno} | Vez de {competidor.nome} | "
            f"Posicao: {competidor.posicao_atual.formatar()} | "
            f"Dist. ate chegada: {dist_atual:.2f}"
        )

        setor = gerar_setor_turno(partida, competidor, gerador=rng)
        exibir_estado_partida(
            partida,
            setor_destaque=setor,
            competidor_da_vez=competidor,
            nome_arquivo="turno_atual.png",
            titulo=f"Turno {turno} - Setor Circular de {competidor.nome}",
        )

        while True:
            destino = ler_destino_turno(partida, competidor, setor)
            if destino is None:
                print("Partida interrompida pelo usuario.")
                return

            resultado = avaliar_e_executar_jogada(partida, competidor, setor, destino)
            if resultado.valida:
                print(f"[JOGADA VALIDA] {resultado.motivo}")
                print(
                    f"Nova posicao de {competidor.nome}: {competidor.posicao_atual.formatar()} "
                    f"(distancia restante ate a chegada: {resultado.distancia_restante_chegada:.2f})"
                )
                exibir_estado_partida(
                    partida,
                    setor_destaque=setor,
                    competidor_da_vez=competidor,
                    nome_arquivo="turno_atual.png",
                    titulo=f"Turno {turno} Concluido - Nova Posicao de {competidor.nome}",
                )
                break

            print(f"[JOGADA INVALIDA] {resultado.motivo}")
            print("Tente novamente dentro do setor circular e sem colidir com obstaculos.")
            exibir_estado_partida(
                partida,
                setor_destaque=setor,
                competidor_da_vez=competidor,
                tentativa_invalida=destino,
                nome_arquivo="jogada_invalida.png",
                titulo=f"Turno {turno} - Jogada Rejeitada ({competidor.nome})",
            )

        if partida.vencedor is not None:
            print("\n" + "*" * 60)
            print(
                f"VITORIA! {partida.vencedor.nome} alcancou o ponto de chegada "
                f"no turno {turno}!"
            )
            print("*" * 60)
            exibir_estado_partida(
                partida,
                setor_destaque=setor,
                competidor_da_vez=partida.vencedor,
                nome_arquivo="partida_finalizada.png",
                titulo=f"Fim de Jogo - Vitoria de {partida.vencedor.nome}!",
            )
            break

        turno += 1


def modo_simulacao_automatica() -> None:
    print("\n=== Modo 2: Simulacao Automatica (Demonstracao Completa) ===")
    entrada_seed = input("Semente aleatoria (Enter para padrao=42): ").strip()
    semente = int(entrada_seed) if entrada_seed.lstrip("-").isdigit() else 42

    partida = simular_partida_completa(semente=semente)
    imprimir_resumo_pista(partida)

    print("\n--- Historico de Jogadas ---")
    for jog in partida.historico_jogadas:
        status = "VALIDA" if jog.valida else "INVALIDA"
        print(
            f"Turno {jog.turno:02d} | {jog.competidor}: "
            f"{jog.origem.formatar()} -> {jog.destino.formatar()} | "
            f"R={jog.setor.raio:.1f}, θ={jog.setor.abertura_graus:.0f}° | "
            f"||d||={jog.distancia_percorrida:.2f}, Δθ={jog.desvio_angular_graus:.1f}° | "
            f"dist_meta={jog.distancia_restante_chegada:.2f} [{status}]"
        )

    if partida.vencedor:
        print(f"\nResultado final: {partida.vencedor.nome} venceu a corrida!")
    else:
        print("\nLimite de turnos atingido sem vencedor.")

    exibir_estado_partida(
        partida,
        setor_destaque=partida.setor_atual,
        competidor_da_vez=partida.vencedor or partida.competidores[0],
        nome_arquivo="simulacao_partida.png",
        titulo="GAAL - Simulacao Completa: Deslocamento com Obstaculos",
    )


def modo_demonstrar_validacoes_gaal() -> None:
    print("\n=== Modo 3: Demonstracao de Validacoes Geometricas (GAAL) ===")
    partida = criar_partida_padrao(semente=7)
    comp = partida.competidores[0]
    setor = gerar_setor_turno(
        partida, comp, raio_fixo=22.0, abertura_fixa_graus=80.0
    )

    casos = [
        ("Fora do raio (||d|| > R)", Ponto(45.0, 25.0)),
        ("Fora do angulo (desvio > θ/2)", Ponto(10.0, 35.0)),
        ("Colisao com obstaculo", Ponto(26.0, 18.0)),
        ("Jogada valida dentro do setor", Ponto(21.0, 24.0)),
    ]

    for descricao, ponto_teste in casos:
        res = avaliar_e_executar_jogada(partida, comp, setor, ponto_teste)
        status = "APROVADA" if res.valida else "REJEITADA"
        print(f"\nCaso: {descricao} -> Destino {ponto_teste.formatar()}")
        print(f"  Status:   {status}")
        print(f"  Detalhes: {res.motivo}")


def exibir_menu() -> None:
    print("\n" + "=" * 56)
    print(" Trabalho de GAAL - Deslocamento com Obstaculos")
    print(" Corrida no Plano Cartesiano R² com Setor Circular")
    print("=" * 56)
    print("1 - Jogar partida interativa (2 competidores)")
    print("2 - Executar simulacao automatica e gerar grafico")
    print("3 - Demonstrar validacoes geometricas (raio, angulo, colisao)")
    print("0 - Sair")


def main() -> None:
    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opcao: ").strip()

        if opcao == "1":
            modo_partida_interativa()
        elif opcao == "2":
            modo_simulacao_automatica()
        elif opcao == "3":
            modo_demonstrar_validacoes_gaal()
        elif opcao == "0":
            print("Encerrando.")
            break
        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    main()
