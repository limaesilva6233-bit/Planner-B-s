import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

# Configurações de Estética "Casal"
st.set_page_config(page_title="Sintonia a Dois", page_icon="❤️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fff5f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; border: none; }
    h1, h2, h3 { color: #d63384; font-family: 'Segoe UI', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 10px 10px 0px 0px; gap: 1px; }
    .stTabs [aria-selected="true"] { background-color: #ffc0cb; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'eventos' not in st.session_state:
    st.session_state.eventos = []
if 'cadastrado' not in st.session_state:
    st.session_state.cadastrado = False

# --- TELA DE CADASTRO INICIAL ---
if not st.session_state.cadastrado:
    st.title("❤️ Bem-vindos ao Nosso Universo")
    st.subheader("Configurem seus perfis para começar:")
    
    with st.form("cadastro_casal"):
        col1, col2 = st.columns(2)
        with col1:
            nome_ele = st.text_input("Nome Dele", placeholder="Ex: João")
            whats_ele = st.text_input("WhatsApp Dele", placeholder="55119...")
        with col2:
            nome_ela = st.text_input("Nome Dela", placeholder="Ex: Maria")
            whats_ela = st.text_input("WhatsApp Dela", placeholder="55119...")
        
        if st.form_submit_button("Criar Nosso Calendário"):
            if nome_ele and whats_ele and nome_ela and whats_ela:
                st.session_state.user_data = {
                    "Masculino": {"nome": nome_ele, "whats": whats_ele, "cor": "#3498db"},
                    "Feminino": {"nome": nome_ela, "whats": whats_ela, "cor": "#e91e63"}
                }
                st.session_state.cadastrado = True
                st.rerun()
            else:
                st.error("Por favor, preencham todos os campos para que as notificações funcionem!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.sidebar.title("👤 Quem está usando?")
quem_acessa = st.sidebar.radio("Selecione seu perfil:", ["Feminino", "Masculino"])
perfil_atual = st.session_state.user_data[quem_acessa]

st.title(f"💞 Agenda de {st.session_state.user_data['Masculino']['nome']} & {st.session_state.user_data['Feminino']['nome']}")

# --- ADICIONAR EVENTOS ---
with st.expander("➕ Adicionar Novo Evento/Compromisso"):
    col_t, col_d = st.columns([2, 1])
    with col_t:
        titulo = st.text_input("O que vai acontecer?")
        tipo_evento = st.selectbox("Para quem é esse evento?", [f"Só para mim ({perfil_atual['nome']})", "Para o Casal"])
    with col_d:
        data_ev = st.date_input("Data")
        importante = st.checkbox("Marcar como Importante? ⭐")
    
    if st.button("Salvar Evento"):
        if titulo:
            # Define se o tipo é o sexo atual ou Casal
            tipo_final = quem_acessa if "Só para mim" in tipo_evento else "Casal"
            st.session_state.eventos.append({
                "titulo": titulo,
                "data": data_ev,
                "tipo": tipo_final,
                "importante": importante
            })
            st.success("Evento salvo com sucesso!")
            st.rerun()

# --- CALENDÁRIO VISUAL ---
st.divider()
st.subheader("📅 Visão Geral do Mês")

calendar_events = []
for ev in st.session_state.eventos:
    # Filtra o que aparece: Meus eventos + Eventos do Casal
    if ev['tipo'] == quem_acessa or ev['tipo'] == "Casal":
        cor = "#ff4b4b" if ev['tipo'] == "Casal" else perfil_atual['cor']
        calendar_events.append({
            "title": f"{'⭐ ' if ev['importante'] else ''}{ev['titulo']}",
            "start": ev['data'].strftime("%Y-%m-%d"),
            "color": cor,
            "allDay": True
        })

calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    "initialView": "dayGridMonth",
    "locale": "pt-br",
}

calendar(events=calendar_events, options=calendar_options)

# --- RELATÓRIO E AVISOS ---
st.divider()
col_rel, col_avisos = st.columns(2)

hoje = datetime.now().date()

with col_rel:
    st.subheader("📋 Para Hoje")
    eventos_hoje = [e for e in st.session_state.eventos if e['data'] == hoje and (e['tipo'] == quem_acessa or e['tipo'] == "Casal")]
    if eventos_hoje:
        for e in eventos_hoje:
            st.info(f"**{e['titulo']}** ({'Nosso' if e['tipo'] == 'Casal' else 'Meu'})")
    else:
        st.write("Nada marcado para hoje! Aproveitem! ✨")

with col_avisos:
    st.subheader("🚨 Avisos de Importantes")
    for e in st.session_state.eventos:
        if e['importante'] and (e['tipo'] == quem_acessa or e['tipo'] == "Casal"):
            dias_para = (e['data'] - hoje).days
            if 0 < dias_para <= 7:
                st.warning(f"Faltam {dias_para} dias para: **{e['titulo']}**")
            elif dias_para == 0:
                st.error(f"É HOJE: **{e['titulo']}**")
