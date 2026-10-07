"""Gera um SVG animado (carrossel infinito) com as stacks, para o README do GitHub.

O GitHub não roda JS nem CSS no README, mas anima SVG carregado como <img>.
Os ícones vão embutidos (data URI), porque SVG-como-imagem não carrega nada externo.
"""
import base64
import math
import re
import sys
import urllib.request
from xml.sax.saxutils import escape

SAIDA = sys.argv[1]

# cores do portfólio (victor-dev/app/globals.css)
FUNDO = "#070b16"
LINHA = "#f9fafb24"
ACENTO = "#60a5fa"
AZUL = "#2563eb"
VERDE = "#34d399"
TINTA2 = "#b4bdcb"
LADRILHO = "#242938"  # mesmo fundo dos ícones do skillicons

LARGURA = 880
PASSO = 78  # distância entre itens
ICONE = 32
VELOCIDADE = 28  # px por segundo

# (rótulo, [(nome, fonte, destaque)])  — fonte: skill:<id> | simple:<slug>:<cor> | lobe:<nome>[:<cor>]
FAIXAS = [
    ("Front-end & UI", [
        ("React", "skill:react"), ("Next.js", "skill:nextjs"), ("TypeScript", "skill:ts"),
        ("JavaScript", "skill:js"), ("Vite", "skill:vite"), ("Angular", "skill:angular"),
        ("Tailwind CSS", "skill:tailwind"), ("Sass", "skill:sass"), ("Bootstrap", "skill:bootstrap"),
        ("Material UI", "skill:materialui"), ("shadcn/ui", "simple:shadcnui:ffffff"),
    ]),
    ("Back-end, Dados & Cloud", [
        ("Python", "skill:py"), ("Django", "skill:django"), ("Node.js", "skill:nodejs"),
        ("NestJS", "skill:nestjs"), ("PostgreSQL", "skill:postgres"), ("MySQL", "skill:mysql"),
        ("Supabase", "skill:supabase"), ("Firebase", "skill:firebase"), ("AWS", "skill:aws"),
        ("Docker", "skill:docker"),
    ]),
    ("IA & Ferramentas", [
        ("Claude Code", "lobe:claudecode:D97757", True), ("Codex", "lobe:codex:ffffff", True),
        ("OpenAI API", "lobe:openai:ffffff", True), ("Git", "skill:git"), ("GitHub", "skill:github"),
        ("GitLab", "skill:gitlab"), ("GitHub Actions", "skill:githubactions"), ("VS Code", "skill:vscode"),
    ]),
    ("Mobile & Bibliotecas", [
        ("React Native", "skill:react"), ("Ionic", "simple:ionic:3880FF"),
        ("TanStack Query", "simple:reactquery:FF4154"), ("React Hook Form", "simple:reacthookform:EC5990"),
        ("Zod", "simple:zod:6B93E6"), ("GSAP", "simple:gsap:0AE448"),
        ("Google Maps", "simple:googlemaps:4285F4"), ("Tag Manager", "simple:googletagmanager:4C8BF5"),
    ]),
]


def baixar(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def ladrilho(svg24: str, cor: str) -> str:
    """Põe um logo 24x24 num ladrilho no mesmo estilo do skillicons."""
    svg24 = re.sub(r"<title>.*?</title>", "", svg24)
    miolo = re.search(r"<svg[^>]*>(.*)</svg>", svg24, re.S).group(1)
    miolo = miolo.replace("currentColor", f"#{cor}")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'
        f'<rect width="256" height="256" rx="60" fill="{LADRILHO}"/>'
        f'<svg x="60" y="60" width="136" height="136" viewBox="0 0 24 24" fill="#{cor}" fill-rule="evenodd">{miolo}</svg>'
        "</svg>"
    )


def icone(fonte: str) -> str:
    tipo, _, resto = fonte.partition(":")
    if tipo == "skill":
        return baixar(f"https://skillicons.dev/icons?i={resto}")
    if tipo == "simple":
        slug, cor = resto.split(":")
        return ladrilho(baixar(f"https://cdn.simpleicons.org/{slug}"), cor)
    if tipo == "lobe":
        nome, cor = resto.split(":")
        return ladrilho(baixar(f"https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@latest/icons/{nome}.svg"), cor)
    raise ValueError(fonte)


# --- ícones únicos, uma vez só no <defs> ----------------------------------------
ids: dict[str, str] = {}
defs = []
for _, itens in FAIXAS:
    for item in itens:
        fonte = item[1]
        if fonte in ids:
            continue
        ident = "i" + str(len(ids))
        ids[fonte] = ident
        dados = base64.b64encode(icone(fonte).encode()).decode()
        defs.append(f'<image id="{ident}" width="{ICONE}" height="{ICONE}" href="data:image/svg+xml;base64,{dados}"/>')

# --- faixas -------------------------------------------------------------------------
PAD_Y = 22
ALTURA_FAIXA = 80
altura = PAD_Y * 2 + ALTURA_FAIXA * len(FAIXAS) - 14

css = [
    "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}",
    f".rot{{font-size:11px;font-weight:700;letter-spacing:.14em;fill:{ACENTO}}}",
    f".nome{{font-size:9.5px;fill:{TINTA2}}}",
    f".nome.ia{{fill:{ACENTO};font-weight:700}}",
    "@media (prefers-reduced-motion: reduce){.trilho{animation:none!important}}",
]
corpo = []
for n, (rotulo, itens) in enumerate(FAIXAS):
    y0 = PAD_Y + n * ALTURA_FAIXA
    largura_seq = len(itens) * PASSO
    copias = math.ceil(LARGURA / largura_seq) + 1
    duracao = round(largura_seq / VELOCIDADE, 1)
    sentido = "normal" if n % 2 == 0 else "reverse"
    css.append(
        f"@keyframes f{n}{{from{{transform:translateX(0)}}to{{transform:translateX(-{largura_seq}px)}}}}"
        f".f{n}{{animation:f{n} {duracao}s linear infinite {sentido}}}"
    )

    corpo.append(f'<circle cx="34" cy="{y0 + 5}" r="3.5" fill="{VERDE}"/>')
    corpo.append(f'<text class="rot" x="45" y="{y0 + 9}">{escape(rotulo.upper())}</text>')

    blocos = []
    for c in range(copias):
        for i, item in enumerate(itens):
            nome, fonte = item[0], item[1]
            ia = len(item) > 2 and item[2]
            x = c * largura_seq + i * PASSO + (PASSO - ICONE) / 2
            yi = y0 + 19
            if ia:
                blocos.append(
                    f'<rect x="{x - 4}" y="{yi - 4}" width="{ICONE + 8}" height="{ICONE + 8}" rx="11" '
                    f'fill="none" stroke="{ACENTO}" stroke-width="2"/>'
                )
            blocos.append(f'<use href="#{ids[fonte]}" x="{x}" y="{yi}"/>')
            blocos.append(
                f'<text class="nome{" ia" if ia else ""}" x="{x + ICONE / 2}" y="{yi + ICONE + 14}" '
                f'text-anchor="middle">{escape(nome)}</text>'
            )
    corpo.append(f'<g class="trilho f{n}">{"".join(blocos)}</g>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{altura}" viewBox="0 0 {LARGURA} {altura}" role="img" aria-label="Tecnologias de Victor Maciel">
<title>Tech Stack — Victor Maciel</title>
<style>{"".join(css)}</style>
<defs>
{"".join(defs)}
<clipPath id="card"><rect width="{LARGURA}" height="{altura}" rx="18"/></clipPath>
<linearGradient id="esq" x1="0" x2="1"><stop offset="0" stop-color="{FUNDO}"/><stop offset="1" stop-color="{FUNDO}" stop-opacity="0"/></linearGradient>
<linearGradient id="dir" x1="0" x2="1"><stop offset="0" stop-color="{FUNDO}" stop-opacity="0"/><stop offset="1" stop-color="{FUNDO}"/></linearGradient>
<radialGradient id="brilho" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="{AZUL}" stop-opacity=".22"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#card)">
<rect width="{LARGURA}" height="{altura}" fill="{FUNDO}"/>
<rect width="{LARGURA}" height="{altura}" fill="url(#brilho)"/>
{"".join(c for c in corpo if c.startswith("<g"))}
<rect width="90" height="{altura}" fill="url(#esq)"/>
<rect x="{LARGURA - 90}" width="90" height="{altura}" fill="url(#dir)"/>
{"".join(c for c in corpo if not c.startswith("<g"))}
</g>
<rect x=".5" y=".5" width="{LARGURA - 1}" height="{altura - 1}" rx="18" fill="none" stroke="{LINHA}"/>
</svg>
"""
open(SAIDA, "w").write(svg)
print(f"{SAIDA}: {len(svg) / 1024:.0f} KB, {len(ids)} ícones, {altura}px de altura")
