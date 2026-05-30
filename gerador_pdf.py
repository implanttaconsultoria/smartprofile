import pandas as pd
from fpdf import FPDF
import os

# =====================================================================
# 🧮 1. LÓGICA DE CÁLCULO (A mesma inteligência do sistema principal)
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
    "Tempo para mim é...": {"Algo que detesto desperdiçar": "Tubarão", "Um grande ciclo que termina e vem outro": "Gato", "Uma flecha que leva ao inevitável": "Lobo", "Irrelevante": "Águia"},
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
    if total_respondido > 0:
        return {animal: round((valor / total_respondido) * 100, 1) for animal, valor in pontos.items()}
    return {"Águia": 0, "Gato": 0, "Lobo": 0, "Tubarão": 0}

# =====================================================================
# 📄 2. CLASSE GERADORA DO PDF (Design Executivo)
# =====================================================================
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(43, 92, 143) # Azul Implantta
        self.cell(0, 10, 'IMPLANTTA CONSULTORIA', ln=True, align='C')
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'RELATÓRIO DE ENGENHARIA DE PERFIL - SÍNTESE EXECUTIVA', ln=True, align='C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(43, 92, 143)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(5)

# =====================================================================
# ⚙️ 3. FUNÇÃO PRINCIPAL (Cria o PDF para um candidato específico)
# =====================================================================
def gerar_pdf(nome_busca):
    print(f"A procurar candidato: {nome_busca}...")
    
    # URL de Exportação Direta da Planilha Google
    url_csv = "https://docs.google.com/spreadsheets/d/1cz6O2iSync1c2E-lNGmEsgwMBrOgB2DHWz02A-y2g1Y/export?format=csv"
    
    try:
        df = pd.read_csv(url_csv)
    except Exception as e:
        return f"Erro ao ler a planilha: {e}"
    
    # Limpeza de colunas
    coluna_nome = None
    for col in df.columns:
        if "nome" in str(col).lower():
            coluna_nome = col
            break
            
    if not coluna_nome:
        return "Erro: Coluna de Nome não encontrada."

    # Procurar o candidato (ignorando maiúsculas/minúsculas)
    df_cand = df[df[coluna_nome].astype(str).str.lower().str.contains(nome_busca.lower())]
    
    if df_cand.empty:
        return f"Candidato '{nome_busca}' não encontrado na planilha."
    
    linha_cand = df_cand.iloc[-1] # Pega a resposta mais recente caso haja duplicados
    
    nome_real = linha_cand[coluna_nome]
    vaga_alvo = linha_cand.get("Setor", "Não Informado")
    empresa_alvo = linha_cand.get("Empresa", "Não Informada")
    data_teste = linha_cand.get("Carimbo de data/hora", "Não Informada")
    
    # Fazer os cálculos
    valores_animais = calcular_perfil_animais(linha_cand)
    valores_canais = calcular_sistema_representacional(linha_cand)
    
    perfis_ordenados = sorted(valores_animais.items(), key=lambda x: x[1], reverse=True)
    top1_nome, top1_valor = perfis_ordenados[0]
    top2_nome, top2_valor = perfis_ordenados[1]
    
    predominante_pnl = max(valores_canais, key=valores_canais.get)
    
    # Lógica da Vaga
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
    
    # =====================================================================
    # 🎨 MONTAR O ARQUIVO PDF
    # =====================================================================
    pdf = PDF()
    pdf.add_page()
    
    # Cabeçalho de Dados
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, f"Candidato: {nome_real}", ln=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, f"Vaga/Função: {vaga_alvo} | Empresa: {empresa_alvo}", ln=True)
    pdf.cell(0, 6, f"Data da Aplicação: {data_teste}", ln=True)
    pdf.ln(5)
    
    # Secção 1: Animais
    pdf.chapter_title("1. PERFIL COMPORTAMENTAL PREDOMINANTE")
    texto_animais = (
        f"Perfil Primário: {top1_nome} ({top1_valor}%)\n"
        f"Perfil Secundário: {top2_nome} ({top2_valor}%)\n\n"
        f"Parecer Analítico:\nDistribuição com predominância de {top1_nome}, com suporte de {top2_nome}."
    )
    pdf.chapter_body(texto_animais)
    
    # Secção 2: Alinhamento
    pdf.chapter_title("2. ALINHAMENTO COM A FUNÇÃO (VAGA)")
    if is_general:
        veredicto = "AVALIACAO DO GESTOR"
        justificativa = "O título da vaga não tem um perfil engessado. Avalie se as forças do candidato atendem à rotina."
    elif convergente:
        veredicto = "CONTRATAR"
        justificativa = "Alta aderência comportamental com o escopo da vaga."
    elif top2_nome in perfis_ideais:
        veredicto = "AVALIAR COM RESSALVAS"
        justificativa = "O perfil principal difere do esperado, mas o secundário equilibra."
    else:
        veredicto = "DESALINHADO A VAGA"
        justificativa = "Desalinhamento natural com as rotinas diárias da função."
        
    texto_vaga = (
        f"Engenharia do Cargo: {tipo_vaga}\n"
        f"Perfis Ideais: {', '.join(perfis_ideais)}\n\n"
        f"VEREDICTO: {veredicto}\n"
        f"Justificativa: {justificativa}"
    )
    pdf.chapter_body(texto_vaga)
    
    # Secção 3: PNL
    pdf.chapter_title("3. SISTEMA REPRESENTACIONAL (PNL)")
    texto_pnl = ""
    for canal, valor in valores_canais.items():
        marcador = " (Predominante)" if canal == predominante_pnl else ""
        texto_pnl += f"- {canal}: {valor}% {marcador}\n"
        
    texto_pnl += f"\nManual de Relacionamento:\nO candidato possui o canal {predominante_pnl} mais elevado. Adapte a comunicação para este canal para maior eficácia na liderança diária."
    
    pdf.chapter_body(texto_pnl)
    
    # Salvar Ficheiro
    nome_ficheiro = f"Parecer_{nome_real.replace(' ', '_')}.pdf"
    pdf.output(nome_ficheiro)
    return nome_ficheiro

# =====================================================================
# TESTE RÁPIDO DO SCRIPT
# =====================================================================
if __name__ == "__main__":
    # Aqui você digita o nome para testar se o script está a gerar o PDF
    arquivo_gerado = gerar_pdf("José Pedro")
    print(f"Sucesso! PDF salvo como: {arquivo_gerado}")
