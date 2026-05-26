import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================================
# 🪄 TRUQUE DE COMPATIBILIDADE COM O RENDER
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
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato"])

# Definição das cores da marca para os 4 canais representacionais
cores_canais = {
    "Visual": "#00B5B5", 
    "Auditivo": "#33CCCC", 
    "Cinestésico": "#004B8D",
    "Digital (Lógico)": "#FF7A00"
}

# =====================================================================
# 🔌 CONEXÃO REAL COM O GOOGLE SHEETS
# =====================================================================
@st.cache_data(ttl=30) # Atualiza a cada 30 segundos
def carregar_dados_planilha():
    try:
        conn = st.connection("gsheets")
        df = conn.read()
        # Limpa linhas onde o nome esteja em branco
        df = df.dropna(subset=["Nome"])
        return df
    except Exception as e:
        st.error(f"Erro de conexão: Verifique os nomes das colunas ou chaves. Detalhes: {e}")
        return None

df_dados = carregar_dados_planilha()

# =====================================================================
# 🧮 PROCESSAMENTO E MATEMÁTICA REAL DO TESTE REPRESENTACIONAL (PNL)
# =====================================================================
def calcular_sistema_representacional(linha):
    # Mapeamento exato baseado nas alternativas fornecidas
    colunas_visual = [
        "Eu tomo decisões importantes baseados em: [o que me parece melhor]",
        "Durante uma discussão eu sou mais influenciado por: [se eu posso ou não ver o argumento da outra pessoa]",
        "Eu comunico mais facilmente o que se passa comigo: [do modo como me visto e aparento]",
        "É muito fácil para mim: [escolher as combinações de cores mais ricas e atraentes]",
        "Eu me percebo assim: [eu respondo fortemente às cores e à aparência de uma sala]"
    ]
    
    colunas_auditivo = [
        "Eu tomo decisões importantes baseados em: [o que melhor me soar melhor]",
        "Durante uma discussão eu sou mais influenciado por: [tom de voz da outra pessoa]",
        "Eu comunico mais facilmente o que se passa comigo: [pelo tom da minha voz]",
        "É muito fácil para mim: [achar o volume e a sintonia ideais num sistema de som]",
        "Eu me percebo assim: [Se estou muito em sintonia com os sons do ambiente]"
    ]
    
    colunas_cinestesico = [
        "Eu tomo decisões importantes baseados em: [intuição]",
        "Durante uma discussão eu sou mais influenciado por: [se eu entro em contato ou não com os sentimentos reais do outro]",
        "Eu comunico mais facilmente o que se passa comigo: [pelos sentimentos que compartilho]",
        "É muito fácil para mim: [escolher os móveis mais confortáveis]",
        "Eu me percebo assim: [eu sou muito sensível à maneira como a roupa veste o meu corpo]"
    ]
    
    colunas_digital = [
        "Eu tomo decisões importantes baseados em: [um estudo preciso e minucioso do assunto]",
        "Durante uma discussão eu sou mais influenciado por: [a lógica do argumento da outra pessoa]",
        "Eu comunico mais facilmente o que se passa comigo: [pelas palavras que escolho]",
        "É muito fácil para mim: [selecionar o ponto mais relevante relativo a um assunto interessante]",
        "Eu me percebo assim: [se sou muito capaz de raciocinar com fatos e dados novos]"
    ]
    
    # Soma dos pontos convertendo os valores de texto para números com segurança
    v_score = sum([pd.to_numeric(linha[col], errors='coerce') for col in colunas_visual if col in linha])
    a_score = sum([pd.to_numeric(linha[col], errors='coerce') for col in colunas_auditivo if col in linha])
    c_score = sum([pd.to_numeric(linha[col], errors='coerce') for col in colunas_cinestesico if col in linha])
    d_score = sum([pd.to_numeric(linha[col], errors='coerce') for col in colunas_digital if col in linha])
    
    total = v_score + a_score + c_score + d_score
    
    if total > 0:
        return {
            "Visual": round((v_score / total) * 100, 1),
            "Auditivo": round((a_score / total) * 100, 1),
            "Cinestésico": round((c_score / total) * 100, 1),
            "Digital (Lógico)": round((d_score / total) * 100, 1)
        }
    return {"Visual": 25.0, "Auditivo": 25.0, "Cinestésico": 25.0, "Digital (Lógico)": 25.0}

# ---- DEFINIÇÃO DE LISTA DE CANDIDATOS ----
if df_dados is not None:
    lista_candidatos = df_dados["Nome"].unique()
else:
    lista_candidatos = ["Aguardando conexão com a planilha..."]

# =====================================================================
# TELA 1: PERFIL DO CANDIDATO (INDIVIDUAL)
# =====================================================================
if tela == "👤 Perfil do Candidato":
    st.title("👤 Avaliação Individual de Perfil")
    st.caption("Mapeamento automatizado extraído em tempo real da base de dados Implantta.")
    
    candidato_sel = st.selectbox("Selecione o Candidato para analisar os resultados:", lista_candidatos)
    
    if df_dados is not None and candidato_sel in df_dados["Nome"].values:
        # Puxa a linha exata do candidato
        linha_cand = df_dados[df_dados["Nome"] == candidato_sel].iloc[0]
        
        # Atribuição de variáveis seguras baseadas nas suas colunas
        vaga_alvo = linha_cand["Setor"] if "Setor" in linha_cand else "Não Informado"
        empresa_alvo = linha_cand["Empresa"] if "Empresa" in linha_cand else "Não Informada"
        email_cand = linha_cand["Endereço de e-mail"] if "Endereço de e-mail" in linha_cand else "Não Informado"
        data_teste = linha_cand["Data:"] if "Data:" in linha_cand else "Não Informada"
        
        # Realiza o cálculo matemático dos canais representacionais
        valores_canais = calcular_sistema_representacional(linha_cand)
        
        st.markdown("---")
        
        # Painel de Metadados
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.info(f"**Vaga / Função:**\n\n{vaga_alvo}")
        with col_b:
            st.info(f"**Empresa Solicitante:**\n\n{empresa_alvo}")
        with col_c:
            st.info(f"**E-mail de Contato:**\n\n{email_cand}")
        with col_d:
            st.info(f"**Data de Aplicação:**\n\n{data_teste}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.subheader("📊 Sistema Representacional (PNL Real)")
            # Monta tabela para o gráfico de barras
            df_chart = pd.DataFrame({
                "Canal": list(valores_canais.keys()),
                "Percentagem (%)": list(valores_canais.values())
            })
            fig = px.bar(df_chart, x="Canal", y="Percentagem (%)", color="Canal",
                         text="Percentagem (%)", template="streamlit",
                         color_discrete_map=cores_canais)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("🧠 Parecer de Engenharia de Perfil")
            st.success("📝 **Status:** Dados integrados e tabulados via API com sucesso.")
            
            # Identifica o canal predominante dinamicamente
            predominante = max(valores_canais, key=valores_canais.get)
            
            st.markdown(f"""
            O candidato **{candidato_sel}** apresenta um perfil de comunicação predominantemente **{predominante}** ({valores_canais[predominante]}%).
            
            **Dicas de Abordagem para o Consultor:**
            * O gráfico ao lado representa a distribuição exata de energia de captação de estímulos do candidato.
            * Use essa informação para estruturar dinâmicas de entrevista alinhadas com a velocidade de processamento dele.
            """)
            
            # SEÇÃO EXPANSÍVEL: Respostas comportamentais brutas para o consultor analisar
            st.markdown("---")
            with st.expander("🔍 Ver Respostas Brutas do Teste Comportamental (Texto)"):
                perguntas_texto = [
                    "Eu sou", "Eu gosto de ...", "Se você quiser se dar bem comigo....",
                    "Para conseguir obter bons resultados é preciso...", "Eu me divirto quando...",
                    "Eu penso que...", "Minha preocupação é...", "Eu prefiro...", "Eu gosto de...",
                    "Eu gosto de chegar...", "Um ótimo dia para mim é quando...", "Eu vejo a morte como...",
                    "Minha Filosofia de vida é...", "Eu sempre gostei de...", "Eu gosto de mudanças se...",
                    "Não existe nada de errado em...", "Eu gosto de buscar conselhos de...", "Meu lema é...",
                    "Tempo para mim é...", "Se eu fosse bilionário...", "Eu acredito que...",
                    "Eu acredito também que...", "Eu acredito ainda que..."
                ]
                for p in perguntas_texto:
                    if p in linha_cand:
                        st.markdown(f"**{p}**")
                        st.code(linha_cand[p])

# =====================================================================
# TELA 2: DASHBOARD GERAL
# =====================================================================
elif tela == "📊 Dashboard Geral":
    st.title("📊 Painel Geral de Recrutamento")
    st.markdown("Monitoramento macro e fluxo de entrada da planilha do Google Drive.")
    
    total_candidatos = len(lista_candidatos) if df_dados is not None else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Candidatos Avaliados", value=total_candidatos)
    col2.metric("Conexão Google Drive", "Ativa e Segura" if df_dados is not None else "Inativa")
    col3.metric("Atualização Automática", "A cada 30s")
    
    if df_dados is not None:
        st.markdown("### 📋 Fluxo de Respostas Mais Recentes")
        st.dataframe(df_dados[["Carimbo de data/hora", "Nome", "Empresa", "Setor"]])
