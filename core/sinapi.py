# Multiplicador regional de preco, baseado na media das composicoes
# SINAPI por estado (fonte: CEF/IBGE, ref. Jun/2026). Nao e uma
# importacao completa da tabela oficial (que tem milhares de itens por
# estado) -- e uma aproximacao: pega a media geral de cada estado e
# calcula o quanto ele fica acima/abaixo da media nacional, aplicando
# esse fator sobre os precos base fixos do calculator.py.
#
# Para manter atualizado de verdade, os valores devem ser conferidos
# periodicamente em https://buscadorsinapi.com.br/estados (ou direto
# no portal oficial da Caixa) e recalculados.
MULTIPLICADOR_POR_ESTADO = {
    "AC": 1.219, "AL": 0.929, "AM": 1.106, "AP": 1.056, "BA": 1.008,
    "CE": 0.931, "DF": 0.993, "ES": 1.003, "GO": 0.952, "MA": 1.001,
    "MG": 0.949, "MS": 0.926, "MT": 1.060, "PA": 1.021, "PB": 0.925,
    "PE": 0.911, "PI": 1.034, "PR": 1.010, "RJ": 1.028, "RN": 0.963,
    "RO": 1.094, "RR": 1.070, "RS": 0.946, "SC": 1.021, "SE": 0.940,
    "SP": 0.956, "TO": 0.948,
}

NOMES_ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
    "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí",
    "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo",
    "TO": "Tocantins",
}

# Preco REAL (nao aproximado) do insumo SINAPI 32 -- ACO CA-50, 6,3MM,
# VERGALHAO (R$/KG), desonerado, por estado. Fonte: buscadorsinapi.com.br
# (dados oficiais Caixa/IBGE), referencia Abr/2026. Coletado insumo por
# insumo -- diferente do MULTIPLICADOR_POR_ESTADO acima, que e uma
# aproximacao pela media geral do estado. Esse e o modelo/padrao para
# ir substituindo os demais materiais por precos reais, um de cada vez.
PRECO_ACO_CA50_POR_ESTADO = {
    "AC": 10.48, "AL": 10.09, "AP": 9.32, "AM": 9.12, "BA": 7.43,
    "CE": 7.55, "DF": 8.24, "ES": 9.38, "GO": 7.12, "MA": 8.44,
    "MT": 8.83, "MS": 8.18, "MG": 7.17, "PA": 8.00, "PB": 7.71,
    "PR": 7.51, "PE": 7.99, "PI": 8.57, "RJ": 8.74, "RN": 8.52,
    "RS": 8.01, "RO": 9.91, "RR": 9.38, "SC": 7.68, "SP": 6.51,
    "SE": 8.99, "TO": 7.51,
}

# Custo de MAO DE OBRA por servico, aproximado a partir das composicoes
# SINAPI (mao de obra separada do material em cada composicao oficial).
# Sao valores medios de referencia nacional, ainda nao coletados item a
# item -- servem como PONTO DE PARTIDA sugerido na tela, e devem ser
# SEMPRE editaveis pelo usuario.
#
# Servicos de piso e porta sao discriminados por CATEGORIA (seca/
# molhada/externa; interna/externa), porque o esforco de mao de obra
# muda de verdade entre elas -- piso de area molhada tem caimento e
# impermeabilizacao, porta externa exige mais alinhamento/vedacao.
MAO_DE_OBRA_POR_SERVICO = {
    "Alvenaria (assentamento)":              {"preco": 28.00, "unidade": "m2_parede"},
    "Assentamento de Piso (Área Seca)":      {"preco": 22.00, "unidade": "m2_piso_seco"},
    "Assentamento de Piso (Área Molhada)":   {"preco": 32.00, "unidade": "m2_piso_molhado"},
    "Assentamento de Piso (Área Externa)":   {"preco": 26.00, "unidade": "m2_piso_externo"},
    "Pintura":                               {"preco": 12.00, "unidade": "m2_parede"},
    "Instalação de Porta Interna":           {"preco": 80.00, "unidade": "unidade"},
    "Instalação de Porta Externa":           {"preco": 115.00, "unidade": "unidade"},
    "Instalação de Janela":                  {"preco": 70.00, "unidade": "unidade"},
    "Execução de Cobertura":                 {"preco": 45.00, "unidade": "m2_cobertura"},
    "Estrutura (fundação/armação)":          {"preco": 35.00, "unidade": "m2_area"},
    "Instalação Elétrica":                   {"preco": 60.00, "unidade": "unidade"},
    "Instalação Hidráulica":                 {"preco": 55.00, "unidade": "unidade"},
}


def obter_multiplicador(estado_uf):
    """Retorna o multiplicador de preco para a UF informada.
    Se a UF nao for reconhecida, retorna 1.0 (preco base, sem ajuste)."""
    return MULTIPLICADOR_POR_ESTADO.get(estado_uf, 1.0)
