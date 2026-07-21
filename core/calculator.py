from core.sinapi import obter_multiplicador, PRECO_ACO_CA50_POR_ESTADO, MAO_DE_OBRA_POR_SERVICO


def calcular_materiais(dados, padrao, estado_uf="SP", tipo_cobertura="Telhado"):
    # Area total de piso (soma das 3 categorias) -- usada pra tudo que
    # nao depende do tipo de acabamento do piso (cobertura, estrutura,
    # pontos eletricos/hidraulicos).
    area_piso_seco = dados.get("area_piso_seco", 0)
    area_piso_molhado = dados.get("area_piso_molhado", 0)
    area_piso_externo = dados.get("area_piso_externo", 0)
    area_piso_total = area_piso_seco + area_piso_molhado + area_piso_externo

    metros_parede = dados["metros_parede"]
    portas_internas = dados.get("portas_internas", 0)
    portas_externas = dados.get("portas_externas", 0)
    janelas = dados.get("janelas", 0)

    # Margem de perda padrão da obra (10%)
    margem = 1.1

    # Definição de coeficientes de consumo por m² ou metro linear
    consumo_tijolo_por_m2 = 27  # blocos por m² de parede (assumindo pé direito de 2.8m)
    altura_parede = 2.8
    area_total_parede = metros_parede * altura_parede

    # Multiplicador regional baseado na media SINAPI do estado (ver
    # core/sinapi.py). Ajusta os precos base pra cima ou pra baixo
    # conforme o custo de construcao tipico da regiao.
    fator_regional = obter_multiplicador(estado_uf)

    # Preco por m² de PISO, discriminado por categoria de ambiente --
    # porcelanato (area seca) custa diferente de ceramica (area
    # molhada, banheiro/area de servico) e de piso externo
    # antiderrapante. Valores medios de mercado por padrao de
    # acabamento, ajustados pelo fator regional como os demais materiais.
    precos_piso_seco_por_padrao =    {"Econômico": 35.00, "Médio": 55.00, "Alto Padrão": 89.90}
    precos_piso_molhado_por_padrao = {"Econômico": 28.00, "Médio": 42.00, "Alto Padrão": 68.00}
    precos_piso_externo_por_padrao = {"Econômico": 38.00, "Médio": 58.00, "Alto Padrão": 95.00}

    # Preco de porta, discriminado por interna (mais simples) x externa
    # (reforcada, fechadura melhor, resistente a intemperie). Preco
    # medio unitario instalado, ajustado por padrao de acabamento.
    precos_porta_interna_por_padrao = {"Econômico": 150.00, "Médio": 260.00, "Alto Padrão": 480.00}
    precos_porta_externa_por_padrao = {"Econômico": 280.00, "Médio": 480.00, "Alto Padrão": 850.00}

    # Janela nao e discriminada por interna/externa -- janela e, por
    # natureza, sempre um elemento externo da edificacao.
    precos_janela_por_padrao = {"Econômico": 150.00, "Médio": 280.00, "Alto Padrão": 590.00}

    # Custo de cobertura por m² de area de piso. Telhado inclui telha +
    # madeiramento (estrutura de madeira) + cumeeira; laje inclui
    # concreto armado + ferragem. Valores medios de mercado, ajustados
    # por padrao de acabamento (telha ceramica x fibrocimento x
    # metalica, laje comum x laje com forro). Fator de 1.15 no telhado
    # cobre o beiral/inclinacao, que aumenta a area real de cobertura
    # em relacao a area de piso.
    precos_cobertura_m2 = {
        "Telhado": {"Econômico": 75.00, "Médio": 110.00, "Alto Padrão": 165.00},
        "Laje": {"Econômico": 95.00, "Médio": 140.00, "Alto Padrão": 210.00},
    }
    fator_area_cobertura = 1.15 if tipo_cobertura == "Telhado" else 1.0

    # Materiais estruturais adicionais, com coeficientes de consumo
    # por m² de area de piso TOTAL -- valores medios de referencia
    # para residencia simples (fundacao rasa/sapata corrida, sem
    # subsolo). Cimento e areia aqui sao para a estrutura
    # (fundacao/contrapiso), separados da Argamassa AC-II (assentamento
    # do piso, tambem proporcional a area total).
    consumo_cimento_saco_por_m2 = 7      # sacos de 50kg por m²
    consumo_areia_m3_por_m2 = 0.5        # m³ por m²
    consumo_brita_m3_por_m2 = 0.3        # m³ por m²
    consumo_aco_kg_por_m2 = 6            # kg de vergalhao por m²
    m2_por_ponto_eletrico = 5            # 1 ponto eletrico a cada 5m²
    m2_por_ponto_hidraulico = 8          # 1 ponto hidraulico a cada 8m²

    precos_ponto_eletrico_por_padrao = {"Econômico": 85.00, "Médio": 110.00, "Alto Padrão": 150.00}
    precos_ponto_hidraulico_por_padrao = {"Econômico": 110.00, "Médio": 140.00, "Alto Padrão": 190.00}

    # Dicionário de preços simulando o SINAPI para o MVP, já ajustado
    # pelo fator regional do estado da obra
    precos_sinapi = {
        "Bloco Cerâmico": 1.25 * fator_regional,
        "Piso Seco": precos_piso_seco_por_padrao[padrao] * fator_regional,
        "Piso Molhado": precos_piso_molhado_por_padrao[padrao] * fator_regional,
        "Piso Externo": precos_piso_externo_por_padrao[padrao] * fator_regional,
        "Argamassa (kg)": 1.80 * fator_regional,
        "Tinta (L)": 22.00 * fator_regional,
        "Porta Interna": precos_porta_interna_por_padrao[padrao] * fator_regional,
        "Porta Externa": precos_porta_externa_por_padrao[padrao] * fator_regional,
        "Janela": precos_janela_por_padrao[padrao] * fator_regional,
        "Cobertura": precos_cobertura_m2[tipo_cobertura][padrao] * fator_regional,
        "Cimento (saco 50kg)": 32.00 * fator_regional,
        "Areia (m³)": 120.00 * fator_regional,
        "Brita (m³)": 140.00 * fator_regional,
        "Ponto Elétrico": precos_ponto_eletrico_por_padrao[padrao] * fator_regional,
        "Ponto Hidráulico": precos_ponto_hidraulico_por_padrao[padrao] * fator_regional,
    }
    # Preco REAL do aco CA-50, coletado do SINAPI (nao mais aproximacao
    # pelo multiplicador regional). Fallback para media nacional (8.38)
    # se o estado nao estiver na tabela.
    preco_aco_real = PRECO_ACO_CA50_POR_ESTADO.get(estado_uf, 8.38)

    # Cálculos de Quantidade
    qtd_tijolos = round(area_total_parede * consumo_tijolo_por_m2 * margem)
    qtd_piso_seco = round(area_piso_seco * margem, 2)
    qtd_piso_molhado = round(area_piso_molhado * margem, 2)
    qtd_piso_externo = round(area_piso_externo * margem, 2)
    qtd_argamassa = round(area_piso_total * 5 * margem)  # 5kg por m²
    qtd_tinta = round(area_total_parede * 0.4)  # 0.4L por m²
    qtd_cobertura = round(area_piso_total * fator_area_cobertura, 2)
    qtd_cimento = round(area_piso_total * consumo_cimento_saco_por_m2 * margem)
    qtd_areia = round(area_piso_total * consumo_areia_m3_por_m2 * margem, 2)
    qtd_brita = round(area_piso_total * consumo_brita_m3_por_m2 * margem, 2)
    qtd_aco = round(area_piso_total * consumo_aco_kg_por_m2 * margem)
    qtd_pontos_eletricos = round(area_piso_total / m2_por_ponto_eletrico)
    qtd_pontos_hidraulicos = round(area_piso_total / m2_por_ponto_hidraulico)

    # Montagem do orçamento final combinando quantitativos e custos.
    # Linhas de piso/porta com quantidade 0 ainda entram na lista (ex:
    # planta sem area externa) -- simplesmente somam R$0,00, o que é
    # mais transparente do que esconder a linha.
    orcamento = [
        {"Tipo": "Material", "Material": "Bloco Cerâmico 14x19x29", "Quantidade": qtd_tijolos, "Preco_Unit": precos_sinapi["Bloco Cerâmico"]},
        {"Tipo": "Material", "Material": f"Piso Interno - Área Seca ({padrao})", "Quantidade": qtd_piso_seco, "Preco_Unit": precos_sinapi["Piso Seco"]},
        {"Tipo": "Material", "Material": f"Piso Interno - Área Molhada ({padrao})", "Quantidade": qtd_piso_molhado, "Preco_Unit": precos_sinapi["Piso Molhado"]},
        {"Tipo": "Material", "Material": f"Piso Externo ({padrao})", "Quantidade": qtd_piso_externo, "Preco_Unit": precos_sinapi["Piso Externo"]},
        {"Tipo": "Material", "Material": "Argamassa AC-II", "Quantidade": qtd_argamassa, "Preco_Unit": precos_sinapi["Argamassa (kg)"]},
        {"Tipo": "Material", "Material": "Tinta Acrílica Premium", "Quantidade": qtd_tinta, "Preco_Unit": precos_sinapi["Tinta (L)"]},
        {"Tipo": "Material", "Material": f"Porta Interna ({padrao})", "Quantidade": portas_internas, "Preco_Unit": precos_sinapi["Porta Interna"]},
        {"Tipo": "Material", "Material": f"Porta Externa ({padrao})", "Quantidade": portas_externas, "Preco_Unit": precos_sinapi["Porta Externa"]},
        {"Tipo": "Material", "Material": f"Janela ({padrao})", "Quantidade": janelas, "Preco_Unit": precos_sinapi["Janela"]},
        {"Tipo": "Material", "Material": f"Cobertura em {tipo_cobertura} ({padrao})", "Quantidade": qtd_cobertura, "Preco_Unit": precos_sinapi["Cobertura"]},
        {"Tipo": "Material", "Material": "Cimento (Fundação/Estrutura)", "Quantidade": qtd_cimento, "Preco_Unit": precos_sinapi["Cimento (saco 50kg)"]},
        {"Tipo": "Material", "Material": "Areia", "Quantidade": qtd_areia, "Preco_Unit": precos_sinapi["Areia (m³)"]},
        {"Tipo": "Material", "Material": "Brita", "Quantidade": qtd_brita, "Preco_Unit": precos_sinapi["Brita (m³)"]},
        {"Tipo": "Material", "Material": "Aço/Vergalhão", "Quantidade": qtd_aco, "Preco_Unit": preco_aco_real},
        {"Tipo": "Material", "Material": f"Pontos Elétricos ({padrao})", "Quantidade": qtd_pontos_eletricos, "Preco_Unit": precos_sinapi["Ponto Elétrico"]},
        {"Tipo": "Material", "Material": f"Pontos Hidráulicos ({padrao})", "Quantidade": qtd_pontos_hidraulicos, "Preco_Unit": precos_sinapi["Ponto Hidráulico"]},
    ]

    # Calcula os totais por linha
    for item in orcamento:
        item["Total"] = round(item["Quantidade"] * item["Preco_Unit"], 2)

    return orcamento


def calcular_mao_de_obra(dados, estado_uf="SP", tipo_cobertura="Telhado"):
    """Gera as linhas de MAO DE OBRA por servico, com preco sugerido
    (baseado em composicoes SINAPI aproximadas -- ver core/sinapi.py).

    Retorna uma lista no MESMO FORMATO das linhas de material
    (Tipo/Material/Quantidade/Preco_Unit/Total), para poder ser
    concatenada com o resultado de calcular_materiais() num unico
    orcamento. O preco de cada linha aqui e so uma SUGESTAO inicial --
    a tela (app.py) deve deixar o usuario editar cada Preco_Unit antes
    de gerar o relatorio final, ja que mao de obra varia por equipe.
    """
    area_piso_seco = dados.get("area_piso_seco", 0)
    area_piso_molhado = dados.get("area_piso_molhado", 0)
    area_piso_externo = dados.get("area_piso_externo", 0)
    area_piso_total = area_piso_seco + area_piso_molhado + area_piso_externo

    metros_parede = dados["metros_parede"]
    portas_internas = dados.get("portas_internas", 0)
    portas_externas = dados.get("portas_externas", 0)
    janelas = dados.get("janelas", 0)

    altura_parede = 2.8
    area_total_parede = metros_parede * altura_parede
    fator_area_cobertura = 1.15 if tipo_cobertura == "Telhado" else 1.0
    area_cobertura = round(area_piso_total * fator_area_cobertura, 2)

    m2_por_ponto_eletrico = 5
    m2_por_ponto_hidraulico = 8
    qtd_pontos_eletricos = round(area_piso_total / m2_por_ponto_eletrico)
    qtd_pontos_hidraulicos = round(area_piso_total / m2_por_ponto_hidraulico)

    fator_regional = obter_multiplicador(estado_uf)

    # Mapa servico -> quantidade correspondente, usando a mesma unidade
    # de base declarada em MAO_DE_OBRA_POR_SERVICO.
    quantidades = {
        "Alvenaria (assentamento)": area_total_parede,
        "Assentamento de Piso (Área Seca)": area_piso_seco,
        "Assentamento de Piso (Área Molhada)": area_piso_molhado,
        "Assentamento de Piso (Área Externa)": area_piso_externo,
        "Pintura": area_total_parede,
        "Instalação de Porta Interna": portas_internas,
        "Instalação de Porta Externa": portas_externas,
        "Instalação de Janela": janelas,
        "Execução de Cobertura": area_cobertura,
        "Estrutura (fundação/armação)": area_piso_total,
        "Instalação Elétrica": qtd_pontos_eletricos,
        "Instalação Hidráulica": qtd_pontos_hidraulicos,
    }

    mao_de_obra = []
    for servico, info in MAO_DE_OBRA_POR_SERVICO.items():
        quantidade = quantidades.get(servico, 0)
        preco_unit = round(info["preco"] * fator_regional, 2)
        mao_de_obra.append({
            "Tipo": "Mão de Obra",
            "Material": servico,
            "Quantidade": quantidade,
            "Preco_Unit": preco_unit,
        })

    for item in mao_de_obra:
        item["Total"] = round(item["Quantidade"] * item["Preco_Unit"], 2)

    return mao_de_obra
