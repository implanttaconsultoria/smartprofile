import pandas as pd
from fpdf import FPDF
import unicodedata
import os

# =====================================================================
# 🛡️ 1. FUNÇÕES DE LIMPEZA, FORMATAÇÃO E GÊNERO
# =====================================================================
def normalizar_busca(texto):
    if pd.isna(texto): return ""
    texto = str(texto).lower().strip()
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

def text_pdf(texto):
    if not isinstance(texto, str): return ""
    reps = {'✔': '[+]', '⚠': '[!]', '–': '-', '—': '-', '“': '"', '”': '"', '\u200b': '', '\ufeff': '', '\xa0': ' '}
    for c, r in reps.items(): texto = texto.replace(c, r)
    return texto.encode('latin-1', 'ignore').decode('latin-1')

def formatar_nome_proprio(texto):
    if pd.isna(texto): return ""
    excecoes = ['de', 'da', 'do', 'das', 'dos', 'e']
    palavras = str(texto).strip().lower().split()
    return " ".join([p.capitalize() if p not in excecoes else p for p in palavras])

def definir_genero(nome):
    primeiro_nome = normalizar_busca(nome.split()[0])
    masculinos_a = ['luca', 'noa', 'noah', 'joshua', 'jonatas', 'messias', 'ozias', 'matias', 'zacarias', 'andrea', 'batista']
    femininos_excecoes = ['miriam', 'raquel', 'ester', 'ruth', 'elisabeth', 'carmen', 'iris', 'lais', 'beatriz', 'tais', 'thais', 'aline', 'simone', 'eliane', 'viviane', 'lilian', 'suelen', 'karen', 'ingrid', 'ellen', 'helen', 'cleide', 'meire', 'irene', 'shirley', 'rose', 'ariadne', 'thaina']
    
    if primeiro_nome in masculinos_a: return "M"
    if primeiro_nome in femininos_excecoes or primeiro_nome.endswith('a') or primeiro_nome.endswith('y') or primeiro_nome.endswith('ie') or primeiro_nome.endswith('elly'): return "F"
    return "M"

def obter_artigos(nome):
    if definir_genero(nome) == "F": return {"o_min": "a", "O_mai": "A", "candidato": "candidata", "integrado": "integrada", "o_colaborador": "a colaboradora"}
    else: return {"o_min": "o", "O_mai": "O", "candidato": "candidato", "integrado": "integrado", "o_colaborador": "o colaborador"}

# =====================================================================
# 🧮 2. LÓGICA DE CÁLCULO
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
    
    v = v if pd.notna(v) else 0; a = a if pd.notna(a) else 0
    c = c if pd.notna(c) else 0; d = d if pd.notna(d) else 0
    total = v + a + c + d
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

# =====================================================================
# 📄 3. CLASSE GERADORA DO PDF
# =====================================================================
class PDF(FPDF):
    def header(self):
        try:
            if os.path.exists('logo.png'): self.image('logo.png', x=10, y=8, h=18)
            elif os.path.exists('logo.jpg'): self.image('logo.jpg', x=10, y=8, h=18)
        except Exception:
            pass 
            
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(43, 92, 143)
        self.cell(0, 10, text_pdf('IMPLANTTA CONSULTORIA'), ln=True, align='C')
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, text_pdf('PARECER DE ENGENHARIA DE PERFIL'), ln=True, align='C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def titulo_secao(self, title):
        if self.get_y() > 250: self.add_page()
        else: self.ln(3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(43, 92, 143)
        self.cell(0, 8, text_pdf(title), ln=True)
        self.set_text_color(0, 0, 0)

    def texto_normal(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text_pdf(text))
        self.ln(2)

    def texto_destaque(self, text):
        self.set_font('Helvetica', 'B', 10)
        self.multi_cell(0, 6, text_pdf(text))
        self.ln(2)

# =====================================================================
# 🧠 4. DICIONÁRIOS DE INTELIGÊNCIA DE TEXTO E VAGAS
# =====================================================================
def categorizar_vaga(vaga):
    v_low = normalizar_busca(vaga)
    cat1_keys = ["contab", "financ", "fiscal", "lobo", "adm", "process", "ti", "suport", "auditor", "qualidad", "estoque", "logistic", "motorist", "operacion", "faturament", "caixa"]
    cat2_keys = ["vend", "comercial", "geren", "diretor", "lider", "meta", "tubarao", "expansao", "negocio", "executiv", "corretor"]
    cat3_keys = ["rh", "human", "atend", "gato", "client", "relacionamento", "cs", "sucesso", "pessoal", "dp", "psico", "recep", "secret"]
    
    if any(k in v_low for k in cat1_keys):
        return {
            "atividades": "atividades que exigem alto nível de foco, precisão, organização metódica, análise de dados e cumprimento rigoroso de regras ou rotinas",
            "ideais": ["Lobo", "Tubarão"]
        }
    elif any(k in v_low for k in cat2_keys):
        return {
            "atividades": "atividades focadas em alcance de metas, tomada de decisão rápida, negociação, persuasão e resolução de problemas sob pressão",
            "ideais": ["Tubarão", "Águia"]
        }
    elif any(k in v_low for k in cat3_keys):
        return {
            "atividades": "atividades que envolvem forte interação humana, escuta ativa, mediação de conflitos, acolhimento e gestão de processos com pessoas",
            "ideais": ["Gato", "Águia", "Lobo"]
        }
    else:
        return {
            "atividades": "atividades multifuncionais que exigem flexibilidade, adaptação a diferentes cenários e equilíbrio entre execução metódica e relacionamento interpessoal",
            "ideais": ["Lobo", "Tubarão", "Águia", "Gato"]
        }

def texto_animal(animal, perc):
    if animal == "Gato":
        if perc >= 25: return "Indica uma pessoa colaborativa, empática e prestativa. Facilidade para trabalhar em equipe, cordialidade e disposição para manter um ambiente harmonioso."
        else: return "Menor foco no relacionamento interpessoal constante. Pode apresentar um perfil mais voltado para a tarefa do que para o acolhimento da equipe."
    elif animal == "Lobo":
        if perc >= 25: return "Demonstra excelente atenção aos detalhes, respeito a regras e procedimentos. Boa capacidade de organização e constância com rotinas."
        else: return "Perfil mais flexível, com menor apego a regras rígidas. Pode preferir ambientes onde haja menos microgestão e maior liberdade operacional."
    elif animal == "Tubarão":
        if perc >= 25: return "Revela forte senso de urgência, foco absoluto em resultados, coragem para decidir e assertividade na execução de tarefas."
        else: return "Percentual moderado-baixo indicando menor tendência a confrontos. Perfil mais cuidadoso que pode precisar de tempo para agir em situações de alta pressão."
    elif animal == "Águia":
        if perc >= 25: return "Sugere grande capacidade criativa, visão de futuro, facilidade em inovar e propor melhorias para processos engessados."
        else: return "Preferência por processos definidos e estruturados. Mostra menor foco na inovação disruptiva e maior conforto no que já está validado."

def obter_fortes_dinamicos(t1, t2, vaga, atividades):
    forcas = {
        "Tubarão": "agilidade, senso de urgência, foco em entregar resultados práticos e capacidade de lidar com momentos de pressão",
        "Lobo": "organização minuciosa, foco na qualidade das entregas, atenção aos detalhes e cumprimento rigoroso de processos",
        "Águia": "visão ampla, rápida adaptação a imprevistos da função e criatividade para encontrar soluções eficazes",
        "Gato": "excelente relacionamento interpessoal, comunicação empática e forte espírito de cooperação"
    }
    return f"Considerando as {atividades}, a predominância do perfil {t1} traz {forcas[t1]}. Complementarmente, os traços de {t2} reforçam a atuação do perfil {t1} com {forcas[t2]} no dia a dia."

def obter_fracos_dinamicos(t1):
    fracos = {
        "Tubarão": "Pode demonstrar impaciência em processos que sejam muito lentos, tarefas monótonas ou situações que exijam excessiva cautela e longas análises de detalhes.",
        "Lobo": "Pode apresentar alguma resistência a mudanças de última hora, improvisos constantes ou ambientes com pouca estruturação e falta de regras claras.",
        "Águia": "Pode ter dificuldade em manter o engajamento e o foco contínuo em rotinas estritamente repetitivas, burocráticas ou excessivamente engessadas.",
        "Gato": "Pode evitar situações de conflito, tendo maior dificuldade em aplicar cobranças firmes ou tomar decisões impessoais sob forte pressão."
    }
    return fracos[t1]

def texto_atencao_gestao(animal, gen):
    if animal == "Tubarão": return f"Recomenda-se uma liderança baseada em metas claras e autonomia, evitando a microgestão. O gestor deve monitorar possíveis atritos com a equipe devido ao forte senso de urgência d{gen['o_min']} {gen['candidato']}, garantindo um ambiente de respeito mútuo e direcionando essa energia para resultados táticos."
    elif animal == "Lobo": return f"A gestão precisa fornecer um ambiente estruturado e com regras bem definidas. Mudanças repentinas de escopo podem gerar desconforto. O líder ideal deve comunicar alterações com antecedência, valorizar a organização e oferecer orientações lógicas e detalhadas para {gen['o_colaborador']}."
    elif animal == "Águia": return f"A gestão deve evitar rotinas excessivamente burocráticas ou repetitivas, que podem causar desmotivação. É recomendável oferecer espaço para ideias e inovações. O líder deve atuar como um facilitador, guiando o foco d{gen['o_min']} {gen['candidato']} para garantir que a sua criatividade não comprometa os prazos estipulados."
    else: return f"A gestão deve priorizar feedbacks humanizados e um clima organizacional harmonioso. {gen['O_mai']} {gen['candidato']} renderá melhor sob uma liderança acolhedora. O líder deve ficar atento para que o foco natural d{gen['o_min']} {gen['candidato']} em relacionamentos e colaboração não ofusque a entrega objetiva das tarefas operacionais."

# =====================================================================
# ⚙️ 5. FUNÇÃO PRINCIPAL
# =====================================================================
def gerar_pdf(nome_busca):
    url_csv = "https://docs.google.com/spreadsheets/d/1cz6O2iSync1c2E-lNGmEsgwMBrOgB2DHWz02A-y2g1Y/export?format=csv"
    try: 
        df = pd.read_csv(url_csv)
    except Exception as e: 
        return f"Erro ao ler a planilha: {e}"
    
    cabecalhos = [str(c).lower().strip() for c in df.columns]
    if not any("nome" in c for c in cabecalhos):
        for i, row in df.iterrows():
            vals = [str(val).lower().strip() for val in row.values]
            if "nome" in vals or "nome do candidato" in vals:
                df.columns = row.values
                df = df.iloc[i+1:].reset_index(drop=True)
                break
                
    col_nome = next((c for c in df.columns if "nome" in str(c).lower()), None)
    if not col_nome: return "Erro: Coluna 'Nome' não encontrada."

    df = df.dropna(subset=[col_nome])
    busca_limpa = normalizar_busca(nome_busca)
    nomes_plan = df[col_nome].apply(normalizar_busca)
    df_cand = df[nomes_plan.str.contains(busca_limpa, na=False)]
    
    if df_cand.empty: return f"Candidato '{nome_busca}' não encontrado."
    linha = df_cand.iloc[-1]
    
    # 🧠 Aqui entra a nova formatação impecável:
    nome_real = formatar_nome_proprio(linha[col_nome])
    vaga = formatar_nome_proprio(linha.get("Setor", "Não Informado"))
    empresa = formatar_nome_proprio(linha.get("Empresa", "Não Informada"))
    data_app = str(linha.get("Carimbo de data/hora", "Não Informada"))
    
    gen = obter_artigos(nome_real)
    animais = calcular_perfil_animais(linha)
    pnl = calcular_sistema_representacional(linha)
    
    animais_ord = sorted(animais.items(), key=lambda x: x[1], reverse=True)
    pnl_ord = sorted(pnl.items(), key=lambda x: x[1], reverse=True)
    
    t1_n, t1_v = animais_ord[0]
    t2_n, t2_v = animais_ord[1]
    pnl_top_n, pnl_top_v = pnl_ord[0]
    
    cat_info = categorizar_vaga(vaga)
    perfis_ideais = cat_info["ideais"]
    atividades_desc = cat_info["atividades"]

    if t1_n in perfis_ideais:
        veredicto = "CONTRATAR"
        just_veredicto = f"{gen['O_mai']} {gen['candidato']} apresenta excelente aderência, pois o perfil predominante ({t1_n}) está diretamente alinhado às exigências necessárias para as {atividades_desc}."
    elif t2_n in perfis_ideais:
        veredicto = "CONTRATAR COM RESSALVAS"
        just_veredicto = f"O perfil principal ({t1_n}) apresenta contrastes com o padrão idealmente esperado para o cargo/setor avaliado ({vaga}), mas o perfil secundário ({t2_n}) oferece o equilíbrio mínimo necessário para as {atividades_desc}. Exigirá acompanhamento do gestor."
    else:
        veredicto = "NÃO CONTRATAR"
        just_veredicto = f"O perfil natural d{gen['o_min']} {gen['candidato']} ({t1_n} primário e {t2_n} secundário) demonstra forte desalinhamento com as exigências comportamentais para as {atividades_desc}."

    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 5, text_pdf(f"Candidat{gen['o_min']}: {nome_real}"), ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, text_pdf(f"Cargo/Setor Avaliado: {vaga}"), ln=True)
    pdf.cell(0, 5, text_pdf(f"Empresa: {empresa}"), ln=True)
    pdf.cell(0, 5, text_pdf(f"Data e hora do preenchimento: {data_app}"), ln=True)
    pdf.ln(5)

    intro = (f"{gen['O_mai']} {gen['candidato']} {nome_real} apresentou o seguinte resultado no teste de perfil comportamental: "
             f"{animais['Tubarão']}% Tubarão, {animais['Lobo']}% Lobo, {animais['Águia']}% Águia e {animais['Gato']}% Gato.\n\n"
             f"O perfil {t1_n} teve {t1_v}% de aderência (predominante), seguido do perfil {t2_n} com {t2_v}% de aderência.")
    pdf.texto_normal(intro)

    pdf.titulo_secao("Análise do Perfil Comportamental")
    for animal in ["Tubarão", "Lobo", "Gato", "Águia"]:
        texto_dinamico = texto_animal(animal, animais[animal])
        pdf.texto_normal(f"- {animal} ({animais[animal]}%): {texto_dinamico}")

    pdf.titulo_secao("Pontos Fortes e Fracos em relação à vaga")
    pdf.texto_normal(f"Considerando as exigências do cargo/setor avaliado ({vaga}):\n")
    
    texto_fortes = obter_fortes_dinamicos(t1_n, t2_n, vaga, atividades_desc)
    texto_fracos = obter_fracos_dinamicos(t1_n)
    
    pdf.texto_normal(f"[+] Pontos Fortes: {texto_fortes}")
    pdf.texto_normal(f"[!] Pontos de Desenvolvimento: {texto_fracos}")

    pdf.titulo_secao("Análise do Perfil Representacional")
    pdf.texto_normal(f"Resultados obtidos: {pnl['Visual']}% Visual, {pnl['Cinestésico']}% Cinestésico, {pnl['Auditivo']}% Auditivo e {pnl['Digital']}% Digital.")
    
    txt_pnl = f"Predominância do perfil {pnl_top_n} ({pnl_top_v}%). "
    if pnl_top_n == "Digital": txt_pnl += "Indica forte tendência a processar informações de forma lógica, analisar procedimentos com racionalidade e valorizar precisão. A melhor abordagem é fornecer instruções claras e baseadas em fatos."
    elif pnl_top_n == "Cinestésico": txt_pnl += "Indica facilidade com atividades práticas e aprendizagem por execução. A melhor abordagem é o treino on-the-job, valorizando o lado humano e o acolhimento."
    elif pnl_top_n == "Visual": txt_pnl += "Indica rapidez mental e aprendizagem por observação e mapas visuais. A melhor abordagem é manter contato visual, usar esquemas e mostrar o 'cenário geral'."
    else: txt_pnl += "Indica forte capacidade de escuta e comunicação verbal. A melhor abordagem é o diálogo claro, feedbacks conversados e evitar dar ordens em locais muito ruidosos."
    pdf.texto_normal(txt_pnl)

    pdf.titulo_secao("Adequação ao Cargo")
    pdf.texto_normal(just_veredicto)

    pdf.titulo_secao("Pontos de Atenção para a Gestão")
    txt_gestao = f"Caso {gen['o_min']} {gen['candidato']} seja {gen['integrado']}, o gestor direto deve ter em atenção que {gen['o_colaborador']}, por ter traços fortes de {t1_n}, necessitará de uma abordagem alinhada ao seu perfil natural.\n\n" + texto_atencao_gestao(t1_n, gen)
    pdf.texto_normal(txt_gestao)

    pdf.titulo_secao("Conclusão do Parecer")
    pdf.texto_destaque(f"Recomendação Final: {veredicto}")

    nome_ficheiro = f"Parecer_{normalizar_busca(nome_real).replace(' ', '_')}.pdf"
    pdf.output(nome_ficheiro)
    return nome_ficheiro

if __name__ == "__main__":
    print(gerar_pdf("Aparecida Oliveira do Amaral"))
