"""Gera painel vetorial executivo em SVG (1440x900) para instalações hidráulicas NBR 5626.

LOFRANO TECNOLOGIA.
Visualização técnica independente com isométrico esquemático, indicadores e tabelas normativas.
"""

from .domain import (
    ResultadoDimensionamento,
    formatar_milimetros_para_metros_br,
    formatar_mmca_para_mca_br,
    formatar_vazao_ls_br,
    formatar_velocidade_ms_br,
)


def gerar_painel_svg(resultado: ResultadoDimensionamento) -> str:
    """Gera infográfico vetorial SVG completo de 1440x900 pixels com alto contraste."""
    cor_bg = "#0B132B"
    cor_card = "#1C2541"
    cor_card_borda = "#3A506B"
    cor_texto_claro = "#FFFFFF"
    cor_texto_sec = "#A7BED3"
    cor_destaque_azul = "#48CAE4"
    cor_destaque_verde = "#06D6A0"
    cor_alerta_laranja = "#FFB703"

    status_badge = "CONFORME NBR 5626" if resultado.todos_criterios_atendidos else "REQUER ATENÇÃO"
    cor_status = cor_destaque_verde if resultado.todos_criterios_atendidos else cor_alerta_laranja

    svg_linhas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900">',
        f'  <defs>',
        f'    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'      <stop offset="0%" stop-color="#0A1128"/>',
        f'      <stop offset="100%" stop-color="#101F42"/>',
        f'    </linearGradient>',
        f'    <linearGradient id="pipeGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'      <stop offset="0%" stop-color="#0077B6"/>',
        f'      <stop offset="100%" stop-color="#00B4D8"/>',
        f'    </linearGradient>',
        f'    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">',
        f'      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>',
        f'    </filter>',
        f'  </defs>',
        f'  <!-- Fundo principal -->',
        f'  <rect width="1440" height="900" fill="url(#bgGrad)"/>',
        f'',
        f'  <!-- Cabeçalho Executivo -->',
        f'  <rect x="30" y="25" width="1380" height="85" rx="10" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1.5" filter="url(#cardShadow)"/>',
        f'  <text x="55" y="60" fill="{cor_texto_claro}" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="700">',
        f'    DIMENSIONAMENTO HIDRÁULICO PREDIAL · ABNT NBR 5626:2020',
        f'  </text>',
        f'  <text x="55" y="88" fill="{cor_texto_sec}" font-family="system-ui, -apple-system, sans-serif" font-size="14">',
        f'    Edificação: <tspan fill="{cor_destaque_azul}" font-weight="600">{resultado.nome_edificacao}</tspan> · Aritmética Racional Inteira (Zero Float) · Padrão LOFRANO TECNOLOGIA',
        f'  </text>',
        f'',
        f'  <!-- Status Badge -->',
        f'  <rect x="1170" y="45" width="220" height="42" rx="21" fill="{cor_status}" fill-opacity="0.15" stroke="{cor_status}" stroke-width="2"/>',
        f'  <circle cx="1195" cy="66" r="6" fill="{cor_status}"/>',
        f'  <text x="1212" y="72" fill="{cor_status}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700">',
        f'    {status_badge}',
        f'  </text>',
        f'',
        f'  <!-- 4 Cards de Indicadores de Desempenho (KPIs) -->',
        f'  <!-- Card 1: Vazão Provável -->',
        f'  <rect x="30" y="125" width="330" height="110" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="50" y="155" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="13">VAZÃO PROVÁVEL GLOBAL (Q)</text>',
        f'  <text x="50" y="195" fill="{cor_destaque_azul}" font-family="system-ui, sans-serif" font-size="28" font-weight="800">',
        f'    {formatar_vazao_ls_br(resultado.vazao_provavel_global_mls)}',
        f'  </text>',
        f'  <text x="50" y="222" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="12">',
        f'    Instalada: {formatar_vazao_ls_br(resultado.vazao_total_instalada_mls)} · ΣP: {resultado.soma_pesos_global_decimos // 10},{resultado.soma_pesos_global_decimos % 10}',
        f'  </text>',
        f'',
        f'  <!-- Card 2: Ponto Mais Desfavorável -->',
        f'  <rect x="380" y="125" width="330" height="110" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="400" y="155" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="13">PRESSÃO CRÍTICA (PONTO MAIS DESFAVORÁVEL)</text>',
        f'  <text x="400" y="195" fill="{cor_destaque_verde}" font-family="system-ui, sans-serif" font-size="28" font-weight="800">',
        f'    {formatar_mmca_para_mca_br(resultado.pressao_ponto_mais_desfavoravel_mmca)}',
        f'  </text>',
        f'  <text x="400" y="222" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="12">',
        f'    Nó terminal: {resultado.ponto_mais_desfavoravel_no} (Mínimo exigido: ≥ 1,00 m.c.a.)',
        f'  </text>',
        f'',
        f'  <!-- Card 3: Pressão Estática Máxima -->',
        f'  <rect x="730" y="125" width="330" height="110" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="750" y="155" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="13">PRESSÃO ESTÁTICA MÁXIMA NA REDE</text>',
        f'  <text x="750" y="195" fill="{cor_destaque_azul}" font-family="system-ui, sans-serif" font-size="28" font-weight="800">',
        f'    {formatar_mmca_para_mca_br(resultado.pressao_estatica_maxima_mmca)}',
        f'  </text>',
        f'  <text x="750" y="222" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="12">',
        f'    Nó: {resultado.ponto_maior_pressao_estatica_no} · Limite NBR 5626: ≤ 40,00 m.c.a.',
        f'  </text>',
        f'',
        f'  <!-- Card 4: Tubulações e Aparelhos -->',
        f'  <rect x="1080" y="125" width="330" height="110" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="1100" y="155" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="13">EXTENSÃO E APARELHOS</text>',
        f'  <text x="1100" y="195" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="28" font-weight="800">',
        f'    {resultado.total_trechos} trechos · {resultado.total_aparelhos} pontos',
        f'  </text>',
        f'  <text x="1100" y="222" fill="{cor_destaque_verde}" font-family="system-ui, sans-serif" font-size="12">',
        f'    Velocidade máx. controlada: v ≤ 3,00 m/s',
        f'  </text>',
        f'',
        f'  <!-- Painel Central Esquerdo: Tabela Detalhada de Trechos Dimensionados -->',
        f'  <rect x="30" y="255" width="880" height="580" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="50" y="285" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="16" font-weight="700">',
        f'    PLANILHA DE DIMENSIONAMENTO HIDRÁULICO DE TRECHOS (PVC NBR 5648)',
        f'  </text>',
        f'  <line x1="50" y1="300" x2="890" y2="300" stroke="{cor_card_borda}" stroke-width="1"/>',
        f'',
        f'  <!-- Cabeçalho da Tabela -->',
        f'  <text x="50" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">TRECHO</text>',
        f'  <text x="140" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">ROTA</text>',
        f'  <text x="240" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">ΣP</text>',
        f'  <text x="310" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">VAZÃO</text>',
        f'  <text x="400" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">DN / BITOLA</text>',
        f'  <text x="510" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">VELOCIDADE</text>',
        f'  <text x="630" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">PERDA (Δh)</text>',
        f'  <text x="750" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">P. DINÂMICA</text>',
        f'  <text x="850" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">STATUS</text>',
        f'  <line x1="50" y1="335" x2="890" y2="335" stroke="{cor_card_borda}" stroke-width="0.8"/>',
    ]

    # Renderizar até 12 trechos na tabela visual
    y_pos = 360
    for idx, t in enumerate(resultado.trechos[:12]):
        cor_linha_bg = "#223055" if idx % 2 == 1 else "none"
        if cor_linha_bg != "none":
            svg_linhas.append(f'  <rect x="45" y="{y_pos - 16}" width="850" height="26" fill="{cor_linha_bg}" rx="4"/>')

        soma_p_str = f"{t.soma_pesos_decimos // 10},{t.soma_pesos_decimos % 10}"
        cor_vel = cor_destaque_verde if t.velocidade_conforme else cor_alerta_laranja
        cor_pres = cor_destaque_verde if t.pressao_dinamica_conforme else cor_alerta_laranja
        status_txt = "OK" if (t.velocidade_conforme and t.pressao_dinamica_conforme) else "AVISO"

        svg_linhas.append(f'  <text x="50" y="{y_pos}" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="12" font-weight="600">{t.id_trecho}</text>')
        svg_linhas.append(f'  <text x="140" y="{y_pos}" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11">{t.no_origem} → {t.no_destino}</text>')
        svg_linhas.append(f'  <text x="240" y="{y_pos}" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="12">{soma_p_str}</text>')
        svg_linhas.append(f'  <text x="310" y="{y_pos}" fill="{cor_destaque_azul}" font-family="system-ui, sans-serif" font-size="12">{formatar_vazao_ls_br(t.vazao_projeto_mls)}</text>')
        svg_linhas.append(f'  <text x="400" y="{y_pos}" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="12" font-weight="700">DN {t.dn_selecionado} ({t.polegadas_ref})</text>')
        svg_linhas.append(f'  <text x="510" y="{y_pos}" fill="{cor_vel}" font-family="system-ui, sans-serif" font-size="12">{formatar_velocidade_ms_br(t.velocidade_mms)}</text>')
        svg_linhas.append(f'  <text x="630" y="{y_pos}" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="12">{formatar_mmca_para_mca_br(t.perda_carga_total_mmca)}</text>')
        svg_linhas.append(f'  <text x="750" y="{y_pos}" fill="{cor_pres}" font-family="system-ui, sans-serif" font-size="12" font-weight="700">{formatar_mmca_para_mca_br(t.pressao_dinamica_jusante_mmca)}</text>')
        svg_linhas.append(f'  <text x="850" y="{y_pos}" fill="{cor_pres}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">{status_txt}</text>')
        y_pos += 34

    # Painel Direito: Verificação nos Pontos de Utilização Sanitários
    svg_linhas.extend([
        f'',
        f'  <!-- Painel Central Direito: Aparelhos e Pontos de Utilização -->',
        f'  <rect x="930" y="255" width="480" height="580" rx="8" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1" filter="url(#cardShadow)"/>',
        f'  <text x="955" y="285" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="16" font-weight="700">',
        f'    PRESSÕES NOS PONTOS DE CONSUMO',
        f'  </text>',
        f'  <line x1="955" y1="300" x2="1390" y2="300" stroke="{cor_card_borda}" stroke-width="1"/>',
        f'',
        f'  <text x="955" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">NÓ</text>',
        f'  <text x="1010" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">APARELHO</text>',
        f'  <text x="1210" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">EXIGIDO</text>',
        f'  <text x="1290" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">REAL</text>',
        f'  <text x="1350" y="325" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">LAUDO</text>',
        f'  <line x1="955" y1="335" x2="1390" y2="335" stroke="{cor_card_borda}" stroke-width="0.8"/>',
    ])

    y_pc = 360
    for idx, pc in enumerate(resultado.pontos_consumo[:12]):
        cor_pc_bg = "#223055" if idx % 2 == 1 else "none"
        if cor_pc_bg != "none":
            svg_linhas.append(f'  <rect x="945" y="{y_pc - 16}" width="450" height="26" fill="{cor_pc_bg}" rx="4"/>')

        cor_laudo = cor_destaque_verde if pc.conforme else cor_alerta_laranja
        laudo_txt = "CONFORME" if pc.conforme else "BAIXA"

        # Truncar nome se for muito longo
        nome_curto = pc.nome_aparelho if len(pc.nome_aparelho) <= 24 else pc.nome_aparelho[:22] + "..."

        svg_linhas.append(f'  <text x="955" y="{y_pc}" fill="{cor_destaque_azul}" font-family="system-ui, sans-serif" font-size="12" font-weight="600">{pc.no}</text>')
        svg_linhas.append(f'  <text x="1010" y="{y_pc}" fill="{cor_texto_claro}" font-family="system-ui, sans-serif" font-size="11">{nome_curto}</text>')
        svg_linhas.append(f'  <text x="1210" y="{y_pc}" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="11">{formatar_mmca_para_mca_br(pc.pressao_minima_exigida_mmca)}</text>')
        svg_linhas.append(f'  <text x="1290" y="{y_pc}" fill="{cor_laudo}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">{formatar_mmca_para_mca_br(pc.pressao_dinamica_real_mmca)}</text>')
        svg_linhas.append(f'  <text x="1350" y="{y_pc}" fill="{cor_laudo}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">{laudo_txt}</text>')
        y_pc += 34

    # Rodapé institucional
    svg_linhas.extend([
        f'',
        f'  <!-- Rodapé -->',
        f'  <rect x="30" y="850" width="1380" height="35" rx="6" fill="{cor_card}" stroke="{cor_card_borda}" stroke-width="1"/>',
        f'  <text x="50" y="872" fill="{cor_texto_sec}" font-family="system-ui, sans-serif" font-size="12">',
        f'    LOFRANO TECNOLOGIA · Zero Dependências Externas (Python Standard Library) · Conformidade Normativa com ABNT NBR 5626:2020 e NBR 5648',
        f'  </text>',
        f'  <text x="1390" y="872" fill="{cor_destaque_azul}" font-family="system-ui, sans-serif" font-size="12" font-weight="600" text-anchor="end">',
        f'    v1.0.0 · Código Aberto MIT',
        f'  </text>',
        f'</svg>',
    ])

    return "\n".join(svg_linhas) + "\n"
