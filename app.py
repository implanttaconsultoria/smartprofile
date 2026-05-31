import os
import shutil
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# =====================================================================
# 🪄 FUNÇÃO DE FORMATAÇÃO PREMIUM (Nomes, Vagas e Empresas)
# =====================================================================
def formatar_nome_proprio(texto):
    if pd.isna(texto): return ""
    excecoes = ['de', 'da', 'do', 'das', 'dos', 'e']
    palavras = str(texto).strip().lower().split()
    return " ".join([p.capitalize() if p not in excecoes else p for p in palavras])

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
# 🎨 ESTILOS VISUAIS E MOTOR DE COMPACTAÇÃO DE PDF (PERFEITO PARA PC)
# =====================================================================
st.markdown("""
    <style>
    /* Ajuste da Caixa de Seleção: Fundo Azul e Fonte Branca */
    div[data-baseweb="select"] > div {
        background-color: #2B5C8F !important;
        color: white !important;
        border-radius: 5px;
    }
    div[data-baseweb="select"] > div * {
        color: white !important;
    }
    
    /* Menu Lateral Branco para Contraste */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    div[role="radiogroup"] label {
        color: white !important;
    }
    
    /* Configurações Estritas para a Geração do PDF Perfeito no PC */
    @media print {
        @page {
            size: A4 portrait;
            margin: 1cm; /* Margem reduzida para dar mais espaço ao conteúdo */
        }
        
        /* Oculta botões, menus, caixas fechadas e o botão de imprimir */
        section[data-testid="stSidebar"], 
        header[data-testid="stHeader"], 
        div[data-testid="stSelectbox"],
        iframe, 
        .no-print,
        details:not([open]) { 
            display: none !important; 
            height: 0 !important;
        }

        /* Remove margens extras para aproveitar a página inteira */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
        }

        /* Compacta as Caixas de Informação do Candidato */
        div[data-testid="stAlert"] {
            padding: 10px !important;
            margin-bottom: 5px !important;
        }
        
        /* Ajusta o tamanho dos títulos no papel para não roubar espaço */
        h1 { font-size: 26px !important; margin-top: 0 !important; padding-top: 0 !important; margin-bottom: 5px !important; }
        h3 { font-size: 18px !important; margin-top: 5px !important; margin-bottom: 5px !important;}
        h4 { font-size: 16px !important; margin-top: 5px !important; margin-bottom: 5px !important;}
        p { margin-bottom: 5px !important; }

        /* IMPEDE CORTES: Garante que os gráficos fiquem 100% visíveis */
        .stPlotlyChart, .stPlotlyChart > div, .js-plotly-plot, .plot-container {
            overflow: visible !important;
            page-break-inside: avoid !important;
        }

        /* BLINDAGEM DE QUEBRA DE PÁGINA COM AS COLUNAS PERFEITAS */
        [data-testid="stHorizontalBlock"] { 
            page-break-inside: avoid !important; 
            align-items: flex-start !important;
        }
        [data-testid="stVerticalBlock"], [data-testid="stExpander"] {
            page-break-inside: avoid !important;
            margin-bottom: 5px !important;
        }
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid !important;
        }
        
        /* Força a impressão das cores corporativas */
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
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
tela = st.sidebar.radio("Navegar para:", ["📊 Dashboard Geral", "👤 Perfil do Candidato"])

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
        
        coluna_nome = None
        for col in df.columns:
            if "nome" in str(col).lower():
                coluna_nome = col
                break
                
        if coluna_nome:
            df = df.dropna(subset=[coluna_nome])
            df = df.rename(columns={coluna_nome: "Nome"})
            
            # 🪄 APLICA A FORMATAÇÃO PERFEITA NAS COLUNAS PRINCIPAIS
            df["Nome"] = df["Nome"].apply(formatar_nome_proprio)
            if "Empresa" in df.columns:
                df["Empresa"] = df["Empresa"].apply(formatar_nome_proprio)
            if "Setor" in df.columns:
                df["Setor"] = df["Setor"].apply(formatar_nome_proprio)
            
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
        return {"Visual": round((v_score / total) * 100, 1), "Auditivo": round((a_score / total) * 100, 1), "Cinestésico": round((c_score / total) * 100, 1), "Digital (Lógico)": round((d_score / total) * 100, 1)}
    return {"Visual": 25.0, "Auditivo": 25.0, "Cinestésico": 25.0, "Digital (Lógico)": 25.0}

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
    "Tempo para mim é...": {"Algo que detesto desperprdiçar": "Tubarão", "Um grande ciclo que termina e vem outro": "Gato", "Uma flecha que leva ao inevitável": "Lobo", "Irrelevante": "Águia"},
    "Se eu fosse bilionário...": {"Faria doações para muitas entidades": "Gato", "Criaria uma poupança avantajada": "Lobo", "Faria o que desse na cabeça": "Águia", "Exibiria bastante com algumas pessoas": "Tubarão"},
    "Eu acredito que...": {"O destino é mais importante que a jornada": "Tubarão", "A jornada é mais importante que o destino": "Gato", "Bastam um navio e uma estrela para navegar": "Águia", "Um centavo economizado é um centavo ganho": "Lobo"},
    "Eu acredito também que...": {"Aquele que hesita está perdido": "Tubarão", "De Grão em Grão a galinha enche o papo": "Lobo", "O que vai, volta": "Gato", "Um sorriso ou uma careta é igual para quem é cego": "Águia"},
    "Eu acredito ainda que...": {"É melhor prudência do que arrependimento": "Lobo", "A autoridade deve ser desafiada": "Águia", "Ganhar é fundamental": "Tubarão", "O coletivo é mais importante do que o individual": "Gato"},
    "Eu acho que...": {"Não é facil ficar cercado e pressionado": "Águia", "É preferivel olhar, antes de pular": "Lobo", "Duas cabeças pensam melhor do que uma": "Gato", "Se você não tem condições de competir, não compita": "Tubarão"}
}

def calcular_perfil_animais(linha):
    pontos = {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}
    total_respondido = 0
    for pergunta, alternativas in gabarito_comportamental.items():
        if pergunta in linha:
            resposta_cand = str(linha.get(pergunta, "")).strip().lower()
            for resp_chave, animal in alternativas.items():
                if resp_chave.strip().lower() in resposta_cand:
                    pontos[animal] += 1
                    total_respondido += 1
                    break
    percentuais = {}
    if total_respondido > 0:
        for animal, valor in pontos.items():
            percentuais[animal] = round((valor / total_respondido) * 100, 1)
    else:
        percentuais = {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}
    return percentuais

if df_dados is not None and "Nome" in df_dados.columns:
    lista_candidatos = df_dados["Nome"].unique()
else:
    lista_candidatos = ["Aguardando candidatos na planilha..."]

# =====================================================================
# TELA 1: PERFIL DO CANDIDATO
# =====================================================================
if tela == "👤 Perfil do Candidato":
    
    # 🌟 CONTROLES NO TOPO (Botão com a lógica perfeita para o PC)
    col_sel, col_btn = st.columns([3, 1.5])
    with col_sel:
        candidato_sel = st.selectbox("Selecione o Candidato:", lista_candidatos)
    
    with col_btn:
        st.write("")
        script_pdf = f"""
        <script>
            function imprimirRelatorio() {{
                try {{
                    var doc = window.parent.document;
                    var tituloAntigo = doc.title;
                    doc.title = "MapeiaAI - Implantta Consultoria - {candidato_sel}";
                    window.parent.print();
                    setTimeout(function() {{ doc.title = tituloAntigo; }}, 2000);
                }} catch(e) {{
                    window.print();
                }}
            }}
        </script>
        <button onclick="imprimirRelatorio()" style="
            background-color: #DDA15E; color: white; border: none; padding: 10px 15px; 
            border-radius: 5px; cursor: pointer; font-family: sans-serif; font-weight: bold;
            font-size: 14px; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;
            margin-top: 10px;
        " onmouseover="this.style.backgroundColor='#c98d4b'" onmouseout="this.style.backgroundColor='#DDA15E'">
            📥 Salvar PDF do Candidato
        </button>
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
        
        # 🌟 CABEÇALHO OFICIAL DO RELATÓRIO
        with st.container():
            col_titulo, col_logo = st.columns([3.5, 1.5])
            with col_titulo:
                st.title("👤 Relatório de Engenharia de Perfil")
                st.caption("Mapeamento automatizado extraído em tempo real pela Implantta Consultoria.")
            with col_logo:
                try:
                    st.image("Versão Melhorada da Marca.png", use_container_width=True)
                except:
                    pass
            
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.info(f"**Candidato:**\n\n**{candidato_sel}**")
            col_b.info(f"**Vaga / Função:**\n\n{vaga_alvo}")
            col_c.info(f"**Empresa:**\n\n{empresa_alvo}")
            col_d.info(f"**Data da Aplicação:**\n\n{data_teste}")
                
        st.markdown('<br class="no-print">', unsafe_allow_html=True)
        
        # 🟢 BLOCO 1: GRÁFICO DOS ANIMAIS
        with st.container():
            st.markdown("### 🦁 Perfil Comportamental Predominante")
            
            perfis_ordenados = sorted(valores_animais.items(), key=lambda x: x[1], reverse=True)
            top1_nome, top1_valor = perfis_ordenados[0]
            top2_nome, top2_valor = perfis_ordenados[1]
                
            df_animais = pd.DataFrame({
                "Perfil": list(valores_animais.keys()), 
                "Percentual (%)": list(valores_animais.values())
            })
            fig_animais = px.pie(
                df_animais, 
                names="Perfil", 
                values="Percentual (%)", 
                color="Perfil", 
                color_discrete_map=cores_animais, 
                hole=0.4
            )
            fig_animais.update_traces(textposition='inside', textinfo='percent+label')
            fig_animais.update_layout(height=240, showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_animais, use_container_width=True)
            
            st.markdown("#### 📊 Parecer Analítico")
            st.markdown(f"**Distribuição de Perfis:** Predominância Primária de **{top1_nome}** ({top1_valor}%) com suporte Secundário de **{top2_nome}** ({top2_valor}%).")

        # 🟢 BLOCO 2: CAIXAS DE PONTOS FORTES E FRACOS
        with st.container():
            detalhes_perfis = {
                "Tubarão": {"fortes": "Foco em resultados, iniciativa, senso de urgência, coragem para decidir.", "fracos": "Dificuldade em delegar, tendência ao autoritarismo, inclinação a atropelar o planejamento."},
                "Lobo": {"fortes": "Organização cirúrgica, atenção extrema a detalhes, disciplina, lealdade a regras.", "fracos": "Resistência acentuada a mudanças repentinas, perfeccionismo, dificuldade de agir no improviso."},
                "Águia": {"fortes": "Pensamento disruptivo, criatividade, facilidade de adaptação, olhar de longo prazo.", "fracos": "Falta de linearidade na execução, propensão a perder o foco e indisciplina com prazos."},
                "Gato": {"fortes": "Excelente comunicação interpessoal, mediação de conflitos, facilidade para trabalhar em equipe.", "fracos": "Dificuldade para dar feedbacks duros, tendência a evitar confrontos necessários."}
            }
            
            # Lógica inteligente das vagas mantida!
            vaga_lower = str(vaga_alvo).lower()
            
            if any(k in vaga_lower for k in ["contab", "financ", "fiscal", "lobo", "adm", "process", "ti", "suport", "auditor", "qualidad", "estoque", "logistica"]):
                tipo_vaga = "Processos/Contábil/Analítico"
                perfis_ideais = ["Lobo", "Tubarão"]
                is_general = False
            elif any(k in vaga_lower for k in ["vend", "comercial", "geren", "diretor", "lider", "meta", "tubarao", "expansao", "negocio"]):
                tipo_vaga = "Comercial/Liderança/Execução"
                perfis_ideais = ["Tubarão", "Águia"]
                is_general = False
            elif any(k in vaga_lower for k in ["rh", "human", "atend", "gato", "client", "relacionamento", "cs", "sucesso", "pessoal", "dp", "psico", "recep"]):
                tipo_vaga = "Pessoas/Atendimento/Suporte"
                perfis_ideais = ["Gato", "Águia"]
                is_general = False
            else:
                tipo_vaga = "Função Dinâmica / Não Específica"
                perfis_ideais = ["(Depende do escopo exato da vaga)"]
                is_general = True
                
            convergente = (top1_nome in perfis_ideais)

            col_fortes, col_fracos = st.columns(2)
            with col_fortes:
                with st.expander("⭐ Pontos Fortes do Candidato", expanded=True):
                    st.write(f"• **{top1_nome}:** {detalhes_perfis[top1_nome]['fortes']}")
                    if top2_valor > 15:
                        st.write(f"• **{top2_nome}:** {detalhes_perfis[top2_nome]['fortes']}")
            with col_fracos:
                with st.expander("⚠️ Pontos de Atenção (Fraquezas)", expanded=True):
                    st.write(f"• **{top1_nome}:** {detalhes_perfis[top1_nome]['fracos']}")
                    if top2_valor > 15:
                        st.write(f"• **{top2_nome}:** {detalhes_perfis[top2_nome]['fracos']}")

        # 🎯 BLOCO 3: CONCLUSÃO
        with st.container():
            st.markdown("#### 🎯 Alinhamento com a Função & Conclusão")
            
            predominante_pnl = max(valores_canais, key=valores_canais.get)
            pnl_detalhes = {
                "Visual": "processa informações em alta velocidade, ideal para rotinas dinâmicas e de alta carga visual.",
                "Auditivo": "excelente para posições que exigem escuta ativa, diálogo e forte negociação verbal.",
                "Cinestésico": "melhor aproveitado em funções práticas, que envolvem contato, intuição e estabilidade.",
                "Digital (Lógico)": "altamente analítico, ideal para cenários que exigem validação de dados, fatos e lógica fria."
            }
            
            col_concl1, col_concl2 = st.columns([1.5, 1])
            with col_concl1:
                st.markdown(f"**Engenharia de Cargo:** A vaga indicada (**{vaga_alvo}**) possui características do tipo *{tipo_vaga}*. Para este cenário, os perfis recomendados são **{', '.join(perfis_ideais)}**.\n\nO candidato combina essa estrutura com um canal predominantemente **{predominante_pnl}**, o que significa que ele {pnl_detalhes[predominante_pnl]}")
                
            with col_concl2:
                if is_general:
                    st.warning("🟡 RECOMENDAÇÃO: **AVALIAÇÃO DO GESTOR**")
                    st.caption("👀 **Justificativa:** O título da vaga não tem um perfil engessado. Avalie se as forças do candidato atendem à rotina.")
                elif convergente:
                    st.success("✅ RECOMENDAÇÃO: **CONTRATAR**")
                    st.caption("🏆 **Justificativa:** Alta aderência comportamental com o escopo da vaga.")
                elif top2_nome in perfis_ideais:
                    st.warning("🟡 RECOMENDAÇÃO: **AVALIAR COM RESSALVAS**")
                    st.caption("👀 **Justificativa:** O perfil principal difere do esperado, mas o secundário equilibra.")
                else:
                    st.error("❌ RECOMENDAÇÃO: **DESALINHADO À VAGA**")
                    st.caption("🚨 **Justificativa:** Desalinhamento natural com as rotinas diárias da função.")
                        
            st.markdown("---")
        
        # 🔵 BLOCO 4: PNL E MANUAL
        with st.container():
            st.subheader("📊 Sistema Representacional (PNL)")
            
            df_chart = pd.DataFrame({"Canal": list(valores_canais.keys()), "Percentagem (%)": list(valores_canais.values())})
            fig = px.bar(df_chart, x="Canal", y="Percentagem (%)", color="Canal", text="Percentagem (%)", template="streamlit", color_discrete_map=cores_canais)
            fig.update_layout(height=260, showlegend=False, margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🧠 Manual de Relacionamento (Liderança)")
            st.info("💡 **Dica para a Gestão:** Use o canal predominante para guiar a comunicação diária com o colaborador.")
            
            st.markdown(f"""
            Como o candidato possui o canal **{predominante_pnl}** mais elevado, aja da seguinte forma:
            * **Se for Visual:** Use termos como *"Veja bem"*, *"Imagine esse cenário"*. Mantenha contato visual e apoie-se em imagens.
            * **Se for Auditivo:** Module o tom de voz, evite dar ordens em ambientes barulhentos. Use *"Me conte o que acha"*.
            * **Se for Cinestésico:** Crie um clima acolhedor antes de corrigir, valorize o lado humano e dê espaço para ele experimentar na prática.
            * **Se for Digital:** Vá direto ao ponto apresentando fatos, planilhas e lógicas claras. Evite apelo puramente emocional.
            """)
            
            st.markdown('<hr class="no-print">', unsafe_allow_html=True)
            with st.expander("🔍 Ver Respostas Brutas do Teste Comportamental (Texto)", expanded=False):
                perguntas_texto = list(gabarito_comportamental.keys())
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
        
        colunas_exibicao = [col for col in ["Carimbo de data/hora", "Nome", "Empresa", "Setor"] if col in df_dados.columns]
        if colunas_exibicao:
            st.dataframe(df_dados[colunas_exibicao])
        else:
            st.dataframe(df_dados)
