from core.models import DadosExtracao, ItemOrcamento, itens_para_dicts
from core.sinapi import obter_multiplicador, PRECO_ACO_CA50_POR_ESTADO, MAO_DE_OBRA_POR_SERVICO

# Margem de perda padrao da obra (10%)
MARGEM_PERDA = 1.1

# --- Coeficientes de consumo (por m2 ou metro linear) ---
CONSUMO_TIJOLO_POR_M2_PAREDE = 27      # blocos por m2 de parede
CONSUMO_CIMENTO_SACO_POR_M2 = 7        # sacos de 50kg por m2 de piso
CONSUMO_AREIA_M3_POR_M2 = 0.5          # m3 por m2 de piso
CONSUMO_BRITA_M3_POR_M2 = 0.3          # m3 por m2 de piso
CONSUMO_ACO_KG_POR_M2 = 6              # kg de vergalhao por m2 de piso
M2_POR_PONTO_ELETRICO = 5              # 1 ponto eletrico a cada 5m2
M2_POR_PONTO_HIDRAULICO = 8            # 1 ponto hidraulico a cada 8m2

# --- Precos base por padrao de acabamento (R$), antes do fator regional ---
PRECOS_PISO_SECO = {"Econômico": 35.00, "Médio": 55.00, "Alto Padrão": 89.90}
PRECOS_PISO_MOLHADO = {"Econômico": 28.00, "Médio": 42.00, "Alto Padrão": 68.00}
PRECOS_PISO_EXTERNO = {"Econômico": 38.00, "Médio": 58.00, "Alto Padrão": 95.00}
PRECOS_PORTA_INTERNA = {"Econômico": 150.00, "Médio": 260.00, "Alto Padrão": 480.00}
PRECOS_PORTA_EXTERNA = {"Econômico": 280.00, "Médio": 480.00, "Alto Padrão": 850.00}
PRECOS_JANELA = {"Econômico": 150.00, "Médio": 280.00, "Alto Padrão": 590.00}
PRECOS_PONTO_ELETRICO = {"Econômico": 85.00, "Médio": 110.00, "Alto Padrão": 150.00}
PRECOS_PONTO_HIDRAULICO = {"Econômico": 110.00, "Médio": 140.00, "Alto Padrão": 190.00}
# Custo de cobertura por m2 de area de piso, por tipo x padrao.
PRECOS_COBERTURA = {
    "Telhado": {"Econômico": 75.00, "Médio": 110.00, "Alto Padrão": 165.00},
    "Laje": {"Econômico": 95.00, "Médio": 140.00, "Alto Padrão": 210.00},
}
# Preco base fixo (nao varia por padrao de acabamento)
PRECO_BLOCO_CERAMICO = 1.25
PRECO_ARGAMASSA_KG = 1.80
PRECO_TINTA_L = 22.00
PRECO_CIMENTO_SACO = 44.00   # Ref. SINAPI/IBGE 1o bim/2026 (media nacional ~R$46/saco)
PRECO_AREIA_M3 = 120.00
PRECO_BRITA_M3 = 140.00
PRECO_ACO_FALLBACK = 8.38    # Media nacional, usado se o estado nao tiver preco real coletado


def _dados_extracao(dados) -> DadosExtracao:
    """Aceita tanto um DadosExtracao pronto quanto um dict cru (formato
    antigo), para nao quebrar chamadores externos durante a transicao."""
    return dados if isinstance(dados, DadosExtracao) else DadosExtracao.from_dict(dados)


def calcular_materiais(dados, padrao, estado_uf="SP", tipo_cobertura="Telhado"):
    """Calcula os itens de MATERIAL do orcamento. Retorna uma lista de
    dicts (Tipo/Material/Quantidade/Preco_Unit/Total), formato esperado
    por core/reporter.py e core/proposta_pdf.py."""
    d = _dados_extracao(dados)

    fator_regional = obter_multiplicador(estado_uf)
    area_cobertura = d.area_cobertura(tipo_cobertura)
    preco_aco_real = PRECO_ACO_CA50_POR_ESTADO.get(estado_uf, PRECO_ACO_FALLBACK)

    itens = [
        ItemOrcamento("Material", "Bloco Cerâmico 14x19x29",
                      round(d.area_parede * CONSUMO_TIJOLO_POR_M2_PAREDE * MARGEM_PERDA),
                      PRECO_BLOCO_CERAMICO * fator_regional),
        ItemOrcamento("Material", f"Piso Interno - Área Seca ({padrao})",
                      round(d.area_piso_seco * MARGEM_PERDA, 2),
                      PRECOS_PISO_SECO[padrao] * fator_regional),
        ItemOrcamento("Material", f"Piso Interno - Área Molhada ({padrao})",
                      round(d.area_piso_molhado * MARGEM_PERDA, 2),
                      PRECOS_PISO_MOLHADO[padrao] * fator_regional),
        ItemOrcamento("Material", f"Piso Externo ({padrao})",
                      round(d.area_piso_externo * MARGEM_PERDA, 2),
                      PRECOS_PISO_EXTERNO[padrao] * fator_regional),
        ItemOrcamento("Material", "Argamassa AC-II",
                      round(d.area_piso_total * 5 * MARGEM_PERDA),  # 5kg por m2
                      PRECO_ARGAMASSA_KG * fator_regional),
        ItemOrcamento("Material", "Tinta Acrílica Premium",
                      round(d.area_parede * 0.4),  # 0.4L por m2 de parede
                      PRECO_TINTA_L * fator_regional),
        ItemOrcamento("Material", f"Porta Interna ({padrao})",
                      d.portas_internas, PRECOS_PORTA_INTERNA[padrao] * fator_regional),
        ItemOrcamento("Material", f"Porta Externa ({padrao})",
                      d.portas_externas, PRECOS_PORTA_EXTERNA[padrao] * fator_regional),
        ItemOrcamento("Material", f"Janela ({padrao})",
                      d.janelas, PRECOS_JANELA[padrao] * fator_regional),
        ItemOrcamento("Material", f"Cobertura em {tipo_cobertura} ({padrao})",
                      area_cobertura, PRECOS_COBERTURA[tipo_cobertura][padrao] * fator_regional),
        ItemOrcamento("Material", "Cimento (Fundação/Estrutura)",
                      round(d.area_piso_total * CONSUMO_CIMENTO_SACO_POR_M2 * MARGEM_PERDA),
                      PRECO_CIMENTO_SACO * fator_regional),
        ItemOrcamento("Material", "Areia",
                      round(d.area_piso_total * CONSUMO_AREIA_M3_POR_M2 * MARGEM_PERDA, 2),
                      PRECO_AREIA_M3 * fator_regional),
        ItemOrcamento("Material", "Brita",
                      round(d.area_piso_total * CONSUMO_BRITA_M3_POR_M2 * MARGEM_PERDA, 2),
                      PRECO_BRITA_M3 * fator_regional),
        ItemOrcamento("Material", "Aço/Vergalhão",
                      round(d.area_piso_total * CONSUMO_ACO_KG_POR_M2 * MARGEM_PERDA),
                      preco_aco_real),
        ItemOrcamento("Material", f"Pontos Elétricos ({padrao})",
                      round(d.area_piso_total / M2_POR_PONTO_ELETRICO),
                      PRECOS_PONTO_ELETRICO[padrao] * fator_regional),
        ItemOrcamento("Material", f"Pontos Hidráulicos ({padrao})",
                      round(d.area_piso_total / M2_POR_PONTO_HIDRAULICO),
                      PRECOS_PONTO_HIDRAULICO[padrao] * fator_regional),
    ]

    return itens_para_dicts(itens)


def calcular_mao_de_obra(dados, estado_uf="SP", tipo_cobertura="Telhado"):
    """Gera as linhas de MAO DE OBRA por servico, com preco sugerido
    (baseado em composicoes SINAPI aproximadas -- ver core/sinapi.py).

    Retorna uma lista de dicts no MESMO FORMATO de calcular_materiais(),
    para poder ser concatenada num unico orcamento. O preco de cada
    linha e so uma SUGESTAO inicial -- a tela (app.py) deve deixar o
    usuario editar cada Preco_Unit, ja que mao de obra varia por equipe.
    """
    d = _dados_extracao(dados)
    fator_regional = obter_multiplicador(estado_uf)
    area_cobertura = d.area_cobertura(tipo_cobertura)

    # Mapa servico -> quantidade correspondente, usando a mesma unidade
    # de base declarada em MAO_DE_OBRA_POR_SERVICO.
    quantidades = {
        "Alvenaria (assentamento)": d.area_parede,
        "Assentamento de Piso (Área Seca)": d.area_piso_seco,
        "Assentamento de Piso (Área Molhada)": d.area_piso_molhado,
        "Assentamento de Piso (Área Externa)": d.area_piso_externo,
        "Pintura": d.area_parede,
        "Instalação de Porta Interna": d.portas_internas,
        "Instalação de Porta Externa": d.portas_externas,
        "Instalação de Janela": d.janelas,
        "Execução de Cobertura": area_cobertura,
        "Estrutura (fundação/armação)": d.area_piso_total,
        "Instalação Elétrica": round(d.area_piso_total / M2_POR_PONTO_ELETRICO),
        "Instalação Hidráulica": round(d.area_piso_total / M2_POR_PONTO_HIDRAULICO),
    }

    itens = [
        ItemOrcamento("Mão de Obra", servico, quantidades.get(servico, 0),
                      round(info["preco"] * fator_regional, 2))
        for servico, info in MAO_DE_OBRA_POR_SERVICO.items()
    ]

    return itens_para_dicts(itens)
