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

# 🔥 NOVA PALETA DE CORES: SÓBRIA, PROFISSIONAL E COM ALTO CONTRASTE
cores_animais = {
    "Tubarão": "#2B5C8F",   # Azul Oceano Sóbrio (Foco, Execução)
    "Lobo": "#5A6B7C",      # Cinza Corporativo (Ordem, Processos)
    "Águia": "#DDA15E",     # Ouro Velho / Mostarda Sóbrio (Criatividade, Visão)
    "Gato": "#8EBCB5"       # Verde Sálvia / Menta Sóbrio (Empatia, Pessoas)
}

cores_canais = {
    "Visual": "#1F4E5B", 
    "Auditivo": "#2D728F", 
    "Cinestésico": "#3B8EA5", 
    "Digital (Lógico)": "#4D9A8E"
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
            
        return df
    except Exception as e:
        st.error(f"Erro de conexão ou processamento: {e}")
        return None

df_dados = carregar_dados_planilha()

# =====================================================================
# 🧮 1. PROCESSAMENTO PNL
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

# =====================================================================
# 🦁 2. PROCESSAMENTO TESTE COMPORTAMENTAL (ANIMAIS)
# =====================================================================
gabarito_comportamental = {
    "Eu sou": {
        "Idealista, criativo e visionário": "Águia",
        "Divertido, espiritual e benéfico": "Gato",
        "Confiável, meticuloso e previsível": "Lobo",
        "Focado, determinado e persistente": "Tubarão"
    },
    "Eu gosto de ...": {
        "Ser piloto, o condutor": "Tubarão",
        "Conversar com os passageiros": "Gato",
        "Planejar a viajem": "Lobo",
        "Explorar novas rotas": "Águia"
    },
    "Se você quiser se dar bem comigo....": {
        "Me dê liberdade": "Águia",
        "Me deixe saber sua expectativa": "Lobo",
        "Lidere, siga ou saia do meu caminho": "Tubarão",
        "Seja amigável, carinhoso e compreensivo": "Gato"
    },
    "Para conseguir obter bons resultados é preciso...": {
        "Ter incertezas": "Águia",
        "Controlar o fundamental": "Lobo",
        "Diversão e comemoração": "Gato",
        "Planejar e obter os recursos para executar": "Tubarão"
    },
    "Eu me divirto quando...": {
        "Estou me exercitando": "Tubarão",
        "Tenho novidades": "Águia",
        "Estou com os outros": "Gato",
        "Determino as regras": "Lobo"
    },
    "Eu penso que...": {
        "Unidos venceremos, divididos perderemos": "Gato",
        "O ataque é melhor que a defesa": "Tubarão",
        "É bom ser manso, mas andar com um porrete": "Águia",
        "Um homem prevenido vale por dois": "Lobo"
    },
    "Minha preocupação é...": {
        "Gerar uma idéia global da situação": "Águia",
        "Fazer com que as pessoas gostem": "Gato",
        "Fazer com que a coisa funcione": "Lobo",
        "Fazer com que aconteça": "Tubarão"
    },
    "Eu escolho...": {
        "Perguntas ao invés de respostas": "Águia",
        "Ter todos os detalhes": "Lobo",
        "Vantagens a meu favor": "Tubarão",
        "Que todos tenham a chance de serem escutados": "Gato"
    },
    "Eu prefiro.": {
        "Fazer progressos": "Tubarão",
        "Construir memórias": "Gato",
        "Fazer sentido": "Lobo",
        "Tornar as pessoas confortáveis": "Águia"
    },
    "Eu gosto de chegar...": {
        "Na frente": "Tubarão",
        "Junto": "Gato",
        "Na hora": "Lobo",
        "Em outro lugar": "Águia"
    },
    "Um ótimo dia para mim é quando...": {
        "Consigo fazer muitas coisas": "Tubarão",
        "Me divirto com meus amigos": "Gato",
        "Tudo segue conforme planejado": "Lobo",
        "Desfruto de coisas novas e estimulantes": "Águia"
    },
    "Eu vejo a morte como...": {
        "Uma grande aventura misteriosa": "Águia",
        "Oportunidade para rever os falecidos": "Gato",
        "Um modo de receber recompensas": "Lobo",
        "Algo que sempre chega muito cedo": "Tubarão"
    },
    "Minha Filosofia de vida é...": {
        "Há ganhadores e perdedores, e eu sou um ganhador": "Tubarão",
        "Para eu ganhar, ninguém precisa perder": "Gato",
        "Para ganhar é preciso seguir as regras": "Lobo",
        "Para ganhar, é necessário inventar novas regras": "Águia"
    },
    "Eu sempre gostei de...": {
        "Explorar algo novo": "Águia",
        "Evitar surpresas": "Lobo",
        "Focalizar uma meta": "Tubarão",
        "Deixar acontecer naturalmente": "Gato"
    },
    "Eu gosto de mudanças se...": {
        "Me der mais liberdade e variedade": "Águia",
        "Melhorar ou me der mais controle da situação": "Lobo",
        "For divertido e puder ser compartilhado": "Gato",
        "Me der uma vantagem competitiva": "Tubarão"
    },
    "Não existe nada de errado em...": {
        "Se colocar na frente dos outros": "Tubarão",
        "Colocar os outros na frente": "Gato",
        "Ser consistente": "Lobo",
        "Mudar de idéia": "Águia"
    },
    "Eu gosto de buscar conselhos de...": {
        "Pessoas bem sucedidas": "Tubarão",
        "Anciões, idosos e conselheiros": "Gato",
        "Autoridades no assunto": "Lobo",
        "Lugares, até os mais estranhos": "Águia"
    },
    "Meu lema é...": {
        "Fazer o que precisa ser feito": "Águia",
        "Fazer bem feito": "Lobo",
        "Fazer Junto com o grupo": "Gato",
        "Simplesmente Fazer": "Tubarão"
    },
    "Para mim é essencial...": {
        "Complexidade mesmo que pareça confusa": "Águia",
        "Ordem e sistematização": "Lobo",
        "Calor humano e animação": "Gato",
        "Coisas claras e simples": "Tubarão"
    },
    "Tempo para mim é...": {
        "Algo que detesto desperdiçar": "Tubarão",
        "Um grande ciclo que termina e vem outro": "Gato",
        "Uma flecha que leva ao inevitável": "Lobo",
        "Irrelevante": "Águia"
    },
    "Se eu fosse bilionário...": {
        "Faria doações para muitas entidades": "Gato",
        "Criaria uma poupança avantajada": "Lobo",
        "Faria o que desse na cabeça": "Águia",
        "Exibiria bastante com algumas pessoas": "Tubarão"
    },
    "Eu acredito que...": {
        "O destino é mais importante que a jornada": "Tubarão",
        "A jornada é mais importante que o destino": "Gato",
        "Bastam um navio e uma estrela para navegar": "Águia",
        "Um centavo economizado é um centavo ganho": "Lobo"
    },
    "Eu acredito também que...": {
        "Aquele que hesita está perdido": "Tubarão",
        "De Grão em Grão a galinha enche o papo": "Lobo",
        "O que vai, volta": "Gato",
        "Um sorriso ou uma careta é igual para quem é cego": "Águia"
    },
    "Eu acredito ainda que...": {
        "É melhor prudência do que arrependimento": "Lobo",
        "A autoridade deve ser desafiada": "Águia",
        "Ganhar é fundamental": "Tubarão",
        "O coletivo é mais importante do que o individual": "Gato"
    },
    "Eu acho que...": {
        "Não é facil ficar cercado e pressionado": "Águia",
        "É preferivel olhar, antes de pular": "Lobo",
        "Duas cabeças pensam melhor do que uma": "Gato",
        "Se você não tem condições de competir, não compita": "Tubarão"
    }
}

def calcular_perfil_animais(linha):
    pontos = {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}
    total_respondido = 0
    
    for pergunta, alternativas in gabarito_comportamental.items():
        # AQUI ESTAVA O ERRO DE DIGITAÇÃO (line -> linha)
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
        
        vaga_alvo = linha_cand.get("Setor", "Não Informado")
        empresa_alvo = linha_cand.get("Empresa", "Não Informada")
        email_cand = linha_cand.get("Endereço de e-mail", "Não Informado")
        data_teste = linha_cand.get("Carimbo de data/hora", linha_cand.get("Data:", "Não Informada"))
        
        valores_canais = calcular_sistema_representacional(linha_cand)
        valores_animais = calcular_perfil_animais(linha_cand)
        
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
        
        # 🟢 SEÇÃO 1: TESTE DOS ANIMAIS
        st.markdown("### 🦁 Teste de Perfil Comportamental (Predominância)")
        col_animais1, col_animais2 = st.columns([1, 1.2])
        
        with col_animais1:
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
            fig_animais.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_animais, use_container_width=True)
            
        with col_animais2:
            st.markdown("#### 📊 Parecer Comportamental Avançado")
            
            perfis_ordenados = sorted(valores_animais.items(), key=lambda x: x[1], reverse=True)
            top1_nome, top1_valor = perfis_ordenados[0]
            top2_nome, top2_valor = perfis_ordenados[1]
            
            # Dicionário dinâmico de características por perfil
            detalhes_perfis = {
                "Tubarão": {
                    "fortes": "Foco em resultados, iniciativa, senso de urgência, coragem para decidir e alta resiliência sob pressão.",
                    "fracos": "Dificuldade em delegar, tendência ao autoritarismo, baixa paciência com processos lentos e inclinação a atropelar o planejamento.",
                    "estilo": "comercial, liderança, posições operacionais de ritmo acelerado ou áreas que demandem metas agressivas."
                },
                "Lobo": {
                    "fortes": "Organização cirúrgica, atenção extrema a detalhes, disciplina, lealdade a regras e alta previsibilidade na entrega.",
                    "fracos": "Resistência acentuada a mudanças repentinas, perfeccionismo que pode gerar lentidão e dificuldade de agir no improviso.",
                    "estilo": "controladoria, finanças, contabilidade, processos de qualidade, auditoria ou TI estruturada."
                },
                "Águia": {
                    "fortes": "Pensamento disruptivo, criatividade, facilidade de adaptação, olhar de longo prazo e entusiasmo para propor inovações.",
                    "fracos": "Falta de linearidade na execução, propensão a perder o foco antes de concluir tarefas repetitivas e indisciplina com prazos rígidos.",
                    "estilo": "marketing, desenvolvimento de produtos, estratégias corporativas ou cenários de transformação e inovação."
                },
                "Gato": {
                    "fortes": "Excelente comunicação interpessoal, mediação de conflitos, facilidade para trabalhar em equipe, empatia e construção de harmonia.",
                    "fracos": "Dificuldade para dar feedbacks duros, tendência a evitar confrontos necessários e vulnerabilidade a ambientes altamente agressivos.",
                    "estilo": "recursos humanos, atendimento ao cliente, sucesso do cliente (CS), recepção ou áreas de suporte focado em pessoas."
                }
            }
            
            # 🔍 MOTOR DE CÁLCULO DE MATCH COM A VAGA
            vaga_lower = str(vaga_alvo).lower()
            tipo_vaga = "Geral"
            
            # Categorização simplificada da vaga com base em palavras-chave comuns
            if any(k in vaga_lower for k in ["contab", "financ", "fiscal", "lobo", "adm", "process", "ti", "suport", "auditor", "qualidad"]):
                tipo_vaga = "Processos/Contábil/Analítico"
                perfis_ideais = ["Lobo", "Tubarão"]
            elif any(k in vaga_lower for k in ["vend", "comercial", "geren", "diretor", "lider", "meta", "tubarao", "expansao"]):
                tipo_vaga = "Comercial/Liderança/Execução"
                perfis_ideais = ["Tubarão", "Águia"]
            elif any(k in vaga_lower for k in ["rh", "human", "atend", "gato", "client", "relacionamento", "cs", "sucesso"]):
                tipo_vaga = "Pessoas/Atendimento/Suporte"
                perfis_ideais = ["Gato", "Águia"]
            else:
                tipo_vaga = "Estratégico/Geral"
                perfis_ideais = [top1_nome, top2_nome]
                
            # Verifica a convergência
            convergente = (top1_nome in perfis_ideais)
            
            # Montagem dinâmica do parecer estratégico
            st.markdown(f"**Distribuição de Perfis:** Predominância Primária de **{top1_nome}** ({top1_valor}%) com suporte Secundário de **{top2_nome}** ({top2_valor}%).")
            
            with st.expander("⭐ Pontos Fortes do Candidato", expanded=True):
                st.write(f"• **Fator {top1_nome}:** {detalhes_perfis[top1_nome]['fortes']}")
                if top2_valor > 15:
                    st.write(f"• **Fator {top2_nome}:** {detalhes_perfis[top2_nome]['fortes']}")
                    
            with st.expander("⚠️ Pontos de Atenção (Fraquezas)", expanded=True):
                st.write(f"• **Riscos de {top1_nome}:** {detalhes_perfis[top1_nome]['fracos']}")
                if top2_valor > 15:
                    st.write(f"• **Riscos de {top2_nome}:** {detalhes_perfis[top2_nome]['fracos']}")

        # 🎯 BLOCO DA CONCLUSÃO E RECOMENDAÇÃO FINAL
        st.markdown("#### 🎯 Alinhamento com a Função & Conclusão do Consultor")
        
        predominante_pnl = max(valores_canais, key=valores_canais.get)
        pnl_detalhes = {
            "Visual": "processa informações em alta velocidade, ideal para rotinas dinâmicas e de alta carga visual.",
            "Auditivo": "excelente para posições que exigem escuta ativa, diálogo e forte negociação verbal.",
            "Cinestésico": "melhor aproveitado em funções práticas, que envolvem contato, intuição e estabilidade.",
            "Digital (Lógico)": "altamente analítico, ideal para cenários que exigem validação de dados, fatos e lógica fria."
        }
        
        col_concl1, col_concl2 = st.columns([1.5, 1])
        with col_concl1:
            st.markdown(f"""
            **Análise de Engenharia de Cargo:** A vaga indicada (**{vaga_alvo}**) possui características de ambiente do tipo *{tipo_vaga}*. Para este cenário, os perfis comportamentais mais recomendados na Engenharia de Perfil são **{', '.join(perfis_ideais)}**.
            
            O candidato combina essa estrutura comportamental com um canal representacional predominantemente **{predominante_pnl}**, o que significa que ele {pnl_detalhes[predominante_pnl]}
            """)
            
        with col_concl2:
            if convergente:
                st.metric(label="RECOMENDAÇÃO FINAL", value="✅ CONTRATAR")
                st.caption("🏆 **Justificativa:** Alta aderência comportamental com o escopo da vaga e o estilo de raciocínio técnico exigido pela função.")
            else:
                if top2_nome in perfis_ideais:
                    st.metric(label="RECOMENDAÇÃO FINAL", value="🟡 CONTRATAR COM RESERVAS")
                    st.caption("👀 **Justificativa:** O perfil principal difere do esperado, mas o perfil secundário equilibra as competências técnicas. Recomendado focar a entrevista técnica nos pontos de atenção.")
                else:
                    st.metric(label="RECOMENDAÇÃO FINAL", value="❌ AVALIAR OUTROS PERFIS")
                    st.caption("🚨 **Justificativa:** Desalinhamento natural entre a energia comportamental predominante do candidato e as rotinas diárias da função.")
                    
        st.markdown("---")
        
        # 🔵 SEÇÃO 2: PNL
        col_pnl1, col_pnl2 = st.columns([1, 1.2])
        
        with col_pnl1:
            st.subheader("📊 Sistema Representacional (PNL)")
            
            df_chart = pd.DataFrame({
                "Canal": list(valores_canais.keys()), 
                "Percentagem (%)": list(valores_canais.values())
            })
            
            fig = px.bar(
                df_chart, 
                x="Canal", 
                y="Percentagem (%)", 
                color="Canal",
                text="Percentagem (%)", 
                template="streamlit",
                color_discrete_map=cores_canais
            )
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_pnl2:
            st.subheader("🧠 Canais de Captação & Abordagem")
            st.info("💡 **Dica de Entrevista:** Use a predominância de PNL para moldar as suas perguntas.")
            
            st.markdown(f"""
            Como o candidato possui o canal **{predominante_pnl}** mais elevado, a melhor tática para o consultor da Implantta durante a fase presencial é:
            * **Se for Visual:** Use termos como *"Veja bem"*, *"Imagine esse cenário"*. Mantenha contato visual fixo.
            * **Se for Auditivo:** Module bem o tom de voz, evite ruídos no ambiente. Use *"Ouça o raciocínio"*.
            * **Se for Cinestésico:** Crie um clima confortável, dê espaço para ele falar sobre sensações e experiências práticas.
            * **Se for Digital:** Apresente números, fatos incontestáveis, lógica estruturada e não tente apelar apenas para o lado emocional.
            """)
            
            st.markdown("---")
            with st.expander("🔍 Ver Respostas Brutas do Teste Comportamental (Texto)"):
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
        
        colunas_exibicao = []
        for col in ["Carimbo de data/hora", "Nome", "Empresa", "Setor"]:
            if col in df_dados.columns:
                colunas_exibicao.append(col)
                
        if colunas_exibicao:
            st.dataframe(df_dados[colunas_exibicao])
        else:
            st.dataframe(df_dados)
