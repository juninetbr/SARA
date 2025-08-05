import streamlit as st
import re

st.markdown("""
<style>
body, .stApp { background-color: #0B2611 !important; color: #B2F2BB; }
.stButton>button {
    color: #fff;
    background: linear-gradient(90deg, #2EB82E 0%, #006600 100%) !important;
    border: 1px solid #00FF00;
    border-radius: 8px;
    font-weight: bold;
    font-size: 18px;
    padding: 0.4em 2em !important;
}
.analysis-bubble {
    background: #153715;
    border-left: 4px solid #00FF00;
    padding: 1em;
    border-radius: 12px;
    margin-bottom: 1.5em;
    color: #A9FFA9;
    font-family: 'Consolas', monospace;
}
.user-bubble {
    background: #204220;
    padding: 1em;
    border-radius: 10px;
    margin-bottom: 1em;
    color: #D0FFCE;
    font-style: italic;
}
.risk-highlight {
    color: #00FF00;
    font-weight: bold;
    background: #013300;
    border-radius: 6px;
    padding: 3px 8px;
}
.tip-highlight {
    color: #00FF00;
    background: #003300;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 10px;
    display: block;
}
.footer-signature {
    font-family: 'Courier New', Courier, monospace;
    text-align: center;
    margin-top: 40px;
    color: #3BCB57;
    font-weight: bold;
    font-size: 16px;
}
</style>

<div class="footer-signature">
    Desenvolvido por Jairo Sousa
</div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#F1C40F;'>🕵️‍♀️ SARA — Sistema de Análise de Risco Automatizado</h1>", unsafe_allow_html=True)
st.markdown("**Converse com a SARA! Digite o caso/relato do cliente e receba orientação investigativa prática.**<br><span style='font-size:15px;color:#BBB;'>Exemplo: 'Cliente CPF recém-aberto, DDD 011, TPV 200mil, pediu 8 máquinas Smart, aceitou taxas sem negociar, CNAE divergente, comprovante: print nada a ver'</span>", unsafe_allow_html=True)
user_input = st.text_area("🕵️‍♀️ O que você observou nesse atendimento?", height=120)

def avaliar_risco_completo(relato):
    relato = relato.lower()
    motivos = []
    dicas_extra = []
    perguntas_recomendadas = []
    sugestoes = set()

    # --- DETECÇÃO DE TIPOS E ATRIBUTOS ---
    cnpj_novo = any(x in relato for x in [
        "cnpj novo", "cnpj criado há 30 dias", "cnpj aberto há 30 dias",
        "cnpj criado recentemente", "cnpj aberto recentemente", "cnpj recente"
    ])
    cnae_div = any(x in relato for x in [
        "cnae diferente", "cnae divergente", "atividade diferente", "ramo divergente"
    ])
    aceitou_sem_negociar = any(x in relato for x in [
        "aceitou proposta sem negociar", "aceitou taxa sem negociar", "aceitou taxa", "aceitaram sem negociar", "aceitou proposta", "não negociou taxa"
    ])
    ramo_alimenticio = any(x in relato for x in [
        "alimentício", "restaurante", "bar", "lanchonete", "marmita", "food", "pizzaria", "padaria", "cafeteria", "mercearia"
    ])
    ddd_sp = bool(re.search(r"\b0?(11|12|13|14|15|16|17|18|19)\b", relato))
    modelos_risco = any(m in relato for m in [
        "smart", "p2", "pinpad", "pin pad", "wisepad"
    ])
    flex = any(k in relato for k in [
        "pré-ativa", "preativa", "plano flex", "transferido do front", "conta pré-ativa"
    ])
    maquinas_regex = re.search(r"(\d+)\s*(máquina|maquinas|maquininhas|maquininha)", relato)
    num_maquinas = int(maquinas_regex.group(1)) if maquinas_regex else 0

    # TPV
    tpv_val = 0
    tpv_regex = re.search(r"tpv.*?([\d\.\-, ]+)(mil|k|mil reais|reais)?", relato)
    if tpv_regex:
        val = tpv_regex.group(1).replace(".", "").replace(",", "").replace("-", "").replace(" ", "")
        try: tpv_val = int(val)
        except: tpv_val = 0
        if tpv_regex.group(2): tpv_val *= 1000

    # Comprovante de atividade válido?
    comprovante_keywords = [
        "comprovante de atividade", "fachada", "instagram", "nota fiscal", "cartão",
        "extrato", "foto da empresa", "comprovação válida", "comprovante válido", "rede social"
    ]
    comprovante_valido = any(c in relato for c in comprovante_keywords)

    cpf_presente = "cpf" in relato
    cnpj_presente = "cnpj" in relato

    # ---- ANÁLISE E LÓGICA ROBUSTA ----
    # 1. CNPJ novo + sem comprovante
    if cnpj_presente and cnpj_novo and not comprovante_valido:
        motivos.append("CNPJ recém-aberto sem comprovação de atividade")
        dicas_extra.append("<span class='tip-highlight'>🟡 Nunca credencie empresas recém-abertas sem documentação real do funcionamento! Exija fotos, extratos, presença digital, nota fiscal emitida etc.</span>")
        perguntas_recomendadas.append("<span class='q-highlight'>Cliente tem comprovação clara e legítima que está realmente ativo? Essa foto/comprovante faz sentido?</span>")
    
    # 2. CNPJ novo + comprovante OK
    if cnpj_presente and cnpj_novo and comprovante_valido:
        motivos.append("CNPJ novo, apresentou comprovante válido")
        dicas_extra.append("<span class='tip-highlight' style='color:#37FF8B;background:#112919;'>🟢 Cliente apresentou documentação. Cheque autenticidade e mantenha monitoramento nas primeiras semanas.</span>")
        perguntas_recomendadas.append("<span class='q-highlight'>Comprovante fornecido é óbvio e legítimo, ou apenas uma foto genérica? Há indícios de operação real?</span>")

    # 3. TPV muito alto (>100mil) SEM comprovante
    if tpv_val > 100000 and not comprovante_valido:
        motivos.append("TPV muito alto sem comprovante de atividade válido")
        dicas_extra.append("<span class='tip-highlight'>🟡 Nunca aceite TPV elevado sem comprovação externa! Empresas que vendem muito têm como provar rapidamente a operação.</span>")
        perguntas_recomendadas.append("<span class='q-highlight'>Solicite evidências proporcionais ao TPV informado.</span>")

    # 4. TPV alto COM comprovante válido
    if tpv_val > 100000 and comprovante_valido:
        motivos.append("TPV alto, comprovante apresentado")  # isso NÃO é risco
        dicas_extra.append("<span class='tip-highlight' style='color:#37FF8B;background:#112919;'>🟢 Cliente demonstrou/confirmou operações robustas. Acompanhe primeiras movimentações e siga rotina normal.</span>")

    # 5. Aceitou tudo sem negociar
    if aceitou_sem_negociar:
        motivos.append("Aceitou taxa/proposta sem negociar")
        dicas_extra.append("<span class='tip-highlight'>🟡 Clientes legítimos tendem a negociar taxas. Questione as referências do cliente, peça para comparar condições em outros bancos/adquirentes.</span>")
        perguntas_recomendadas.append("<span class='q-highlight'>Você já comparou nossas condições com outras empresas? Por que aceitou tudo tão rápido?</span>")

    # 6. CNAE divergente
    if cnae_div:
        motivos.append("CNAE divergente do segmento declarado")
        dicas_extra.append("<span class='tip-highlight'>🟡 CNAE incoerente geralmente é sinal de que algo está escondido. Considere contato extra/consulta Sintegra e Google Maps.</span>")
        perguntas_recomendadas.append("<span class='q-highlight'>O CNAE do CNPJ bate com o segmento que o cliente diz operar? Ele apresentou documentação do ramo ou só há divergência?</span>")

    # 7. Muitos sinais conhecidos (máquinas, modelo)
    if num_maquinas >= 7:
        motivos.append(f"Solicitação de {num_maquinas} máquinas")
        perguntas_recomendadas.append("<span class='q-highlight'>Por que tantas máquinas? Negócios legítimos com alto volume tendem a provar demanda por fotos/vídeos de balcão, equipe etc.</span>")
    if modelos_risco:
        motivos.append("Insistência por modelos Smart/P2/Pinpad")
        perguntas_recomendadas.append("<span class='q-highlight'>Por que exige esse modelo? Qual diferença para o negócio? Exija argumentos reais.</span>")
    if flex:
        motivos.append("Conta pré-ativa/plano Flex transferido")
        dicas_extra.append("<span class='tip-highlight'>🟡 Fique atento a fluxos pulados: fraude pode começar por facilitar demais onboarding.</span>")

    if ramo_alimenticio:
        motivos.append("Ramo alimentício")
        perguntas_recomendadas.append("<span class='q-highlight'>O faturamento e quantidade de máquinas fazem sentido para o tamanho e perfil do estabelecimento?</span>")

    # Recorrências documentais...
    if cpf_presente and not comprovante_valido:
        motivos.append("CPF sem comprovante de atividade")
        perguntas_recomendadas.append("<span class='q-highlight'>NUNCA credencie CPF sem documento real. Tudo deve ser validado na fonte.</span>")
    if "sem comprovante de atividade" in relato:
        motivos.append("Cliente afirmou ausência de comprovante de atividade")
        dicas_extra.append("<span class='tip-highlight'>🟡 Falta de comprovante é sempre motivo de investigação extra.</span>")

    # Sinais extras para reforçar a cultura de não-credenciamento fácil
    blacklist = ["fraude", "golpe", "documento falso", "nome sujo"]
    if any(bl in relato for bl in blacklist):
        motivos.append("Alerta: possível fraude conhecida no atendimento!")
        dicas_extra.append("<span class='tip-highlight'>🚨 Avalie imediatamente com o time de prevenção!</span>")

    # Recomendações extras geral
    sugestoes.update([
        "Use o Google Maps para checar lojas e endereços.",
        "Pesquise o nome, telefone e razão social do cliente nos órgãos de proteção ao crédito.",
        "Sempre peça nota fiscal, extrato, contrato social e demais provas que confirmem o modelo de negócio.",
        "Confirme, se possível, que a pessoa apresentada como proprietário é mesmo quem movimenta o negócio.",
        "Desconfie de pressa/desinteresse em apresentar documentação."
    ])

    # --- Lógica combinada para risco ---
    alto_riscos = [
        "CNPJ recém-aberto sem comprovação de atividade",
        "TPV muito alto sem comprovante de atividade válido",
        "CPF sem comprovante de atividade",
        "Cliente afirmou ausência de comprovante de atividade",
        "Solicitação de 7 máquinas",
        "Solicitação de 8 máquinas",
        "Insistência por modelos Smart/P2/Pinpad",
        "Conta pré-ativa/plano Flex transferido",
        "Aceitou taxa/proposta sem negociar",
        "CNAE divergente do segmento declarado",
        "Alerta: possível fraude conhecida no atendimento!"
    ]
    risco_encontrado = any(r in motivos for r in alto_riscos)
    motivos_destacados = ", ".join([f"<span class='risk-highlight'>{m}</span>" for m in motivos]) if motivos else 'Nenhum motivo crítico identificado.'

    # --- Resposta composta: balão, motivos, dicas e perguntas ---
    if risco_encontrado:
        resposta = (
            f"<div class='analysis-bubble'>🕵️‍♀️ <span class='risk-highlight'>RISCO ENCONTRADO</span>.<br>"
            f"<b>Motivos:</b> {motivos_destacados}<br>"
            + "".join(dicas_extra)
            + "<br><b>Perguntas de investigação para você fazer ao cliente:</b><ul>"
            + "".join([f"<li>{p}</li>" for p in perguntas_recomendadas]) + "</ul>"
            + "<br><b>Sugestões finais:</b><ul>"
            + "".join([f"<li>{s}</li>" for s in sorted(sugestoes)]) + "</ul>"
            + "🟡 <i>Alerta: Nunca credencie apenas por boa conversa ou promessas. Siga a trilha de documentação!</i></div>"
        )
    else:
        resposta = (
            "<div class='analysis-bubble' style='color:#37FF8B;border-left:4px solid #22AA73;'>"
            "🕵️‍♀️ <span class='risk-highlight' style='color:#37FF8B;'>CLIENTE SEM RISCO ENCONTRADO</span>.<br>"
            f"{''.join(dicas_extra)}"
            "<br><b>Motivos:</b> Nenhum motivo crítico encontrado.<br>"
            "<b>DICA:</b> Continue seguindo boas práticas de checagem e investigação.<br>"
            "<b>Pergunte-se sempre:</b> Você teria confiança em credenciar esse cliente se a receita fosse sua?</div>"
        )
    return resposta

if user_input:
    st.markdown(f"<div class='user-bubble'>💬 {user_input}</div>", unsafe_allow_html=True)
    st.markdown(avaliar_risco_completo(user_input), unsafe_allow_html=True)
else:
    st.info("Preencha a caixa acima com a descrição do caso de atendimento para análise investigativa.")

