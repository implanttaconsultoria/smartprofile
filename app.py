import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# =====================================================================
# 🪄 TRUQUE DE COMPATIBILIDADE (RENDER)
# =====================================================================
if os.path.exists("secrets.toml"):
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

# Definição das cores da marca para os 4 canais representacionais (PNL)
cores_canais = {
    "Visual": "#00B5B5", 
    "Auditivo": "#33CCCC", 
    "Cinestésico": "#004B8D",
    "Digital (Lógico)": "#FF7A00"
}

# =====================================================================
# 🔌 CONEXÃO E AUTO-LIMPEZA DA PLANILHA (BLINDADO)
# =====================================================================
@st.cache_data(ttl=30) 
def carregar_dados_planilha():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        url_planilha = "https://docs.google.com/spreadsheets/d/1cz6O2iSync1c2E-lNGmEsgwMBrOgB2DHWz02A-y2g1Y/edit"
        df = conn.read(spreadsheet=url_planilha)
        
        # ✨ CAÇADOR DE CABEÇALHOS: Ignora os filtros no topo
        if "Nome" not in df.columns:
            for i, row in df.iterrows():
                valores_linha = [str(val).lower().strip() for val in row.values]
                if "nome" in valores_linha or "nome do candidato" in valores_linha:
                    df.columns = row.values 
                    df = df.iloc[i+1:].reset_index(drop=True) 
                    break
        
        # Limpa o dataframe de colunas nulas
        df = df.loc[:, df.columns.notna()]
        
        # ✨ BLINDAGEM: Transforma o nome em texto (str) antes de procurar para evitar erros de tipos
        coluna_nome = None
        for col in df.columns:
            if "nome" in str(col).lower():
                coluna_nome = col
                break
                
        if coluna_nome:
            df = df.dropna(subset=[coluna_nome])
            df = df.rename(columns={coluna_nome: "Nome"})
            
        return df
    except Exception as e:
        st.error(f"Erro de conexão ou processamento: {e}")
        return None

df_dados = carregar_dados_planilha()

# =====================================================================
# 🧮 PROCESSAMENTO DA MATEMÁTICA DO TESTE REPRESENTACIONAL (PNL)
# =====================================================================
def calcular_sistema_representacional(linha):
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
    
    v_score = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_visual])
    a_score = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_auditivo])
    c_score = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_cinestesico])
    d_score = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_digital])
    
    v_score = v_score if pd.notna(v_score) else 0
    a_score = a_score if pd.notna(a_score) else 0
    c_score = c_score if pd.notna(c_score) else 0
    d_score = d_score if pd.notna(d_score) else 0
    
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
if df_dados is not None and "Nome" in df_dados.columns:
    lista_candidatos = df_dados["Nome"].unique()
else:
    lista_candidatos = ["Aguardando candidatos na planilha..."]

# =====================================================================
# TELA 1: PERFIL DO CANDIDATO
# =====================================================================
if tela == "👤 Perfil do Candidato":
    st.title("👤 Avaliação Individual de Perfil")
    st.caption("Mapeamento automatizado extraído em tempo real da base de dados Implantta.")
    
    candidato_sel = st.selectbox("Selecione o Candidato para analisar os resultados:", lista_candidatos)
    
    if df_dados is not None and "Nome" in df_dados.columns and candidato_sel in df_dados["Nome"].values:
        linha_cand = df_dados[df_dados["Nome"] == candidato_sel].iloc[0]
        
        # Pega as colunas com segurança usando .get()
        vaga_alvo = linha_cand.get("Setor", "Não Informado")
        empresa_alvo = linha_cand.get("Empresa", "Não Informada")
        email_cand = linha_cand.get("Endereço de e-mail", "Não Informado")
        data_teste = linha_cand.get("Carimbo de data/hora", linha_cand.get("Data:", "Não Informada"))
        
        valores_canais = calcular_sistema_representacional(linha_cand)
        
        st.markdown("---")
        
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
            
            predominante = max(valores_canais, key=valores_canais.get)
            
            st.markdown(f"""
            O candidato **{candidato_sel}** apresenta um perfil de comunicação predominantemente **{predominante}** ({valores_canais[predominante]}%).
            
            **Dicas de Abordagem para o Consultor:**
            * O gráfico ao lado representa a distribuição exata de energia de captação de estímulos do candidato.
            * Use essa informação para estruturar dinâmicas de entrevista alinhadas com a velocidade de processamento dele.
            """)
            
            # 🔍 ABA ATUALIZADA COM AS PERGUNTAS ÚNICAS REAIS DA PLANILHA
            st.markdown("---")
            with st.expander("🔍 Ver Respostas Brutas do Teste Comportamental (Texto)"):
                perguntas_texto = [
                    "Eu sou", "Eu gosto de ...", "Se você quiser se dar bem comigo....",
                    "Para conseguir obter bons resultados é preciso...", "Eu me divirto quando...",
                    "Eu penso que...", "Minha preocupação é...", "Eu escolho...", "Eu prefiro.",
                    "Eu gosto de chegar...", "Um ótimo dia para mim é quando...", "Eu vejo a morte como...",
                    "Minha Filosofia de vida é...", "Eu sempre gostei de...", "Eu gosto de mudanças se...",
                    "Não existe nada de errado em...", "Eu gosto de buscar conselhos de...", "Meu lema é...",
                    "Para mim é essencial...", "Tempo para mim é...", "Se eu fosse bilionário...", 
                    "Eu acredito que...", "Eu acredito também que...", "Eu acredito ainda que...", 
                    "Eu acho que..."
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
    
    total_candidatos = len(lista_candidatos) if df_dados is not None and "Nome" in df_dados.columns else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Candidatos Avaliados", value=total_candidatos)
    col2.metric("Conexão Google Drive", "Ativa e Segura" if df_dados is not None else "Inativa")
    col3.metric("Atualização Automática", "A cada 30s")
    
    if df_dados is not None and "Nome" in df_dados.columns:
        st.markdown("### 📋 Fluxo de Respostas Mais Recentes")
        
        colunas_exibicao = []
        for col in ["Carimbo de data/hora", "Nome", "Empresa", "Setor"]:
            if col in df_dados.columns:
                colunas_exibicao.append(col)
                
        if colunas_exibicao:
            st.dataframe(df_dados[colunas_exibicao])
        else:
            st.dataframe(df_dados)
