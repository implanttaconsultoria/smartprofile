import pandas as pd
from fpdf import FPDF
import unicodedata
import os

# =====================================================================
# 🛡️ FUNÇÕES DE LIMPEZA (BLINDAGEM COM SUPORTE A ACENTOS)
# =====================================================================
def normalizar_busca(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

def text_pdf(texto):
    if not isinstance(texto, str):
        return ""
    # 1. Substitui símbolos problemáticos e remove espaços invisíveis
    reps = {
        '✔': '[+]', '⚠': '[!]', '–': '-', '—': '-', 
        '“': '"', '”': '"', '\u200b': '', '\ufeff': '', '\xa0': ' '
    }
    for c, r in reps.items():
        texto = texto.replace(c, r)
    
    # 2. A MAGIA: Mantém os acentos (latin-1) e ignora apenas o que a fonte não suporta (emojis)
    return texto.encode('latin-1', 'ignore').decode('latin-1')

# =====================================================================
# 🧮 LÓGICA DE CÁLCULO
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
    
    v = v if pd.notna(v) else 0
    a = a if pd.notna(a) else 0
    c = c if pd.notna(c) else 0
    d = d if pd.notna(d) else 0
    
    total = v + a + c + d
    if total > 0:
        return {"Visual": round((v/total)*100, 1), "Auditivo": round((a/total)*100, 1), 
                "Cinestésico": round((c/total)*100, 1), "Digital": round((d/total)*100, 1)}
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
    if total > 0:
        return {a: round((v/total)*100, 1) for a, v in pontos.items()}
    return {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}

# =====================================================================
# 📄 CLASSE GERADORA DO PDF
# =====================================================================
class PDF(FPDF):
    def header(self):
        # Limita a altura (h=18) para a logomarca não cortar a linha dos 30mm
        try:
            if os.path.exists('logo.png'):
                self.image('logo.png', x=10, y=8, h=18)
            elif os.path.exists('logo.jpg'):
                self.image('logo.jpg', x=10, y=8, h=18)
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
        # Lógica de Paginação (Evita que o título fique isolado no final da página)
        if self.get_y() > 250:  
            self.add_page()
        else:
            self.ln(3)
            
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
# 🧠 DICIONÁRIOS DE INTELIGÊNCIA DE TEXTO
# =====================================================================
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

# =====================================================================
# ⚙️ FUNÇÃO PRINCIPAL
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
    if not col_nome: 
        return "Erro: Coluna 'Nome' não encontrada."

    df = df.dropna(subset=[col_nome])
    busca_limpa = normalizar_busca(nome_busca)
    nomes_plan = df[col_nome].apply(normalizar_busca)
    df_cand = df[nomes_plan.str.contains(busca_limpa, na=False)]
    
    if df_cand.empty: 
        return f"Candidato '{nome_busca}' não encontrado."
    linha = df_cand.iloc[-1]
    
    nome_real = str(linha[col_nome]).strip().title()
    vaga = str(linha.get("Setor", "Não Informado")).title()
    empresa = str(linha.get("Empresa", "Não Informada")).title()
    data_app = str(linha.get("Carimbo de data/hora", "Não Informada"))
    
    animais = calcular_perfil_animais(linha)
    pnl = calcular_sistema_representacional(linha)
    
    animais_ord = sorted(animais.items(), key=lambda x: x[1], reverse=True)
    pnl_ord = sorted(pnl.items(), key=lambda x: x[1], reverse=True)
    
    t1_n, t1_v = animais_ord[0]
    t2_n, t2_v = animais_ord[1]
    pnl_top_n, pnl_top_v = pnl_ord[0]
    
    v_low = vaga.lower()
    if any(k in v_low for k in ["contab", "financ", "fiscal", "lobo", "adm", "process", "ti", "suport", "auditor", "qualidad", "estoque", "logistica"]):
        tipo = "Processos/Operacional/Analítico"
        fortes = "Organização, conformidade com processos, foco em detalhes e execução consistente."
        fracos = "Pode evitar improvisos rápidos ou situações de conflito intenso."
        se_encaixa = (t1_n in ["Lobo", "Tubarão", "Gato"]) 
    elif any(k in v_low for k in ["vend", "comercial", "geren", "diretor", "lider", "meta", "tubarao", "expansao", "negocio"]):
        tipo = "Comercial/Liderança/Resultados"
        fortes = "Foco em metas, persuasão, resiliência sob pressão e relacionamento."
        fracos = "Pode apresentar dificuldades com rotinas altamente burocráticas ou rotineiras."
        se_encaixa = (t1_n in ["Tubarão", "Águia", "Gato"])
    elif any(k in v_low for k in ["rh", "human", "atend", "gato", "client", "relacionamento", "cs", "sucesso", "pessoal", "dp", "psico", "recep"]):
        tipo = "Pessoas/Atendimento/Suporte"
        fortes = "Escuta ativa, empatia, mediação de conflitos e forte trabalho em equipe."
        fracos = "Dificuldade em tomar decisões frias que prejudiquem o clima da equipe."
        se_encaixa = (t1_n in ["Gato", "Águia", "Lobo"])
    else:
        tipo = "Função Dinâmica / Geral"
        fortes = "Forças dependem diretamente do escopo diário e do perfil da chefia."
        fracos = "Requer alinhamento claro de expectativas no momento da integração."
        se_encaixa = True

    if se_encaixa:
        veredicto = "CONTRATAR"
        just_veredicto = f"O candidato apresenta excelente aderência à função, com destaque para características de {t1_n} e {t2_n}, que favorecem o desempenho em vagas de {tipo}."
    elif t2_n in ["Tubarão", "Lobo", "Gato", "Águia"]: 
        veredicto = "CONTRATAR COM RESSALVAS"
        just_veredicto = f"O perfil principal ({t1_n}) difere um pouco do esperado para {tipo}, mas o secundário ({t2_n}) equilibra. Exigirá acompanhamento nos primeiros meses."
    else:
        veredicto = "NÃO CONTRATAR"
        just_veredicto = "O perfil natural do candidato demonstra desalinhamento com as exigências rotineiras e comportamentais desta vaga específica."

    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 5, text_pdf(f"Candidato: {nome_real}"), ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, text_pdf(f"Cargo Avaliado: {vaga}"), ln=True)
    pdf.cell(0, 5, text_pdf(f"Empresa: {empresa}"), ln=True)
    pdf.cell(0, 5, text_pdf(f"Data e hora do preenchimento: {data_app}"), ln=True)
    pdf.ln(5)

    intro = (f"O candidato {nome_real} apresentou o seguinte resultado no teste de perfil comportamental: "
             f"{animais['Tubarão']}% Tubarão, {animais['Lobo']}% Lobo, {animais['Águia']}% Águia e {animais['Gato']}% Gato.\n\n"
             f"O perfil {t1_n} teve {t1_v}% de aderência (predominante), seguido do perfil {t2_n} com {t2_v}% de aderência.")
    pdf.texto_normal(intro)

    pdf.titulo_secao("Análise do Perfil Comportamental")
    for animal in ["Tubarão", "Lobo", "Gato", "Águia"]:
        texto_dinamico = texto_animal(animal, animais[animal])
        pdf.texto_normal(f"- {animal} ({animais[animal]}%): {texto_dinamico}")

    pdf.titulo_secao("Pontos Fortes e Fracos do candidato em relação à vaga")
    pdf.texto_normal(f"Considerando as exigências para o setor de {vaga} ({tipo}):\n")
    pdf.texto_normal(f"[+] Pontos Fortes: {fortes}")
    pdf.texto_normal(f"[!] Pontos Fracos/Desenvolver: {fracos}")

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
    pdf.texto_normal(f"Caso o candidato seja integrado, o gestor direto deve ter em atenção que o colaborador, por ter traços fortes de {t1_n}, responderá melhor a um modelo de liderança que respeite a sua natureza. Deverá ser feito um alinhamento claro das expectativas nas primeiras semanas, focando nos pontos fracos descritos acima para mitigar quebras de produtividade.")

    pdf.titulo_secao("Conclusão do Parecer")
    pdf.texto_destaque(f"Recomendação Final: {veredicto}")

    nome_ficheiro = f"Parecer_{normalizar_busca(nome_real).replace(' ', '_')}.pdf"
    pdf.output(nome_ficheiro)
    return nome_ficheiro
if __name__ == "__main__":
    print(gerar_pdf("José Pedro"))
