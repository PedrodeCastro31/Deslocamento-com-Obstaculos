from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Wedge

from geometria import Ponto, vetor_por_polar
from partida import Competidor, EstadoPartida, SetorCircular

_PASTA_GRAFICOS = Path(__file__).parent / "graficos"


def exibir_figura(fig: plt.Figure, nome_arquivo: str) -> Path:
    """Salva o grafico em disco e exibe se o backend for interativo."""
    _PASTA_GRAFICOS.mkdir(exist_ok=True)
    caminho = _PASTA_GRAFICOS / nome_arquivo
    fig.savefig(caminho, dpi=150, bbox_inches="tight")

    backend = matplotlib.get_backend().lower()
    print(f"Grafico salvo em: {caminho}")
    if "agg" in backend:
        plt.close(fig)
        return caminho

    plt.show()
    return caminho


def _desenhar_obstaculos(ax: plt.Axes, partida: EstadoPartida) -> None:
    for idx, obs in enumerate(partida.obstaculos):
        coords = [(v.x, v.y) for v in obs.vertices]
        cor_face = "#f39c12" if obs.tipo == "triangulo" else "#8e44ad"
        label = (
            f"Obstaculo ({obs.tipo})"
            if idx == 0 or all(o.tipo != obs.tipo for o in partida.obstaculos[:idx])
            else None
        )
        poligono = Polygon(
            coords,
            closed=True,
            facecolor=cor_face,
            edgecolor="#2c3e50",
            alpha=0.55,
            linewidth=1.8,
            label=label,
        )
        ax.add_patch(poligono)

        cx = sum(v.x for v in obs.vertices) / len(obs.vertices)
        cy = sum(v.y for v in obs.vertices) / len(obs.vertices)
        ax.text(
            cx,
            cy,
            obs.nome,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#2c3e50", alpha=0.75),
        )


def _desenhar_setor(
    ax: plt.Axes,
    setor: SetorCircular,
    cor: str = "#2ecc71",
    rotulo_prefixo: str = "Setor atual",
) -> None:
    ang_central = setor.angulo_central_graus()
    meia = setor.abertura_graus / 2.0
    theta1 = ang_central - meia
    theta2 = ang_central + meia

    cunha = Wedge(
        center=(setor.centro.x, setor.centro.y),
        r=setor.raio,
        theta1=theta1,
        theta2=theta2,
        facecolor=cor,
        edgecolor="#1e8449",
        alpha=0.25,
        linewidth=1.8,
        linestyle="--",
        label=f"{rotulo_prefixo} (R={setor.raio:.1f}, θ={setor.abertura_graus:.0f}°)",
    )
    ax.add_patch(cunha)

    # Desenha o vetor bissetriz (eixo central do setor) indicando o raio R
    ponta_eixo = setor.centro.transladar(
        vetor_por_polar(setor.raio, ang_central)
    )
    ax.annotate(
        "",
        xy=(ponta_eixo.x, ponta_eixo.y),
        xytext=(setor.centro.x, setor.centro.y),
        arrowprops=dict(arrowstyle="->", color="#117a65", lw=1.6, ls="-."),
    )
    meio_eixo = Ponto(
        (setor.centro.x + ponta_eixo.x) / 2.0,
        (setor.centro.y + ponta_eixo.y) / 2.0,
    )
    ax.text(
        meio_eixo.x,
        meio_eixo.y + 2.2,
        f"R={setor.raio:.1f} | θ={setor.abertura_graus:.0f}°",
        fontsize=8.5,
        fontweight="bold",
        color="#0e6251",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#e8f8f5", edgecolor="#117a65", alpha=0.9),
    )


def exibir_estado_partida(
    partida: EstadoPartida,
    setor_destaque: Optional[SetorCircular] = None,
    competidor_da_vez: Optional[Competidor] = None,
    tentativa_invalida: Optional[Ponto] = None,
    nome_arquivo: str = "estado_partida.png",
    titulo: Optional[str] = None,
) -> Path:
    """
    Renderiza o plano cartesiano completo:
    - obstaculos sorteados (triangulos e quadrados);
    - posicoes iniciais, trajetorias e posicoes atuais dos 2 competidores;
    - ponto de chegada e zona de tolerancia;
    - setor circular de movimento (raio R e abertura angular theta);
    - resumo analitico das ultimas jogadas.
    """
    fig, (ax, ax_info) = plt.subplots(
        1,
        2,
        figsize=(14, 7),
        gridspec_kw={"width_ratios": [2.3, 1.0]},
    )

    titulo_final = titulo or "GAAL - Deslocamento com Obstaculos no Plano Cartesiano"
    fig.suptitle(titulo_final, fontsize=13, fontweight="bold")

    ax.set_xlim(0, partida.largura_plano)
    ax.set_ylim(0, partida.altura_plano)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.set_xlabel("Eixo X")
    ax.set_ylabel("Eixo Y")
    ax.set_title("Plano Cartesiano R² — Trajetorias, Obstaculos e Setor Circular")

    _desenhar_obstaculos(ax, partida)

    # Ponto de chegada + circulo de tolerancia
    zona_chegada = Circle(
        (partida.ponto_chegada.x, partida.ponto_chegada.y),
        radius=partida.raio_chegada,
        facecolor="#f1c40f",
        edgecolor="#b7950b",
        alpha=0.35,
        linewidth=1.5,
        label=f"Zona de chegada (r={partida.raio_chegada:.1f})",
    )
    ax.add_patch(zona_chegada)
    ax.plot(
        partida.ponto_chegada.x,
        partida.ponto_chegada.y,
        marker="*",
        markersize=15,
        color="#d4ac0d",
        markeredgecolor="black",
        linestyle="None",
        label=f"Chegada {partida.ponto_chegada.formatar()}",
    )

    # Trajetorias dos 2 competidores
    for comp in partida.competidores:
        xs = [p.x for p in comp.trajetoria]
        ys = [p.y for p in comp.trajetoria]
        ax.plot(
            xs,
            ys,
            "-o",
            color=comp.cor,
            linewidth=2.2,
            markersize=6,
            label=f"{comp.nome} (atual: {comp.posicao_atual.formatar()})",
        )
        ax.plot(
            comp.posicao_inicial.x,
            comp.posicao_inicial.y,
            marker="s",
            markersize=8,
            color=comp.cor,
            markeredgecolor="black",
        )
        ax.plot(
            comp.posicao_atual.x,
            comp.posicao_atual.y,
            marker="o",
            markersize=10,
            color=comp.cor,
            markeredgecolor="black",
        )

    setor_para_desenhar = setor_destaque or partida.setor_atual
    if setor_para_desenhar is not None:
        nome_vez = competidor_da_vez.nome if competidor_da_vez else "Setor do turno"
        _desenhar_setor(ax, setor_para_desenhar, rotulo_prefixo=f"Setor ({nome_vez})")

    if tentativa_invalida is not None and setor_para_desenhar is not None:
        ax.plot(
            [setor_para_desenhar.centro.x, tentativa_invalida.x],
            [setor_para_desenhar.centro.y, tentativa_invalida.y],
            "r--",
            linewidth=1.8,
        )
        ax.plot(
            tentativa_invalida.x,
            tentativa_invalida.y,
            marker="x",
            markersize=11,
            color="red",
            markeredgewidth=2.5,
            label=f"Jogada invalida {tentativa_invalida.formatar()}",
        )

    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.92)

    # Painel lateral de informacoes matematicas / GAAL
    ax_info.axis("off")
    linhas = [
        "Resumo da Partida (GAAL)",
        "=" * 32,
        f"Chegada: {partida.ponto_chegada.formatar()} (tol <= {partida.raio_chegada:.1f})",
        f"Obstaculos sorteados: {', '.join(f'{o.nome}({o.tipo[0].upper()})' for o in partida.obstaculos)}",
        f"Total de jogadas registradas: {len(partida.historico_jogadas)}",
        f"Vencedor: {partida.vencedor.nome if partida.vencedor else 'Em andamento'}",
        "",
        "Posicoes e passos:",
    ]
    for comp in partida.competidores:
        passos = len(comp.trajetoria) - 1
        linhas.append(
            f"- {comp.nome}: {comp.posicao_atual.formatar()} ({passos} mov.)"
        )

    if setor_para_desenhar is not None:
        linhas.extend(
            [
                "",
                "Setor Circular em Destaque:",
                f"  Centro C = {setor_para_desenhar.centro.formatar()}",
                f"  Raio maximo R = {setor_para_desenhar.raio:.1f}",
                f"  Abertura θ = {setor_para_desenhar.abertura_graus:.1f}° (±{setor_para_desenhar.abertura_graus/2:.1f}°)",
                f"  Eixo central = {setor_para_desenhar.angulo_central_graus():.1f}°",
            ]
        )

    if partida.historico_jogadas:
        linhas.extend(["", "Ultimas jogadas validadas:"])
        for jog in partida.historico_jogadas[-6:]:
            status = "OK" if jog.valida else "REJ"
            linhas.append(
                f"T{jog.turno:02d} [{status}] {jog.competidor}: "
                f"-> {jog.destino.formatar()} "
                f"(||d||={jog.distancia_percorrida:.1f}, Δθ={jog.desvio_angular_graus:.1f}°)"
            )

    ax_info.text(
        0.02,
        0.98,
        "\n".join(linhas),
        va="top",
        ha="left",
        fontsize=9.2,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9f9", edgecolor="#bdc3c7"),
    )

    plt.tight_layout()
    return exibir_figura(fig, nome_arquivo)
