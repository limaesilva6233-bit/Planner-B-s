import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
from st_gsheets_connection import GSheetsConnection

# Configuração da Página
st.set_page_config(page_title="Sintonia a Dois", page_icon="❤️", layout="wide")

# Conexão com o Banco de Dados (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        return conn.read(ttl=0) # ttl=0 força a ler os dados novos sempre
    except:
        return pd.DataFrame(columns=["data", "titulo", "tipo", "importante"])

def salvar_evento(nova_linha):
    dados_atuais = carregar_dados()
    dados_novos = pd.concat([dados_atuais, pd.DataFrame([nova_linha])], ignore_index=True)
    conn.update(data=dados_novos)
    st.cache_data.clear()

# --- SISTEMA DE LOGIN SIMPLES ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito ao Casal")
    senha = st.text_input("Digite a senha secreta do casal:", type="password")
    if st.button("Entrar"):
        if senha == "6233": # <--- MUDE SUA SENHA AQUI
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta! ❤️")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.sidebar.title("👤 Perfil")
quem_acessa = st.sidebar.radio("Selecione quem está usando:", ["Feminino", "Masculino"])

# Cores e Nomes (Você pode fixar aqui para não ter que cadastrar toda hora)
perfis = {
    "Masculino": {"nome": "Ele", "cor": "#3498db"},
    "Feminino": {"nome": "Ela", "cor": "#e91e63"}
}
perfil_atual = perfis[quem_acessa]

st.title(f"💞 Agenda de {perfis['Masculino']['nome']} & {perfis['Feminino']['nome']}")

# --- ADICIONAR EVENTOS ---
with st.expander("➕ Adicionar Novo Compromisso"):
    col_t, col_d = st.columns([2, 1])
    with col_t:
        titulo = st.text_input("O que vai acontecer?")
        tipo_evento = st.selectbox("Para quem?", ["Só para mim", "Para o Casal"])
    with col_d:
        data_ev = st.date_input("Data")
        imp = st.checkbox("Importante? ⭐")
    
    if st.button("Salvar na Nuvem"):
        if titulo:
            tipo_final = quem_acessa if tipo_evento == "Só para mim" else "Casal"
            nova_linha = {
                "data": data_ev.strftime("%Y-%m-%d"),
                "titulo": titulo,
                "tipo": tipo_final,
                "importante": "Sim" if imp else "Não"
            }
            salvar_evento(nova_linha)
            st.success("Gravado com sucesso! Agora não apaga mais. ✅")
            st.rerun()

# --- CARREGAR E EXIBIR CALENDÁRIO ---
df_eventos = carregar_dados()

calendar_events = []
for _, row in df_eventos.iterrows():
    # Filtro de privacidade
    if row['tipo'] == quem_acessa or row['tipo'] == "Casal":
        cor = "#ff4b4b" if row['tipo'] == "Casal" else perfil_atual['cor']
        calendar_events.append({
            "title": f"{'⭐ ' if row['importante'] == 'Sim' else ''}{row['titulo']}",
            "start": row['data'],
            "color": cor,
            "allDay": True
        })

st.divider()
calendar(events=calendar_events, options={"locale": "pt-br"})

# --- AVISOS ---
hoje = datetime.now().strftime("%Y-%m-%d")
st.subheader("📢 Avisos Próximos")
eventos_futuros = df_eventos[df_eventos['data'] >= hoje].sort_values(by="data")

for _, e in eventos_futuros.head(5).iterrows():
    if e['tipo'] == quem_acessa or e['tipo'] == "Casal":
        st.write(f"📅 **{e['data']}**: {e['titulo']} ({e['tipo']})")
