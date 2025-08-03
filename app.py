import streamlit as st
import re

# Configuração inicial para tema visual (escuro, fontes e ícones)
st.set_page_config(
    page_title="SARA - Sistema de Análise de Risco Automatizado",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Instruções com toque investigativo
st.markdown("""
<style>
body, .stApp { background-color: #101824 !important; color: #E0E6EC; }
div[data-testid="stTextArea"] > div > textarea { background: #232d36 !important; color: #E0E6EC !important; font-size:16px;}
.css-1n76uvr { background: #232d36 !important; }
.stButton>button { 
    color: #fff;
    background: linear-gradient(90deg, #008B8B 0%, #00596d 100%) !important;
    border: 1px solid #F1C40F;
    border-radius: 5px;
    font-weight: bold;
    font-size: 18px;
    padding: 0.4em 2em !important;
}
.stTextInput, .stTextArea { border: 1px solid #F1C40F; }
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
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#F1C40F;'>🔎 SARA — Sistema de Análise Rápida Automatizado</h1>", unsafe_allow_html=True)
st.markdown("**Digite o caso/relato do cliente abaixo para investigação.**<br><span style='font-size:15px;color:#BBB;'>Exemplo: 'CPF, DDD 011, TPV 120mil, pediu 7 máquinas Smart, aceitou taxas, sem comprovante de atividade...'</span>", unsafe_allow_html=True)

user_input = st.text_area("🕵️‍♂️ O que você observou nesse atendimento?", height=120)

def avaliar_risco_completo(relato):
    relato = relato.lower()
    motivos = []
    sugestoes = []

    # DDD São Paulo
    ddd_sp = False
    ddd_regex = re.compile(r"\b0?(11|12|13|14|15|16|17|18|19)\b")
    if ddd_regex.search(relato): motivos.append("DDD de São Paulo"); ddd_sp = True

    # Ramo alimentício (robusto)
    ramos_alimenticios = ["alimentício", "restaurante", "bar", "lanchonete", "marmita", "food", "pizzaria", "padaria", "cafeteria", "mercearia"]
    if any(r in relato for r in ramos_alimenticios): motivos.append("Ramo alimentício")

    # TPV muito alto (> R$100.000)
    tpv_alto = False
    tpv_val = 0
    tpv_regex = re.search(r"tpv.*?([\d\.\-, ]+)(mil|k|\.|,)?", relato)
    if tpv_regex:
        val = tpv_regex.group(1).replace(".", "").replace(",", "").replace("-", "").replace(" ", "")
        try:
            tpv_val = int(val)
            if tpv_regex.group(2) and tpv_regex.group(2) in ["mil", "k"]: tpv_val *= 1000
            if tpv_val > 100000 and any(r in relato for r in ramos_alimenticios):
                motivos.append("TPV alimentício acima de R$100mil"); tpv_alto = True
        except: pass

    # Muitas máquinas
    maquinas_regex = re.search(r"(\d+)\s*(máquina|maquinas|maquininhas|maquininha)", relato)
    maquinas_alto = False
    if maquinas_regex and int(maquinas_regex.group(1)) >= 7:
        motivos.append(f"Solicitação de {maquinas_regex.group(1)} máquinas"); maquinas_alto = True

    # Modelos específicos
    modelos_suspeitos = ["smart", "p2", "pinpad", "pin pad"]
    if any(m in relato for m in modelos_suspeitos): motivos.append("Insistência por modelos Smart/P2/Pinpad")

    # Conta pré-ativa/plano Flex solicitado
    if any(t in relato for t in ["pré-ativa", "preativa", "plano flex", "transferido do front", "conta pré-ativa"]):
        motivos.append("Conta pré-ativa e/ou plano Flex solicitado")

    # Cliente CPF sem comprovante de atividade (pontua para risco!)
    cpf_presente = re.search(r"cpf", relato) is not None
    comprovante_presente = any(c in relato for c in [
        "comprovante", "fachada", "instagram", "facebook", "nota fiscal", "cartão", "transacional", "extrato"
    ])
    if cpf_presente and not comprovante_presente:
        motivos.append("CPF sem comprovante de atividade")
    # Cliente sem comprovante (qualquer perfil)
    if "sem comprovante de atividade" in relato or (cpf_presente and not comprovante_presente):
        motivos.append("Cliente sem comprovante de atividade")

    # Aceitação rápida de taxas e proposta
    aceita_taxa_rapida = any(
        frase in relato for frase in [
            "aceitou taxa", "não negociou taxa", "aceitou proposta", "aceitou sem negociar", "aceitou taxas rapidamente"
        ]
    )
    if aceita_taxa_rapida: motivos.append("Aceitou taxas sem negociação")

    # Verificação de endereço
    if "endereço" in relato or "endereço de entrega" in relato or "localização" in relato:
        sugestoes.append("Confirme se o endereço de entrega bate com o endereço do CNPJ e verifique no Google Maps se o local é idôneo.")

    # Recomendações padrão para análise investigativa
    sugestoes.append("Solicite comprovante de atividade (fachada, redes sociais, notas fiscais, cartão de visita, extrato de vendas).")
    sugestoes.append("Pesquise o comprovante enviado no Google Imagens para verificar sua autenticidade.")
    sugestoes.append("Questione a necessidade real se o cliente pedir muitas máquinas ou modelos específicos.")
    sugestoes.append("Antes de credenciar, envie o APP e peça que o cliente realize o KYC.")

    # Lógica para risco
    alto_riscos = [
        "TPV alimentício acima de R$100mil",
        "Solicitação de 7 máquinas", "Solicitação de 8 máquinas",
        "Insistência por modelos Smart/P2/Pinpad",
        "Conta pré-ativa e/ou plano Flex solicitado",
        "CPF sem comprovante de atividade",
        "Aceitou taxas sem negociação",
        "Cliente sem comprovante de atividade"
    ]
    risco_encontrado = False
    if ddd_sp and len(motivos) >= 4: risco_encontrado = True
    if any(r in motivos for r in alto_riscos): risco_encontrado = True

    if risco_encontrado:
        resposta = (
            f"<div class='analysis-bubble'><span class='risk-highlight'>RISCO ENCONTRADO</span>.<br><b>Motivos:</b> <span class='risk-highlight'>{', '.join(motivos)}</span>.<br><b>Sugestões:</b><ul>" +
            "".join([f"<li>{s}</li>" for s in list(dict.fromkeys(sugestoes))]) +
            "</ul>🟡 <i>Alerta: Reforce a validação deste atendimento!</i></div>"
        )
    else:
        resposta = (
            "<div class='analysis-bubble' style='color:#37FF8B;border-left:4px solid #22AA73;'>"
            "<span class='risk-highlight' style='color:#37FF8B;'>CLIENTE SEM RISCO ENCONTRADO</span>.<br>"
            f"<b>Motivos:</b> {', '.join(motivos) if motivos else 'Nenhum motivo crítico identificado.'}"
            "<br>Continue seguindo boas práticas de checagem e validação."
            "</div>"
        )
    return resposta

if user_input:
    st.markdown(f"<div class='user-bubble'>💬 {user_input}</div>", unsafe_allow_html=True)
    st.markdown(avaliar_risco_completo(user_input), unsafe_allow_html=True)
else:
    st.info("Preencha a caixa acima com a descrição do caso de atendimento para análise investigativa.")