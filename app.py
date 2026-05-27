import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# =====================================================================
# 🪄 TRUQUE DE COMPATIBILIDADE SENSÍVEL (SEMPRE SOBRESCREVE)
# =====================================================================
if os.path.exists("secrets.toml"):
    os.makedirs(".streamlit", exist_ok=True)
    shutil.copy("secrets.toml", ".streamlit/secrets.toml")
# =====================================================================

st.set_page_config(
    page_title="MapeiaAI - Diagnóstico", 
    page_icon="🧠",
    layout="wide"
)

st.sidebar.title("Painel de Controle")
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato"])

# Definição das cores
cores_canais = {"Visual": "#00B5B5", "Auditivo": "#33CCCC", "Cinestésico": "#004B8D", "Digital (Lógico)": "#FF7A00"}

# =====================================================================
# 🔌 CONEXÃO PURA (SEM FILTROS INICIAIS)
# =====================================================================
@st.cache_data(ttl=10) # Atualiza rápido para testarmos
def carregar_dados_diagnostico():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        return df
    except Exception as e:
        st.error("🚨 CONEXÃO BLOQUEADA PELO GOOGLE OU ERRO DE CHAVE!")
        st.exception(e) # Exibe o rastro técnico completo do erro na tela
        return None

df_dados = carregar_dados_diagnostico()

# =====================================================================
# SE CONECTOU, EXIBE O DIAGNÓSTICO DAS COLUNAS REAL
# =====================================================================
if df_dados is not None:
    st.success("🎉 EXCELENTE! O Python conseguiu abrir a sua planilha do Google Sheets!")
    
    st.markdown("### 🔍 Lista de Colunas Detectadas na sua Planilha:")
    st.info(", ".join([f"**[{col}]**" for col in df_dados.columns]))
    
    # Identificação automática da coluna de nome para não travar
    coluna_nome_real = None
    for col in df_dados.columns:
        if "nome" in col.lower():
            coluna_nome_real = col
            break
            
    if coluna_nome_real:
        df_dados = df_dados.dropna(subset=[coluna_nome_real])
        lista_candidatos = df_dados[coluna_nome_real].unique()
    else:
        st.warning("⚠️ Não encontramos nenhuma coluna com a palavra 'Nome'. Usando a primeira coluna por padrão.")
        coluna_nome_real = df_dados.columns[1]
        lista_candidatos = df_dados[coluna_nome_real].unique()

    # ---- TELA: PERFIL DO CANDIDATO ----
    if tela == "👤 Perfil do Candidato":
        st.title("👤 Avaliação Individual de Perfil")
        candidato_sel = st.selectbox("Selecione o Candidato:", lista_candidatos)
        
        if candidato_sel in df_dados[coluna_nome_real].values:
            linha_cand = df_dados[df_dados[coluna_nome_real] == candidato_sel].iloc[0]
            st.write("✅ Dados do candidato carregados. Pronto para acoplamento das fórmulas.")
            st.json(linha_cand.to_dict()) # Mostra os dados brutos dele organizados

    # ---- TELA: DASHBOARD GERAL ----
    else:
        st.title("📊 Painel Geral de Recrutamento")
        st.metric(label="Total de Candidatos Identificados", value=len(lista_candidatos))
        st.dataframe(df_dados)

else:
    st.warning("🛟 O sistema está aguardando a correção da conexão acima para poder exibir os gráficos.")
