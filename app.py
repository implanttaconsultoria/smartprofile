import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================================
# 🪄 TRUQUE DE COMPATIBILIDADE COM O RENDER (MANTIDO)
# =====================================================================
if os.path.exists("secrets.toml") and not os.path.exists(".streamlit/secrets.toml"):
    os.makedirs(".streamlit", exist_ok=True)
    shutil.copy("secrets.toml", ".streamlit/secrets.toml")
# =====================================================================

# 1. Configuração da página
st.set_page_config(
    page_title="MapeiaAI - Implantta Consultoria", 
    page_icon="🧠",
    layout="wide"
)

# ---- BARRA LATERAL (MENU E LOGO) ----
try:
    st.sidebar.image("logo_branca.png", use_container_width=True)
except:
    st.sidebar.subheader("🌱 Implantta Consultoria")

st.sidebar.markdown("---")
st.sidebar.title("Painel de Controle")
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato", "⚙️ Configurações"])

# Definição das cores da marca para os gráficos
cores_canais = {"Visual": "#00B5B5", "Auditivo": "#33CCCC", "Cinestésico": "#004B8D"}

# =====================================================================
# 🔌 CONEXÃO REAL COM O GOOGLE SHEETS
# =====================================================================
@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def carregar_dados_planilha():
    try:
        # Cria a conexão usando o arquivo secrets salvo no Render
        conn = st.connection("gsheets", type=st.connections.GSheetsConnection)
        # Lê a planilha ativa
        df = conn.read()
        # Remove linhas totalmente vazias se houverem
        df = df.dropna(subset=["Nome do candidato"])
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None

df_dados = carregar_dados_planilha()

# =====================================================================
# 🧮 FUNÇÃO DE TABULAÇÃO E PESOS (A MENTE DO SEU TESTE)
# =====================================================================
def calcular_resultados_reais(linha_candidato):
    """
    Aqui dentro o Python vai aplicar as regras da sua planilha de pesos.
    Por enquanto, deixei valores fixos simulados até você me passar as regras!
    """
    # Exemplo de como o Python lerá uma resposta de texto ou número futuramente:
    # resposta_q1 = linha_candidato["Pergunta 1"]
    
    resultados = {
        "visual": 40,
        "auditivo": 35,
        "cinestesico": 25,
        "perfil_comportamental": "Executor / Comunicador (Simulado)"
    }
    return resultados
# =====================================================================


# ---- PROGRAMAÇÃO DAS TELAS ----

if df_dados is not None:
    lista_candidatos = df_dados["Nome do candidato"].unique()
else:
    lista_candidatos = ["Nenhum candidato encontrado (Verifique a planilha)"]

# ---- TELA: PERFIL DO CANDIDATO ----
if tela == "👤 Perfil do Candidato":
    st.title("👤 Avaliação Individual de Perfil")
    st.caption("Mapeamento comportamental e representacional automatizado pela inteligência Implantta.")
    
    candidato_sel = st.selectbox("Selecione o Candidato para Análise:", lista_candidatos)
    
    if df_dados is not None and candidato_sel in df_dados["Nome do candidato"].values:
        # Filtra a linha exata do candidato selecionado
        dados_candidato_real = df_dados[df_dados["Nome do candidato"] == candidato_sel].iloc[0]
        
        # Puxa as informações das colunas que você me passou
        vaga_alvo = dados_candidato_real["Setores /função a qual o candidato está se candidatando"]
        
        # Tenta puxar a empresa (como tem parênteses no nome da coluna, usamos o nome exato)
        try:
            empresa_alvo = dados_candidato_real["(Empresa  a qual ele está se candidatando a vaga)"]
        except:
            empresa_alvo = "Não informada"
            
        email_candidato = dados_candidato_real.iloc[-1] # Puxa a última coluna da planilha (E-mail)
        
        # Executa os cálculos matemáticos baseados na linha dele
        metricas = calcular_resultados_reais(dados_candidato_real)
        
        st.markdown("---")
        
        # Informações Básicas organizadas em cards limpos
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.info(f"**Vaga / Função:**\n\n{vaga_alvo}")
        with col_b:
            st.info(f"**Empresa-Cliente:**\n\n{empresa_alvo}")
        with col_c:
            st.info(f"**Perfil Comportamental:**\n\n{metricas['perfil_comportamental']}")
        with col_d:
            st.info(f"**E-mail do Candidato:**\n\n{email_candidato}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos e Parecer
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.subheader("📊 Sistema Representacional")
            df_rep = pd.DataFrame({
                "Canal": ["Visual", "Auditivo", "Cinestésico"],
                "Percentagem (%)": [metricas["visual"], metricas["auditivo"], metricas["cinestesico"]]
            })
            fig_rep = px.bar(df_rep, x="Canal", y="Percentagem (%)", color="Canal", 
                             text="Percentagem (%)", template="streamlit",
                             color_discrete_map=cores_canais)
            fig_rep.update_layout(showlegend=False)
            st.plotly_chart(fig_rep, use_container_width=True)
            
        with col2:
            st.subheader("🧠 Parecer de Contratação (Implantta AI)")
            st.success("📝 **Recomendação:** Análise liberada para parecer do consultor.")
            
            texto_parecer = f"""
            O candidato **{candidato_sel}** concluiu o teste com sucesso. Os dados acima já foram processados diretamente da planilha oficial da **Implantta Consultoria**.
            
            *Nota: O motor de inteligência artificial gerará o texto personalizado assim que integrarmos a fórmula de tabulação dos pesos.*
            """
            st.markdown(texto_parecer)
            st.button("🖨️ Exportar Relatório em PDF", key="btn_pdf")

# ---- TELA: DASHBOARD GERAL ----
elif tela == "📊 Dashboard Geral":
    st.title("📊 Painel Geral de Recrutamento")
    st.markdown("Visão macro dos testes realizados no sistema.")
    
    total_candidatos = len(lista_candidatos) if df_dados is not None else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Candidatos na Planilha", value=total_candidatos)
    col2.metric("Vagas Monitoradas", "Dinâmico")
    col3.metric("Status da Conexão", "100% Online" if df_dados is not None else "Erro")
    
    if df_dados is not None:
        st.markdown("### 📋 Últimas Respostas Recebidas")
        st.dataframe(df_dados[["Carimbo de data/hora", "Nome do candidato", "Setores /função a qual o candidato está se candidatando"]])

# ---- TELA: CONFIGURAÇÕES ----
else:
    st.title("⚙️ Parâmetros e Chaves")
    st.write("Configurações internas do sistema Implantta.")
