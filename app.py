import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="MapeiaAI - Painel de RH", layout="wide")

# ---- BARRA LATERAL (MENU) ----
st.sidebar.image("https://via.placeholder.com/150x50.png?text=LOGOTIPO", use_column_width=True)
st.sidebar.title("Navegação")
tela = st.sidebar.radio("Ir para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato", "⚙️ Configurações"])

# Dados simulados de candidatos (Substituirá pela sua planilha futuramente)
dados_candidatos = {
    "João Silva": {"vaga": "Analista Comercial", "visual": 45, "auditivo": 35, "cinestesico": 20, "perfil": "Executor/Comunicador"},
    "Maria Santos": {"vaga": "Gestora de Projetos", "visual": 30, "auditivo": 50, "cinestesico": 20, "perfil": "Planeadora/Analista"},
    "Pedro Lima": {"vaga": "Desenvolvedor Python", "visual": 25, "auditivo": 35, "cinestesico": 40, "perfil": "Analista/Executor"}
}

# ---- TELA: PERFIL DO CANDIDATO ----
if tela == "👤 Perfil do Candidato":
    st.title("👤 Avaliação Individual de Perfil")
    st.markdown("Selecione um candidato para tabular os resultados e gerar o parecer com IA.")
    
    # Seleção do candidato
    candidato_sel = st.selectbox("Escolha o Candidato:", list(dados_candidatos.keys()))
    info = dados_candidatos[candidato_sel]
    
    # Informações Básicas
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Vaga Alvo", info["vaga"])
    col_b.metric("Perfil Predominante", info["perfil"])
    col_c.write("📅 **Data do Teste:** 24/05/2026")
    
    st.markdown("---")
    
    # Gráficos de Tabulação
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👁️👂💪 Sistema Representacional")
        df_rep = pd.DataFrame({
            "Canal": ["Visual", "Auditivo", "Cinestésico"],
            "Percentagem (%)": [info["visual"], info["auditivo"], info["cinestesico"]]
        })
        fig_rep = px.bar(df_rep, x="Canal", y="Percentagem (%)", color="Canal", text="Percentagem (%)")
        st.plotly_chart(fig_rep, use_container_width=True)
        
    with col2:
        st.subheader("🧠 Parecer de Contratação (IA)")
        st.success("🟢 **Recomendação:** Altamente Recomendado para a Vaga")
        
        texto_parecer = f"""
        O candidato **{candidato_sel}** apresenta um forte alinhamento com a vaga de **{info["vaga"]}**.
        
        **Pontos Fortes:**
        - Elevada capacidade de comunicação e foco em resultados (Perfil {info["perfil"]}).
        - Canal **Visual** proeminente ({info["visual"]}%), facilitando a apresentação de ideias e visão estratégica.
        
        **Pontos de Atenção:**
        - Pode demonstrar impaciência em tarefas puramente rotineiras.
        - Recomenda-se validar na entrevista de fit cultural a sua tolerância à frustração em ciclos longos de negociação.
        """
        st.write(texto_parecer)
        
        # Botão Simulado de PDF
        st.button("🖨️ Exportar Relatório em PDF")

# ---- TELA: DASHBOARD GERAL ----
elif tela == "📊 Dashboard Geral":
    st.title("📊 Painel Geral de Recrutamento")
    st.markdown("Visão macro dos testes realizados no sistema.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Candidatos", len(dados_candidatos))
    col2.metric("Vagas Abertas", "3")
    col3.metric("Testes Hoje", "1")

# ---- TELA: CONFIGURAÇÕES ----
else:
    st.title("⚙️ Parâmetros do Sistema")
    st.write("Aqui poderá configurar as chaves da API de Inteligência Artificial e os pesos das perguntas da sua planilha.")