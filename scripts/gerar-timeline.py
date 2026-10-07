"""Gera a timeline da trajetória (SVG animado) para o README do GitHub.

Mesmo truque do carrossel: o GitHub anima SVG carregado como <img>, sem JS.
Uso: python3 scripts/gerar-timeline.py assets/trajetoria.svg
"""
import sys
from xml.sax.saxutils import escape

SAIDA = sys.argv[1]

# cores do portfólio (victor-dev/app/globals.css)
FUNDO = "#070b16"
SUPERFICIE = "#0c1426"
LINHA = "#f9fafb24"
BRANCO = "#f9fafb"
ACENTO = "#60a5fa"
AZUL = "#2563eb"
VERDE = "#34d399"
TINTA2 = "#b4bdcb"
TINTA3 = "#98a3b4"

IA = {"Claude Code", "Codex", "OpenAI"}

# do agora para o começo — mesma ordem e textos da linha do tempo do portfólio
MARCOS = [
    {
        "ano": "2026", "periodo": "mar 2026 — agora", "empresa": "NOCLAF Tech",
        "cargo": "Desenvolvedor Full Stack", "atual": True,
        "texto": "AI Factory: plataformas web completas, do front-end à API, com IA no fluxo de desenvolvimento.",
        "marcas": ["Next.js", "React", "TypeScript", "Python", "Django", "AWS", "OpenAI", "Claude Code", "Codex"],
    },
    {
        "ano": "2025", "periodo": "set 2025 — mar 2026", "empresa": "NOCLAF Tech",
        "cargo": "Desenvolvedor Front-end",
        "texto": "Front-ends de sistemas de gestão, painéis administrativos, portais e landing pages de captação.",
        "marcas": ["React", "TypeScript", "Next.js", "Angular", "Tailwind CSS", "Claude Code"],
    },
    {
        "ano": "2022", "periodo": "jun 2022 — set 2025", "empresa": "MV Sistemas",
        "cargo": "Desenvolvedor Front-end",
        "texto": "Aplicações web de grande escala para a área da saúde.",
        "marcas": ["React", "JavaScript", "TypeScript", "Sass", "Bootstrap"],
    },
    {
        "ano": "2021", "periodo": "mai — jul 2021", "empresa": "Alterdata Software",
        "cargo": "Técnico de Infraestrutura Cloud",
        "texto": "Manutenção de servidores em nuvem, implantação de clientes e otimização do banco de dados.",
        "marcas": ["AWS", "Nutanix", "VMware"],
    },
    {
        "ano": "2020", "periodo": "jul 2020 — jun 2022", "empresa": "Alterdata Software",
        "cargo": "Técnico de Help Desk",
        "texto": "Suporte ao cliente, resolução de problemas e manutenção de sistemas e banco de dados.",
        "marcas": ["PostgreSQL", "SQL Server"],
    },
]

LARGURA = 880
CENTRO = LARGURA / 2
CARTAO = 372  # largura de cada cartão
VAO = 34  # do eixo até o cartão
PAD = 17  # respiro interno do cartão
TOPO = 28
DISCO = 20


def largura_texto(s: str, tamanho: float, negrito=False) -> float:
    """Estimativa para fonte sem serifa do sistema (sem medir de verdade)."""
    return len(s) * tamanho * (0.58 if negrito else 0.5)


def quebrar(texto: str, tamanho: float, maximo: float) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if largura_texto(teste, tamanho) > maximo and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + [atual]


def montar_cartao(m: dict, x: float, y: float, n: int) -> tuple[str, float]:
    """Devolve o SVG do cartão e a altura dele."""
    miolo = CARTAO - PAD * 2
    partes = []
    cy = y + PAD + 4

    partes.append(f'<text class="periodo" x="{x + PAD}" y="{cy + 8}">{escape(m["periodo"].upper())}</text>')
    if m.get("atual"):
        px = x + CARTAO - PAD - 66
        partes.append(
            f'<rect x="{px}" y="{cy - 4}" width="66" height="18" rx="9" fill="{VERDE}1f" stroke="{VERDE}80"/>'
            f'<circle class="pisca" cx="{px + 11.5}" cy="{cy + 5}" r="3" fill="{VERDE}"/>'
            f'<text class="agora" x="{px + 20}" y="{cy + 8.5}">AGORA</text>'
        )
    cy += 29
    partes.append(f'<text class="cargo" x="{x + PAD}" y="{cy}">{escape(m["cargo"])}</text>')
    cy += 18
    partes.append(f'<text class="empresa" x="{x + PAD}" y="{cy}">{escape(m["empresa"])}</text>')
    cy += 20
    for linha in quebrar(m["texto"], 11.5, miolo):
        partes.append(f'<text class="texto" x="{x + PAD}" y="{cy}">{escape(linha)}</text>')
        cy += 16
    cy += 4

    # etiquetas da stack, quebrando linha quando não cabem
    tx = x + PAD
    for marca in m["marcas"]:
        w = largura_texto(marca, 10) + 18
        if tx + w > x + CARTAO - PAD:
            tx = x + PAD
            cy += 24
        classe = "tag ia" if marca in IA else "tag"
        partes.append(
            f'<g class="{classe}"><rect x="{tx}" y="{cy}" width="{w:.1f}" height="19" rx="9.5"/>'
            f'<text x="{tx + w / 2:.1f}" y="{cy + 13}" text-anchor="middle">{escape(marca)}</text></g>'
        )
        tx += w + 5
    cy += 19

    altura = cy + PAD - y
    borda = f'stroke="{AZUL}" stroke-width="1.5"' if m.get("atual") else f'stroke="{LINHA}"'
    fundo = ""
    if m.get("atual"):
        fundo = f'<rect x="{x}" y="{y}" width="{CARTAO}" height="{altura}" rx="16" fill="{AZUL}" opacity=".35" filter="url(#halo)"/>'
    cartao = (
        f'<g class="cartao {"esq" if n % 2 == 0 else "dir"}" style="animation-delay:{0.25 + n * 0.18:.2f}s">'
        f'{fundo}<rect x="{x}" y="{y}" width="{CARTAO}" height="{altura}" rx="16" fill="{SUPERFICIE}" {borda}/>'
        f'{"".join(partes)}</g>'
    )
    return cartao, altura


# --- posições: zigue-zague, cada lado só precisa não encostar no cartão anterior do mesmo lado
cartoes, nos = [], []
alturas, ys = [], []
for n, m in enumerate(MARCOS):
    _, h = montar_cartao(m, 0, 0, n)
    alturas.append(h)
for n in range(len(MARCOS)):
    y = TOPO if n == 0 else ys[-1] + 74
    if n >= 2:
        y = max(y, ys[n - 2] + alturas[n - 2] + 22)
    ys.append(y)

for n, m in enumerate(MARCOS):
    esquerda = n % 2 == 0
    x = CENTRO - VAO - CARTAO if esquerda else CENTRO + VAO
    svg_cartao, h = montar_cartao(m, x, ys[n], n)
    cartoes.append(svg_cartao)

    ny = ys[n] + 26  # o disco se alinha com o topo do cartão
    borda_x = x + CARTAO if esquerda else x
    cor = VERDE if m.get("atual") else AZUL
    no = [f'<line x1="{CENTRO}" y1="{ny}" x2="{borda_x}" y2="{ny}" stroke="{cor}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="3 4"/>']
    if m.get("atual"):
        no.append(f'<circle class="pulso" cx="{CENTRO}" cy="{ny}" r="{DISCO}" fill="none" stroke="{VERDE}" stroke-width="2"/>')
    no.append(
        f'<g class="no" style="animation-delay:{0.15 + n * 0.18:.2f}s">'
        f'<circle cx="{CENTRO}" cy="{ny}" r="{DISCO}" fill="{FUNDO}" stroke="{cor}" stroke-width="2.5"/>'
        f'<text class="ano" x="{CENTRO}" y="{ny + 4.5}" text-anchor="middle">{m["ano"]}</text></g>'
    )
    nos.append("".join(no))

altura = max(y + h for y, h in zip(ys, alturas)) + TOPO
eixo_fim = altura - 14

css = f"""
text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}
.periodo{{font-size:10px;font-weight:700;letter-spacing:.12em;fill:{ACENTO}}}
.agora{{font-size:9px;font-weight:800;letter-spacing:.12em;fill:{VERDE}}}
.cargo{{font-size:15px;font-weight:700;fill:{BRANCO}}}
.empresa{{font-size:12px;font-weight:600;fill:{TINTA2}}}
.texto{{font-size:11.5px;fill:{TINTA3}}}
.ano{{font-size:11px;font-weight:800;fill:{BRANCO}}}
.tag rect{{fill:{AZUL}1f;stroke:{AZUL}66}}
.tag text{{font-size:10px;font-weight:600;fill:{ACENTO}}}
.tag.ia rect{{fill:{VERDE}1a;stroke:{VERDE}80}}
.tag.ia text{{fill:{VERDE}}}
.eixo{{stroke-dasharray:{eixo_fim};animation:desenha 1.8s ease-out both}}
.cartao{{animation:entra .8s cubic-bezier(.2,.7,.2,1) both}}
.cartao.esq{{--de:-28px}}.cartao.dir{{--de:28px}}
.no{{animation:surge .5s ease-out both;transform-box:fill-box;transform-origin:center}}
.pulso{{animation:pulso 2.2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
.pisca{{animation:pisca 1.4s ease-in-out infinite}}
.viajante{{animation:viaja 5s ease-in-out infinite}}
@keyframes desenha{{from{{stroke-dashoffset:{eixo_fim}}}to{{stroke-dashoffset:0}}}}
@keyframes entra{{from{{opacity:0;transform:translateX(var(--de))}}to{{opacity:1;transform:none}}}}
@keyframes surge{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
@keyframes pulso{{from{{opacity:.8;transform:scale(1)}}to{{opacity:0;transform:scale(1.7)}}}}
@keyframes pisca{{50%{{opacity:.25}}}}
@keyframes viaja{{from{{transform:translateY(0);opacity:0}}12%{{opacity:1}}88%{{opacity:1}}to{{transform:translateY({eixo_fim - 30}px);opacity:0}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{altura:.0f}" viewBox="0 0 {LARGURA} {altura:.0f}" role="img" aria-label="Trajetória profissional de Victor Maciel">
<title>Trajetória — Victor Maciel</title>
<style>{css}</style>
<defs>
<linearGradient id="gEixo" gradientUnits="userSpaceOnUse" x1="{CENTRO}" y1="14" x2="{CENTRO}" y2="{eixo_fim}"><stop offset="0" stop-color="{VERDE}"/><stop offset=".35" stop-color="{AZUL}"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></linearGradient>
<radialGradient id="brilho" cx=".5" cy="0" r=".8"><stop offset="0" stop-color="{AZUL}" stop-opacity=".2"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></radialGradient>
<radialGradient id="gViajante"><stop offset="0" stop-color="{ACENTO}"/><stop offset="1" stop-color="{ACENTO}" stop-opacity="0"/></radialGradient>
<filter id="halo" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
<clipPath id="card"><rect width="{LARGURA}" height="{altura:.0f}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{LARGURA}" height="{altura:.0f}" fill="{FUNDO}"/>
<rect width="{LARGURA}" height="{altura:.0f}" fill="url(#brilho)"/>
<line class="eixo" x1="{CENTRO}" y1="14" x2="{CENTRO}" y2="{eixo_fim}" stroke="url(#gEixo)" stroke-width="3" stroke-linecap="round"/>
<circle class="viajante" cx="{CENTRO}" cy="30" r="8" fill="url(#gViajante)"/>
{"".join(cartoes)}
{"".join(nos)}
</g>
<rect x=".5" y=".5" width="{LARGURA - 1}" height="{altura - 1:.0f}" rx="18" fill="none" stroke="{LINHA}"/>
</svg>
"""
open(SAIDA, "w").write(svg)
print(f"{SAIDA}: {len(svg) / 1024:.0f} KB, {altura:.0f}px de altura")
