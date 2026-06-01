import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# =====================================================================
# 🪄 FUNÇÃO DE FORMATAÇÃO PREMIUM E TRADUÇÃO DE CRITÉRIOS
# =====================================================================
def formatar_nome_proprio(texto):
    if pd.isna(texto): return ""
    excecoes = ['de', 'da', 'do', 'das', 'dos', 'e']
    palavras = str(texto).strip().lower().split()
    return " ".join([p.capitalize() if p not in excecoes else p for p in palavras])

def qualificar_criterio(percentual, invertido=False):
    if not invertido:
        if percentual >= 35: return "Muito Alto / Excelente"
        elif percentual >= 25: return "Alto / Bom"
        elif percentual >= 15: return "Moderado"
        else: return "Baixo / Atenção"
    else: # Para riscos (ex: impulsividade)
        if percentual >= 35: return "Alto Risco"
        elif percentual >= 25: return "Risco Moderado-Alto"
        elif percentual >= 15: return "Risco Controlado"
        else: return "Baixo Risco"

# =====================================================================
# 🪄 TRUQUE DE COMPATIBILIDADE (RENDER)
# =====================================================================
if os.path.exists("secrets.toml"):
    os.makedirs(".streamlit", exist_ok=True)
    shutil.copy("secrets.toml", ".streamlit/secrets.toml")
# =====================================================================

st.set_page_config(
    page_title="MapeiaAI - Implantta Consultoria", 
    page_icon="🧠",
    layout="wide"
)

# =====================================================================
# 🎨 ESTILOS VISUAIS E MOTOR DE COMPACTAÇÃO DE PDF
# =====================================================================
st.markdown("""
    <style>
    div[data-baseweb="select"] > div { background-color: #2B5C8F !important; color: white !important; border-radius: 5px; }
    div[data-baseweb="select"] > div * { color: white !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    div[role="radiogroup"] label { color: white !important; }
    
    @media print {
        @page { size: A4 portrait; margin: 1cm; }
        section[data-testid="stSidebar"], header[data-testid="stHeader"], 
        div[data-testid="stSelectbox"], iframe, .no-print, details:not([open]) { 
            display: none !important; height: 0 !important;
        }
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; width: 100% !important; }
        div[data-testid="stAlert"] { padding: 10px !important; margin-bottom: 5px !important; }
        h1 { font-size: 26px !important; margin-top: 0 !important; padding-top: 0 !important; margin-bottom: 5px !important; }
        h3 { font-size: 18px !important; margin-top: 5px !important; margin-bottom: 5px !important;}
        h4 { font-size: 16px !important; margin-top: 5px !important; margin-bottom: 5px !important;}
        p { margin-bottom: 5px !important; }
        .stPlotlyChart, .stPlotlyChart > div, .js-plotly-plot, .plot-container { overflow: visible !important; page-break-inside: avoid !important; }
        [data-testid="stHorizontalBlock"] { page-break-inside: avoid !important; align-items: flex-start !important; }
        [data-testid="stVerticalBlock"], [data-testid="stExpander"], table { page-break-inside: avoid !important; margin-bottom: 5px !important; }
        h1, h2, h3, h4, h5, h6 { page-break-after: avoid !important; }
        * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        
        /* Estilo elegante para a tabela no PDF */
        table { width: 100%; border-collapse: collapse; font-size: 12px !important; }
        th { background-color: #2B5C8F !important; color: white !important; padding: 8px !important; text-align: left; }
        td { border-bottom: 1px solid #ddd; padding: 6px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ---- BARRA LATERAL (MENU) ----
try:
    st.sidebar.image("Versão Melhorada da Marca.png", use_container_width=True)
except:
    st.sidebar.subheader("🌱 Implantta Consultoria")

st.sidebar.markdown("---")
st.sidebar.title("Painel de Controle")
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato", "⚖️ Comparador (Ranking)"])

# 🔥 PALETA DE CORES
cores_animais = {"Tubarão": "#2B5C8F", "Lobo": "#5A6B7C", "Águia": "#DDA15E", "Gato": "#8EBCB5"}
cores_canais = {"Visual": "#1F4E5B", "Auditivo": "#2D728F", "Cinestésico": "#3B8EA5", "Digital (Lógico)": "#4D9A8E"}

# =====================================================================
# 🔌 CONEXÃO E AUTO-LIMPEZA DA PLANILHA
# =====================================================================
@st.cache_data(ttl=30) 
def carregar_dados_planilha():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        url_planilha = "https://docs.google.com/spreadsheets/d/1cz6O2iSync1c2E-lNGmEsgwMBrOgB2DHWz02A-y2g1Y/edit"
        df = conn.read(spreadsheet=url_planilha)
        
        if "Nome" not in df.columns:
            for i, row in df.iterrows():
                valores_linha = [str(val).lower().strip() for val in row.values]
                if "nome" in valores_linha or "nome do candidato" in valores_linha:
                    df.columns = row.values 
                    df = df.iloc[i+1:].reset_index(drop=True) 
                    break
                    
        df = df.loc[:, df.columns.notna()]
        coluna_nome = next((col for col in df.columns if "nome" in str(col).lower()), None)
                
        if coluna_nome:
            df = df.dropna(subset=[coluna_nome])
            df = df.rename(columns={coluna_nome: "Nome"})
            df["Nome"] = df["Nome"].apply(formatar_nome_proprio)
            if "Empresa" in df.columns: df["Empresa"] = df["Empresa"].apply(formatar_nome_proprio)
            if "Setor" in df.columns: df["Setor"] = df["Setor"].apply(formatar_nome_proprio)
            
        return df
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

df_dados = carregar_dados_planilha()

# =====================================================================
# 🧮 1. PROCESSAMENTO PNL E ANIMAIS
# =====================================================================
def calcular_sistema_representacional(linha):
    colunas_visual = ["Eu tomo decisões importantes baseados em: [o que me parece melhor]", "Durante uma discussão eu sou mais influenciado por: [se eu posso ou não ver o argumento da outra pessoa]", "Eu comunico mais facilmente o que se passa comigo: [do modo como me visto e aparento]", "É muito fácil para mim: [escolher as combinações de cores mais ricas e atraentes]", "Eu me percebo assim: [eu respondo fortemente às cores e à aparência de uma sala]"]
    colunas_auditivo = ["Eu tomo decisões importantes baseados em: [o que melhor me soar melhor]", "Durante uma discussão eu sou mais influenciado por: [tom de voz da outra pessoa]", "Eu comunico mais facilmente o que se passa comigo: [pelo tom da minha voz]", "É muito fácil para mim: [achar o volume e a sintonia ideais num sistema de som]", "Eu me percebo assim: [Se estou muito em sintonia com os sons do ambiente]"]
    colunas_cinestesico = ["Eu tomo decisões importantes baseados em: [intuição]", "Durante uma discussão eu sou mais influenciado por: [se eu entro em contato ou não com os sentimentos reais do outro]", "Eu comunico mais facilmente o que se passa comigo: [pelos sentimentos que compartilho]", "É muito fácil para mim: [escolher os móveis mais confortáveis]", "Eu me percebo assim: [eu sou muito sensível à maneira como a roupa veste o meu corpo]"]
    colunas_digital = ["Eu tomo decisões importantes baseados em: [um estudo preciso e minucioso do assunto]", "Durante uma discussão eu sou mais influenciado por: [a lógica do argumento da outra pessoa]", "Eu comunico mais facilmente o que se passa comigo: [pelas palavras que escolho]", "É muito fácil para mim: [selecionar o ponto mais relevante relativo a um assunto interessante]", "Eu me percebo assim: [se sou muito capaz de raciocinar com fatos e dados novos]"]
    
    v = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_visual])
    a = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_auditivo])
    c = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_cinestesico])
    d = sum([pd.to_numeric(linha.get(col, 0), errors='coerce') for col in colunas_digital])
    
    total = (v if pd.notna(v) else 0) + (a if pd.notna(a) else 0) + (c if pd.notna(c) else 0) + (d if pd.notna(d) else 0)
    if total > 0: return {"Visual": round((v/total)*100, 1), "Auditivo": round((a/total)*100, 1), "Cinestésico": round((c/total)*100, 1), "Digital": round((d/total)*100, 1)}
    return {"Visual": 25.0, "Auditivo": 25.0, "Cinestésico": 25.0, "Digital": 25.0}

gabarito_comportamental = {
    "Eu sou": {"Idealista, criativo e visionário": "Águia", "Divertido, espiritual e benéfico": "Gato", "Confiável, meticuloso e previsível": "Lobo", "Focado, determinado e persistente": "Tubarão"},
    "Eu gosto de ...": {"Ser piloto, o condutor": "Tubarão", "Conversar com os passageiros": "Gato", "Planejar a viajem": "Lobo", "Explorar novas rotas": "Águia"},
    "Se você quiser se dar bem comigo....": {"Me dê liberdade": "Águia", "Me deixe saber sua expectativa": "Lobo", "Lidere, siga ou saia do meu caminho": "Tubarão", "Seja amigável, carinhoso e compreensivo": "Gato"},
    "Para conseguir obter bons resultados é preciso...": {"Ter incertezas": "Águia", "Controlar o fundamental": "Lobo", "Diversão e comemoração": "Gato", "Planejar e obter os recursos para executar": "Tubarão"},
    "Eu me divirto quando...": {"Estou me exercitando": "Tubarão", "Tenho novidades": "Águia", "Estou com os outros": "Gato", "Determino as regras": "Lobo"},
    "Eu penso que...": {"Unidos venceremos, divididos perderemos": "Gato", "O ataque é melhor que a defesa": "Tubarão", "É bom ser manso, mas andar com um porrete": "Águia", "Um homem prevenido vale por dois": "Lobo"},
    "Minha preocupação é...": {"Gerar uma idéia global da situação": "Águia", "Fazer com que as pessoas gostem": "Gato", "Fazer com que a coisa funcione": "Lobo", "Fazer com que aconteça": "Tubarão"},
    "Eu escolho...": {"Perguntas ao invés de respostas": "Águia", "Ter todos os detalhes": "Lobo", "Vantagens a meu favor": "Tubarão", "Que todos tenham a chance de serem escutados": "Gato"},
    "Eu prefiro.": {"Fazer progressos": "Tubarão", "Construir memórias": "Gato", "Fazer sentido": "Lobo", "Tornar as pessoas confortáveis": "Águia"},
    "Eu gosto de chegar...": {"Na frente": "Tubarão", "Junto": "Gato", "Na hora": "Lobo", "Em outro lugar": "Águia"},
    "Um ótimo dia para mim é quando...": {"Consigo fazer muitas coisas": "Tubarão", "Me divirto com meus amigos": "Gato", "Tudo segue conforme planejado": "Lobo", "Desfruto de coisas novas e estimulantes": "Águia"},
    "Eu vejo a morte como...": {"Uma grande aventura misteriosa": "Águia", "Oportunidade para rever os falecidos": "Gato", "Um modo de receber recompensas": "Lobo", "Algo que sempre chega muito cedo": "Tubarão"},
    "Minha Filosofia de vida é...": {"Há ganhadores e perdedores, e eu sou um ganhador": "Tubarão", "Para eu ganhar, ninguém precisa perder": "Gato", "Para ganhar é preciso seguir as regras": "Lobo", "Para ganhar, é necessário inventar novas regras": "Águia"},
    "Eu sempre gostei de...": {"Explorar algo novo": "Águia", "Evitar surpresas": "Lobo", "Focalizar uma meta": "Tubarão", "Deixar acontecer naturalmente": "Gato"},
    "Eu gosto de mudanças se...": {"Me der mais liberdade e variedade": "Águia", "Melhorar ou me der mais controle da situação": "Lobo", "For divertido e puder ser compartilhado": "Gato", "Me der uma vantagem competitiva": "Tubarão"},
    "Não existe nada de errado em...": {"Se colocar na frente dos outros": "Tubarão", "Colocar os outros na frente": "Gato", "Ser consistente": "Lobo", "Mudar de idéia": "Águia"},
    "Eu gosto de buscar conselhos de...": {"Pessoas bem sucedidas": "Tubarão", "Anciões, idosos e conselheiros": "Gato", "Autoridades no assunto": "Lobo", "Lugares, até os mais estranhos": "Águia"},
    "Meu lema é...": {"Fazer o que precisa ser feito": "Águia", "Fazer bem feito": "Lobo", "Fazer Junto com o grupo": "Gato", "Simplesmente Fazer": "Tubarão"},
    "Para mim é essencial...": {"Complexidade mesmo que pareça confusa": "Águia", "Ordem e sistematização": "Lobo", "Calor humano e animação": "Gato", "Coisas claras e simples": "Tubarão"},
    "Tempo para mim é...": {"Algo que detesto desperdiçar": "Tubarão", "Um grande ciclo que termina e vem outro": "Gato", "Uma flecha que leva ao inevitável": "Lobo", "Irrelevante": "Águia"},
    "Se eu fosse bilionário...": {"Faria doações para muitas entidades": "Gato", "Criaria uma poupança avantajada": "Lobo", "Faria o que desse na cabeça": "Águia", "Exibiria bastante com algumas pessoas": "Tubarão"},
    "Eu acredito que...": {"O destino é mais importante que a jornada": "Tubarão", "A jornada é mais importante que o destino": "Gato", "Bastam um navio e uma estrela para navegar": "Águia", "Um centavo economizado é um centavo ganho": "Lobo"},
    "Eu acredito também que...": {"Aquele que hesita está perdido": "Tubarão", "De Grão em Grão a galinha enche o papo": "Lobo", "O que vai, volta": "Gato", "Um sorriso ou uma careta é igual para quem é cego": "Águia"},
    "Eu acredito ainda que...": {"É melhor prudência do que arrependimento": "Lobo", "A autoridade deve ser desafiada": "Águia", "Ganhar é fundamental": "Tubarão", "O coletivo é mais importante do que o individual": "Gato"},
    "Eu acho que...": {"Não é facil ficar cercado e pressionado": "Águia", "É preferivel olhar, antes de pular": "Lobo", "Duas cabeças pensam melhor do que uma": "Gato", "Se você não tem condições de competir, não compita": "Tubarão"}
}

def calcular_perfil_animais(linha):
    pontos = {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}
    total = 0
    for perg, alts in gabarito_comportamental.items():
        if perg in linha:
            resp = str(linha.get(perg, "")).strip().lower()
            for chave, animal in alts.items():
                if chave.strip().lower() in resp:
                    pontos[animal] += 1
                    total += 1
                    break
    if total > 0: return {a: round((v/total)*100, 1) for a, v in pontos.items()}
    return {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}

def categorizar_vaga(vaga):
    v_low = str(vaga).lower()
    cat1 = ["contab", "financ", "fiscal", "lobo", "adm", "process", "ti", "suport", "auditor", "qualidad", "estoque", "logistic", "motorist", "operacion"]
    cat2 = ["vend", "comercial", "geren", "diretor", "lider", "meta", "tubarao", "expansao", "negocio", "executiv", "corretor"]
    cat3 = ["rh", "human", "atend", "gato", "client", "relacionamento", "cs", "sucesso", "pessoal", "dp", "psico", "recep", "secret"]
    
    if any(k in v_low for k in cat1): return ["Lobo", "Tubarão"], "Processos/Operacional"
    elif any(k in v_low for k in cat2): return ["Tubarão", "Águia"], "Liderança/Comercial"
    elif any(k in v_low for k in cat3): return ["Gato", "Águia", "Lobo"], "Pessoas/Atendimento"
    else: return ["Lobo", "Tubarão", "Águia", "Gato"], "Geral/Dinâmico"

if df_dados is not None and "Nome" in df_dados.columns:
    lista_candidatos = df_dados["Nome"].unique()
else:
    lista_candidatos = ["Aguardando candidatos na planilha..."]

# =====================================================================
# TELA 1: PERFIL DO CANDIDATO (MANTIDA INTACTA)
# =====================================================================
if tela == "👤 Perfil do Candidato":
    col_sel, col_btn = st.columns([3, 1.5])
    with col_sel:
        candidato_sel = st.selectbox("Selecione o Candidato:", lista_candidatos)
    with col_btn:
        st.write("")
        script_pdf = f"""
        <script>function imprimirRelatorio() {{ try {{ var doc = window.parent.document; var tituloAntigo = doc.title; doc.title = "MapeiaAI - {candidato_sel}"; window.parent.print(); setTimeout(function() {{ doc.title = tituloAntigo; }}, 2000); }} catch(e) {{ window.print(); }} }}</script>
        <button onclick="imprimirRelatorio()" style="background-color: #DDA15E; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px;">📥 Salvar PDF do Candidato</button>
        """
        components.html(script_pdf, height=75)
        
    st.markdown('<hr class="no-print" style="margin: 0.5em 0;">', unsafe_allow_html=True)
    
    if df_dados is not None and "Nome" in df_dados.columns and candidato_sel in df_dados["Nome"].values:
        linha_cand = df_dados[df_dados["Nome"] == candidato_sel].iloc[0]
        vaga_alvo = linha_cand.get("Setor", "Não Informado")
        empresa_alvo = linha_cand.get("Empresa", "Não Informada")
        data_teste = linha_cand.get("Carimbo de data/hora", linha_cand.get("Data:", "Não Informada"))
        
        valores_canais = calcular_sistema_representacional(linha_cand)
        valores_animais = calcular_perfil_animais(linha_cand)
        
        with st.container():
            col_titulo, col_logo = st.columns([3.5, 1.5])
            with col_titulo:
                st.title("👤 Relatório de Engenharia de Perfil")
                st.caption("Mapeamento automatizado extraído em tempo real pela Implantta Consultoria.")
            with col_logo:
                try: st.image("Versão Melhorada da Marca.png", use_container_width=True)
                except: pass
            
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.info(f"**Candidato:**\n\n**{candidato_sel}**")
            col_b.info(f"**Vaga / Função:**\n\n{vaga_alvo}")
            col_c.info(f"**Empresa:**\n\n{empresa_alvo}")
            col_d.info(f"**Data da Aplicação:**\n\n{data_teste}")
                
        st.markdown('<br class="no-print">', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### 🦁 Perfil Comportamental Predominante")
            perfis_ordenados = sorted(valores_animais.items(), key=lambda x: x[1], reverse=True)
            top1_nome, top1_valor = perfis_ordenados[0]
            top2_nome, top2_valor = perfis_ordenados[1]
                
            df_animais = pd.DataFrame({"Perfil": list(valores_animais.keys()), "Percentual (%)": list(valores_animais.values())})
            fig_animais = px.pie(df_animais, names="Perfil", values="Percentual (%)", color="Perfil", color_discrete_map=cores_animais, hole=0.4)
            fig_animais.update_traces(textposition='inside', textinfo='percent+label')
            fig_animais.update_layout(height=240, showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_animais, use_container_width=True)
            
            st.markdown("#### 📊 Parecer Analítico")
            st.markdown(f"**Distribuição de Perfis:** Predominância Primária de **{top1_nome}** ({top1_valor}%) com suporte Secundário de **{top2_nome}** ({top2_valor}%).")

        with st.container():
            detalhes_perfis = {
                "Tubarão": {"fortes": "Foco em resultados, iniciativa, senso de urgência, coragem para decidir.", "fracos": "Dificuldade em delegar, tendência ao autoritarismo, inclinação a atropelar o planejamento."},
                "Lobo": {"fortes": "Organização cirúrgica, atenção extrema a detalhes, disciplina, lealdade a regras.", "fracos": "Resistência acentuada a mudanças repentinas, perfeccionismo, dificuldade de agir no improviso."},
                "Águia": {"fortes": "Pensamento disruptivo, criatividade, facilidade de adaptação, olhar de longo prazo.", "fracos": "Falta de linearidade na execução, propensão a perder o foco e indisciplina com prazos."},
                "Gato": {"fortes": "Excelente comunicação interpessoal, mediação de conflitos, facilidade para trabalhar em equipe.", "fracos": "Dificuldade para dar feedbacks duros, tendência a evitar confrontos necessários."}
            }
            
            perfis_ideais, tipo_vaga = categorizar_vaga(vaga_alvo)
            convergente = (top1_nome in perfis_ideais)

            col_fortes, col_fracos = st.columns(2)
            with col_fortes:
                with st.expander("⭐ Pontos Fortes do Candidato", expanded=True):
                    st.write(f"• **{top1_nome}:** {detalhes_perfis[top1_nome]['fortes']}")
                    if top2_valor > 15: st.write(f"• **{top2_nome}:** {detalhes_perfis[top2_nome]['fortes']}")
            with col_fracos:
                with st.expander("⚠️ Pontos de Atenção (Fraquezas)", expanded=True):
                    st.write(f"• **{top1_nome}:** {detalhes_perfis[top1_nome]['fracos']}")
                    if top2_valor > 15: st.write(f"• **{top2_nome}:** {detalhes_perfis[top2_nome]['fracos']}")

        with st.container():
            st.markdown("#### 🎯 Alinhamento com a Função & Conclusão")
            predominante_pnl = max(valores_canais, key=valores_canais.get)
            pnl_detalhes = {
                "Visual": "processa informações em alta velocidade, ideal para rotinas dinâmicas e de alta carga visual.",
                "Auditivo": "excelente para posições que exigem escuta ativa, diálogo e forte negociação verbal.",
                "Cinestésico": "melhor aproveitado em funções práticas, que envolvem contato, intuição e estabilidade.",
                "Digital": "altamente analítico, ideal para cenários que exigem validação de dados, fatos e lógica fria."
            }
            
            col_concl1, col_concl2 = st.columns([1.5, 1])
            with col_concl1:
                st.markdown(f"**Engenharia de Cargo:** A vaga indicada (**{vaga_alvo}**) possui características do tipo *{tipo_vaga}*. Para este cenário, os perfis recomendados são **{', '.join(perfis_ideais)}**.\n\nO candidato combina essa estrutura com um canal predominantemente **{predominante_pnl}**, o que significa que ele {pnl_detalhes.get(predominante_pnl, '')}")
                
            with col_concl2:
                if convergente:
                    st.success("✅ RECOMENDAÇÃO: **CONTRATAR**")
                    st.caption("🏆 **Justificativa:** Alta aderência comportamental com o escopo da vaga.")
                elif top2_nome in perfis_ideais:
                    st.warning("🟡 RECOMENDAÇÃO: **AVALIAR COM RESSALVAS**")
                    st.caption("👀 **Justificativa:** O perfil principal difere do esperado, mas o secundário equilibra.")
                else:
                    st.error("❌ RECOMENDAÇÃO: **DESALINHADO À VAGA**")
                    st.caption("🚨 **Justificativa:** Desalinhamento natural com as rotinas diárias da função.")

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
        colunas_exibicao = [col for col in ["Carimbo de data/hora", "Nome", "Empresa", "Setor"] if col in df_dados.columns]
        if colunas_exibicao: st.dataframe(df_dados[colunas_exibicao])

# =====================================================================
# TELA 3: COMPARADOR (NOVA FUNCIONALIDADE)
# =====================================================================
elif tela == "⚖️ Comparador (Ranking)":
    st.title("⚖️ Comparador e Ranking de Candidatos")
    
    col_input1, col_input2 = st.columns([2, 1])
    with col_input1:
        candidatos_selecionados = st.multiselect("Selecione os candidatos para comparar (2 ou mais):", lista_candidatos)
    with col_input2:
        vaga_referencia = st.text_input("Cargo/Vaga Referência:", placeholder="Ex: Motorista, Contábil, Vendedor...")
    
    # Botão de Impressão
    script_pdf_comp = """
    <script>function imprimirRelatorio() { try { var doc = window.parent.document; var tituloAntigo = doc.title; doc.title = "Comparativo_Candidatos"; window.parent.print(); setTimeout(function() { doc.title = tituloAntigo; }, 2000); } catch(e) { window.print(); } }</script>
    <button onclick="imprimirRelatorio()" style="background-color: #5A6B7C; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-bottom: 20px;">📥 Salvar PDF Comparativo</button>
    """
    components.html(script_pdf_comp, height=55)

    if len(candidatos_selecionados) >= 2 and vaga_referencia:
        st.markdown("---")
        st.markdown(f"### 📊 Análise Comparativa para: **{vaga_referencia}**")
        
        perfis_ideais, tipo_vaga = categorizar_vaga(vaga_referencia)
        st.info(f"**Categoria da Vaga:** {tipo_vaga} | **Perfis de Maior Aderência:** {', '.join(perfis_ideais)}")
        
        dados_comparativos = []
        for cand in candidatos_selecionados:
            linha_cand = df_dados[df_dados["Nome"] == cand].iloc[0]
            animais = calcular_perfil_animais(linha_cand)
            
            # Cálculo do Fit Cultural (Nota de Aderência baseada na vaga)
            nota_aderencia = sum([animais[p] for p in perfis_ideais])
            
            if nota_aderencia >= 65:
                adequacao = "Excelente"
            elif nota_aderencia >= 45:
                adequacao = "Boa"
            elif nota_aderencia >= 30:
                adequacao = "Moderada"
            else:
                adequacao = "Baixa"
            
            # Tradução dos Animais para Critérios Profissionais
            agilidade = animais["Tubarão"]
            organizacao = animais["Lobo"]
            atencao_detalhes = animais["Lobo"]
            eq_emocional = animais["Gato"] + (animais["Lobo"] * 0.5)
            relacionamento = animais["Gato"]
            lidar_pressao = animais["Tubarão"] + (animais["Águia"] * 0.5)
            adaptabilidade = animais["Águia"]
            disciplina = animais["Lobo"]
            risco_impulsividade = animais["Tubarão"] + animais["Águia"]

            dados_comparativos.append({
                "Candidato": formatar_nome_proprio(cand),
                "Nota de Aderência": nota_aderencia,
                "Adequação Geral": adequacao,
                "Agilidade e Senso de Urgência": qualificar_criterio(agilidade),
                "Organização e Regras": qualificar_criterio(organizacao),
                "Atenção a Detalhes": qualificar_criterio(atencao_detalhes),
                "Equilíbrio Emocional": qualificar_criterio(eq_emocional),
                "Relacionamento Interpessoal": qualificar_criterio(relacionamento),
                "Lidar com Pressão": qualificar_criterio(lidar_pressao),
                "Adaptabilidade a Imprevistos": qualificar_criterio(adaptabilidade),
                "Disciplina Operacional": qualificar_criterio(disciplina),
                "Risco de Impulsividade": qualificar_criterio(risco_impulsividade, invertido=True),
                "Animais Base": f"1º {max(animais, key=animais.get)}"
            })

        # Ordenar pelo Ranking (Maior Nota primeiro)
        dados_comparativos.sort(key=lambda x: x["Nota de Aderência"], reverse=True)
        
        # Gerar a Tabela Dinâmica
        df_tabela = pd.DataFrame(dados_comparativos)
        
        colunas_tabela = ["Candidato", "Agilidade e Senso de Urgência", "Organização e Regras", "Atenção a Detalhes", "Equilíbrio Emocional", "Relacionamento Interpessoal", "Lidar com Pressão", "Adaptabilidade a Imprevistos", "Disciplina Operacional", "Risco de Impulsividade", "Adequação Geral"]
        
        st.markdown("#### 📋 Matriz de Critérios Inerentes à Vaga")
        st.dataframe(df_tabela[colunas_tabela].set_index("Candidato"), use_container_width=True)
        
        # Parecer Final e Ranking
        st.markdown("#### 🏆 Parecer Comparativo e Ranking Final")
        
        for i, candidato in enumerate(dados_comparativos):
            lugar = i + 1
            nome = candidato["Candidato"]
            nota = candidato["Nota de Aderência"]
            perfil = candidato["Animais Base"].split("1º ")[1]
            adequacao = candidato["Adequação Geral"]
            
            if lugar == 1:
                st.markdown(f"🥇 **1º Lugar: {nome} (Aderência {adequacao})**")
                st.write(f"Apresenta o perfil comportamental primário de **{perfil}**, garantindo o melhor equilíbrio e alinhamento prático com o contexto da vaga de {vaga_referencia}. Demonstra {colunas_tabela[1].lower()} ({candidato[colunas_tabela[1]]}) e {colunas_tabela[2].lower()} ({candidato[colunas_tabela[2]]}), possuindo a maior tração operacional para assumir a rotina proposta de forma imediata.")
            else:
                st.markdown(f"**{lugar}º Lugar: {nome} (Aderência {adequacao})**")
                st.write(f"Possui perfil de **{perfil}**, sendo compatível em diversas instâncias, com destaque para {colunas_tabela[7].lower()} ({candidato[colunas_tabela[7]]}). Contudo, no cruzamento total de competências exigidas para {vaga_referencia}, o seu indicador de {colunas_tabela[9].lower()} ({candidato[colunas_tabela[9]]}) ou alinhamento técnico exige um acompanhamento mais próximo da gestão caso seja contratado.")
                
        st.success(f"**Conclusão da Consultoria:** Todos os candidatos avaliados apresentam pontos fortes distintos. No entanto, o candidato **{dados_comparativos[0]['Candidato']}** é o mais recomendado, apresentando a maior nota global de Fit Cultural e o menor risco operacional para o escopo da função de {vaga_referencia}.")

    elif len(candidatos_selecionados) > 0:
        st.warning("Selecione pelo menos 2 candidatos e escreva o nome da vaga para gerar a comparação.")
