import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página - Nome da sua empresa no navegador
st.set_page_config(
    page_title="MapeiaAI - Implantta Consultoria", 
    page_icon="🧠",
    layout="wide"
)

# ---- BARRA LATERAL (MENU CENTRALIZADO E COLORIDO) ----
# Centraliza a logo com CSS customizado
st.markdown("""
    <style>
    [data-testid="stSidebarImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    st.sidebar.image("logo.png", use_container_width=True)
except:
    st.sidebar.subheader("🌱 Implantta Consultoria")

st.sidebar.markdown("---")
st.sidebar.title("Painel de Controle")
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato", "⚙️ Configurações"])

# Dados simulados de candidatos (futuramente virão do Google Sheets)
dados_candidatos = {
    "João Silva": {"vaga": "Analista Comercial", "visual": 45, "auditivo": 35, "cinestesico": 20, "perfil": "Executor/Comunicador"},
    "Maria Santos": {"vaga": "Gestora de Projetos", "visual": 30, "auditivo": 50, "cinestesico": 20, "perfil": "Planeadora/Analista"},
    "Pedro Lima": {"vaga": "Desenvolvedor Python", "visual": 25, "auditivo": 35, "cinestesico": 40, "perfil": "Analista/Executor"}
}

# Definição das cores da marca para os gráficos
cores_implantta = px.colors.qualitative.Prism
cores_canais = {"Visual": "#00B5B5", "Auditivo": "#33CCCC", "Cinestésico": "#004B8D"}

# ---- TELA: PERFIL DO CANDIDATO ----
if tela == "👤 Perfil do Candidato":
    st.title("👤 Avaliação Individual de Perfil")
    st.caption("Mapeamento comportamental e representacional automatizado pela inteligência Implantta.")
    
    candidato_sel = st.selectbox("Selecione o Candidato para Análise:", list(dados_candidatos.keys()))
    info = dados_candidatos[candidato_sel]
    
    st.markdown("---")
    
    # Informações Básicas organizadas em cards limpos e coloridos com turquesa
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info(f"**Vaga Alvo:**\n\n{info['vaga']}")
    with col_b:
        st.info(f"**Perfil Comportamental:**\n\n{info['perfil']}")
    with col_c:
        st.info(f"**Status da Avaliação:**\n\nConcluído em 24/05/2026")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos e Parecer
    col1, col2 = st.columns([1, 1.2]) # Coluna da IA ligeiramente maior para o texto respirar
    
    with col1:
        st.subheader("📊 Sistema Representacional")
        df_rep = pd.DataFrame({
            "Canal": ["Visual", "Auditivo", "Cinestésico"],
            "Percentagem (%)": [info["visual"], info["auditivo"], info["cinestesico"]]
        })
        # Gráfico elegante usando a paleta de cores do tema do Streamlit
        fig_rep = px.bar(df_rep, x="Canal", y="Percentagem (%)", color="Canal", 
                         text="Percentagem (%)", template="streamlit",
                         color_discrete_map=cores_canais)
        fig_rep.update_layout(showlegend=False)
        st.plotly_chart(fig_rep, use_container_width=True)
        
    with col2:
        st.subheader("🧠 Parecer de Contratação (Implantta AI)")
        
        # Alerta visual de recomendação usando o turquesa vibrante
        st.success("📝 **Recomendação:** Candidato com Forte Aderência ao Perfil da Vaga.")
        
        texto_parecer = f"""
        Após a tabulação automatizada dos parâmetros Implantta, identificou-se que o candidato **{candidato_sel}** possui competências comportamentais muito próximas do padrão esperado para a posição de **{info["vaga"]}**.
        
        **Principais Forças Identificadas:**
        * Predomínio do canal **Visual** ({info["visual"]}%), indicando facilidade com organização, metas claras e forte assimilação de processos visuais.
        * Perfil comportamental voltado para a ação ({info["perfil"]}), ideal para ambientes que demandam dinamismo.
        
        **Recomendações para a Entrevista:**
        * Investigar como reage sob pressão quando os canais de comunicação tradicionais falham.
        * Recomenda-se validar a sua tolerância à frustração em ciclos longos de negociação.
        """
        st.markdown(texto_parecer)
        
        # Botão de PDF com a cor primária turquesa
        st.button("🖨️ Exportar Relatório em PDF", key="btn_pdf")

# ---- TELA: DASHBOARD GERAL ----
elif tela == "📊 Dashboard Geral":
    st.title("📊 Painel Geral de Recrutamento")
    st.markdown("Visão macro dos testes realizados no sistema.")
    
    # Métricas com o turquesa vibrante
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Candidatos", value=len(dados_candidatos), delta="30 dias")
    col2.metric("Vagas Monitoradas", "3")
    col3.metric("Análises este Mês", "12")

# ---- TELA: CONFIGURAÇÕES ----
else:
    st.title("⚙️ Parâmetros e Chaves")
    st.write("Aqui poderá configurar as chaves da API de Inteligência Artificial e os pesos das perguntas da sua planilha.")
