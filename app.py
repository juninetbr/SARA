import streamlit as st
import re

st.set_page_config(
    page_title="SARA - Sistema de Análise de Risco Automatizado",
    page_icon="🕵️‍♀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
body, .stApp { background-color: #101824 !important; color: #E0E6EC; }
.stButton>button { 
    color: #fff;
    background: linear-gradient(90deg, #008B8B 0%, #00596d 100%) !important;
    border: 1px solid #F1C40F;
    border-radius: 5px;
    font-weight: bold;
    font-size: 18px;
    padding: 0.4em 2em !important;
}
.analysis-bubble {
    background: #172734;
    border-left: 4px solid #F1C40F;
    padding: 1em;
    border-radius: 10px;
    margin-bottom: 1.5em;
    color: #FFD700;
    font-family: 'Consolas', monospace;
}
.user-bubble {
    background: #23313D;
    padding: 1em;
    border-radius: 10px;
    margin-bottom: 1em;
    color: #B2DFDB;
    font-style: italic;
}
.risk-highlight {
    color: #FFD700;
    font-weight: bold;
    background: #14334B;
    border-radius: 5px;
    padding: 2px 6px;
}
.tip-highlight {
    color: #FFD700;
    background: #2b260b;
    border-radius: 6px;
    padding: 6px 12px;
    display: block;
    margin: 10px 0;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#F1C40F;'>🕵️‍♀️ SARA — Sistema de Análise de Risco Automatizado</h1>", unsafe_allow_html=True)
st.markdown("**Converse com a SARA! Digite o caso/relato do cliente para investigar juntas.**<br><span style='font-size:15px;color:#BBB;'>Exemplo: 'CPF, DDD 011, TPV 150mil, pediu 8 máquinas Smart, aceitou proposta sem negociar, CNAE divergente, CNPJ criado há 15 dias...'</span>", unsafe_allow_html=True)

user_input = st.text_area("🕵️‍♀️ O que você observou nesse atendimento?", height=120)

def avaliar_risco_completo(relato):
    relato = relato.lower()
    motivos = []
    sugestoes = set()
    dicas_extra = []

    # DDD São Paulo
    ddd_sp = False
    ddd_regex = re.compile(r"\b0?(11|12|13|14|15|16|17|18|19)\b")
    if ddd_regex.search(relato): motivos.append("DDD de São Paulo"); ddd_sp = True

    # Ramo alimentício
    ramos_alimenticios = ["alimentício", "restaurante", "bar", "lanchonete", "marmita", "food", "pizzaria", "padaria", "cafeteria", "mercearia"]
    ramo_ali = any(r in relato for r in ramos_alimenticios)
    if ramo_ali: motivos.append("Ramo alimentício")

    # TPV muito alto (> R$100.000)
    tpv_val = 0
    tpv_regex = re.search(r"tpv.*?([\d\.\-, ]+)(mil|k|mil reais|reais)?", relato)
    if tpv_regex:
        val = tpv_regex.group(1).replace(".", "").replace(",", "").replace("-", "").replace(" ", "")
        try:
            tpv_val = int(val)
        except: tpv_val = 0
        if tpv_regex.group(2): tpv_val *= 1000
    if ramo_ali and tpv_val > 100000:
        motivos.append("TPV alimentício acima de R$100mil")

    # Muitas máquinas
    maquinas_regex = re.search(r"(\d+)\s*(máquina|maquinas|maquininhas|maquininha)", relato)
    if maquinas_regex and int(maquinas_regex.group(1)) >= 7:
        motivos.append(f"Solicitação de {maquinas_regex.group(1)} máquinas")

    # Modelos específicos
    modelos_suspeitos = ["smart", "p2", "pinpad", "pin pad"]
    if any(m in relato for m in modelos_suspeitos): motivos.append("Insistência por modelos Smart/P2/Pinpad")

    # Conta pré-ativa/plano Flex solicitado
    if any(t in relato for t in [
        "pré-ativa", "preativa", "plano flex", "transferido do front", "conta pré-ativa"
    ]):
        motivos.append("Conta pré-ativa e/ou plano Flex solicitado")

    # Cliente CPF sem comprovante de atividade (pontua para risco!)
    cpf_presente = re.search(r"cpf", relato) is not None
    comprovante_presente = any(c in relato for c in [
        "comprovante", "fachada", "instagram", "facebook", "nota fiscal", "cartão", "transacional", "extrato"
    ])
    if cpf_presente and not comprovante_presente:
        motivos.append("CPF sem comprovante de atividade")
    if "sem comprovante de atividade" in relato or (cpf_presente and not comprovante_presente):
        motivos.append("Cliente sem comprovante de atividade")

    # Aceitação rápida sem negociar
    aceitou_sem_negociar = any(
        frase in relato for frase in [
            "aceitou proposta sem negociar", "aceitou taxa sem negociar", "aceitou taxa", "aceitaram sem negociar", "aceitou proposta", "não negociou taxa"
        ]
    )
    if aceitou_sem_negociar:
        motivos.append("Aceitou proposta/taxa sem negociar")
        dicas_extra.append("<span class='tip-highlight'>🟡 Bastante atenção: clientes legítimos costumam negociar taxas ou propostas. Questione o cliente sobre ofertas da concorrência e o motivo da aceitação imediata!</span>")

    # CNAE divergente
    cnae_div = any(x in relato for x in ["cnae diferente", "cnae divergente", "atividade diferente", "ramo divergente"])
    if cnae_div:
        motivos.append("CNAE do CNPJ divergente do ramo informado")
        dicas_extra.append("<span class='tip-highlight'>🟡 Bastante atenção: Quando o CNAE do CNPJ não combina com o ramo de atividade informado, investigue documentação, histórico do negócio e consulte Sintegra/Receita Federal!</span>")

    # CNPJ recém-aberto
    cnpj_novo = any(x in relato for x in [
        "cnpj novo", "cnpj criado há 30 dias", "cnpj aberto há 30 dias", "cnpj criado recentemente", "cnpj aberto recentemente", "cnpj recente"
    ])
    if cnpj_novo:
        motivos.append("CNPJ criado nos últimos 30 dias")
        dicas_extra.append("<span class='tip-highlight'>🟡 Bastante atenção: Empresas recém-abertas podem indicar tentativa de fraude. Solicite fotos, extratos de bancos e outras comprovações de atividade real. Sempre questione histórico e motivos da abertura recente.</span>")

    # Verificação de endereço
    if "endereço" in relato or "endereço de entrega" in relato or "localização" in relato:
        sugestoes.add("Confirme se o endereço de entrega bate com o endereço do CNPJ e verifique no Google Maps se o local é idôneo.")
    # Recomendações padrão
    sugestoes.update([
        "Solicite comprovante de atividade (fachada, redes sociais, notas fiscais, cartão de visita, extrato de vendas).",
        "Pesquise o comprovante enviado no Google Imagens para verificar sua autenticidade.",
        "Questione a necessidade real se o cliente pedir muitas máquinas ou modelos específicos.",
        "Antes de credenciar, envie o APP e peça que o cliente realize o KYC."
    ])

    # Lógica para risco
    alto_riscos = [
        "TPV alimentício acima de R$100mil",
        "Solicitação de 7 máquinas", "Solicitação de 8 máquinas",
        "Insistência por modelos Smart/P2/Pinpad",
        "Conta pré-ativa e/ou plano Flex solicitado",
        "CPF sem comprovante de atividade",
        "Aceitou proposta/taxa sem negociar",
        "Cliente sem comprovante de atividade",
        "CNAE do CNPJ divergente do ramo informado",
        "CNPJ criado nos últimos 30 dias"
    ]
    risco_encontrado = False
    if ddd_sp and len(motivos) >= 4: risco_encontrado = True
    if any(r in motivos for r in alto_riscos): risco_encontrado = True

    motivos_destacados = ", ".join([f"<span class='risk-highlight'>{m}</span>" for m in motivos])
    if risco_encontrado:
        resposta = (
            f"<div class='analysis-bubble'>🕵️‍♀️ <span class='risk-highlight'>RISCO ENCONTRADO</span>.<br><b>Motivos:</b> {motivos_destacados}."
            + (f"<br>{''.join(dicas_extra)}" if dicas_extra else "")
            + "<br><b>Sugestões:</b><ul>"
            + "".join([f"<li>{s}</li>" for s in sorted(sugestoes)])
            + "</ul>🟡 <i>Alerta: Reforce a validação deste atendimento!</i></div>"
        )
    else:
        resposta = (
            "<div class='analysis-bubble' style='color:#37FF8B;border-left:4px solid #22AA73;'>"
            "🕵️‍♀️ <span class='risk-highlight' style='color:#37FF8B;'>CLIENTE SEM RISCO ENCONTRADO</span>.<br>"
            f"<b>Motivos:</b> {motivos_destacados if motivos else 'Nenhum motivo crítico identificado.'}"
            "<br>Continue seguindo boas práticas de checagem e validação."
            "</div>"
        )
    return resposta

if user_input:
    st.markdown(f"<div class='user-bubble'>💬 {user_input}</div>", unsafe_allow_html=True)
    st.markdown(avaliar_risco_completo(user_input), unsafe_allow_html=True)
else:
    st.info("Preencha a caixa acima com a descrição do caso de atendimento para análise investigativa.")
