import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais Estilo "Casal"
st.set_page_config(page_title="Sintonia a Dois", page_icon="❤️")

st.markdown("""
    <style>
    .main { background-color: #fff5f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 15px; }
    h1 { color: #d63384; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE CADASTRO ---
if 'cadastrado' not in st.session_state:
    st.session_state.cadastrado = False

if not st.session_state.cadastrado:
    st.title("❤️ Bem-vindos ao Sintonia a Dois")
    st.subheader("Para começar, vamos configurar o perfil do casal:")
    
    with st.form("cadastro_casal"):
        col1, col2 = st.columns(2)
        with col1:
            nome_ele = st.text_input("Nome Dele")
            whats_ele = st.text_input("WhatsApp Dele (ex: 5511999999999)")
        with col2:
            nome_ela = st.text_input("Nome Dela")
            whats_ela = st.text_input("WhatsApp Dela (ex: 5511888888888)")
        
        if st.form_submit_button("Criar Nosso Universo"):
            if nome_ele and whats_ele and nome_ela and whats_ela:
                st.session_state.user_data = {
                    "Masculino": {"nome": nome_ele, "whats": whats_ele},
                    "Feminino": {"nome": nome_ela, "whats": whats_ela}
                }
                st.session_state.cadastrado = True
                st.session_state.eventos = []
                st.rerun()
            else:
                st.error("Por favor, preencham todos os campos!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title(f"💞 Calendário de {st.session_state.user_data['Masculino']['nome']} & {st.session_state.user_data['Feminino']['nome']}")

# Escolha de quem está acessando agora
quem_acessa = st.sidebar.selectbox("Quem está acessando?", ["Masculino", "Feminino"])
perfil_atual = st.session_state.user_data[quem_acessa]

st.sidebar.info(f"Logado como: **{perfil_atual['nome']}**\n\nNotificações via: {perfil_atual['whats']}")

# --- ABAS ---
tab_pessoal, tab_casal = st.tabs([f"🌸 Meu Espaço ({perfil_atual['nome']})", "💍 Nosso Espaço (Casal)"])

def adicionar_evento(titulo, data, tipo, importante):
    evento = {
        "titulo": titulo,
        "data": data,
        "tipo": tipo, # 'Masculino', 'Feminino' ou 'Casal'
        "importante": importante,
        "enviado_1w": False, "enviado_3d": False, "enviado_1d": False
    }
    st.session_state.eventos.append(evento)

with tab_pessoal:
    st.subheader(f"Meus Eventos Privados")
    with st.expander("➕ Adicionar compromisso só meu"):
        t = st.text_input("O que é?", key="t_pessoal")
        d = st.date_input("Quando?", key="d_pessoal")
        imp = st.checkbox("É importante? ⭐", key="i_pessoal")
        if st.button("Salvar na Minha Agenda"):
            adicionar_evento(t, d, quem_acessa, imp)
            st.success("Adicionado!")

with tab_casal:
    st.subheader("Eventos do Casal (Notificação para AMBOS)")
    with st.expander("➕ Adicionar compromisso do casal"):
        tc = st.text_input("O que vamos fazer?", key="t_casal")
        dc = st.date_input("Quando?", key="d_casal")
        impc = st.checkbox("É importante? ⭐", key="i_casal")
        if st.button("Salvar na Agenda do Casal"):
            adicionar_evento(tc, dc, "Casal", impc)
            st.success("Adicionado para nós dois!")

# --- LÓGICA DE NOTIFICAÇÃO (WHATSAPP) ---
st.divider()
st.subheader("🚀 Status das Notificações")

def enviar_msg_whatsapp(numero, mensagem):
    # Aqui entraria o código da API (Twilio ou Evolution API)
    # Por segurança e simplicidade, o Streamlit apenas simula o disparo
    st.write(f"📲 **Simulando WhatsApp para {numero}:** {mensagem}")

hoje = datetime.now().date()

for ev in st.session_state.eventos:
    dias_restantes = (ev['data'] - hoje).days
    
    # Lógica de quem recebe
    destinatarios = []
    if ev['tipo'] == "Masculino": destinatarios = [st.session_state.user_data['Masculino']['whats']]
    elif ev['tipo'] == "Feminino": destinatarios = [st.session_state.user_data['Feminino']['whats']]
    else: destinatarios = [st.session_state.user_data['Masculino']['whats'], st.session_state.user_data['Feminino']['whats']]

    # Gatilhos de Notificação para eventos Importantes
    if ev['importante']:
        msg = f"⚠️ LEMBRETE: O evento '{ev['titulo']}' está chegando! Faltam {dias_restantes} dias."
        
        if dias_restantes == 7 and not ev['enviado_1w']:
            for n in destinatarios: enviar_msg_whatsapp(n, msg)
            ev['enviado_1w'] = True
        elif dias_restantes == 3 and not ev['enviado_3d']:
            for n in destinatarios: enviar_msg_whatsapp(n, msg)
            ev['enviado_3d'] = True
        elif dias_restantes == 1 and not ev['enviado_1d']:
            for n in destinatarios: enviar_msg_whatsapp(n, "🚨 É AMANHÃ: " + ev['titulo'])
            ev['enviado_1d'] = True
