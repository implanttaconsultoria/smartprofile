import telebot
import os
from gerador_pdf import gerar_pdf  # Importa o nosso motor de PDFs!

# 🚨 COLOQUE A CHAVE DO BOTFATHER ENTRE AS ASPAS ABAIXO 🚨
CHAVE_API = "8817892481:AAGBU6PjMleZFskqExoXvrMhAR075usLJ50"

bot = telebot.TeleBot(CHAVE_API)

@bot.message_handler(func=lambda message: True)
def responder_mensagem(mensagem):
    nome_candidato = mensagem.text.strip()
    
    # 1. O Robô avisa que recebeu a mensagem
    bot.reply_to(mensagem, f"🔍 Olá! Estou a analisar a planilha à procura de '{nome_candidato}'... Aguarde um momento!")
    
    try:
        # 2. O Robô pede ao gerador_pdf.py para criar o documento
        resultado = gerar_pdf(nome_candidato)
        
        # 3. Se o ficheiro for criado com sucesso (termina em .pdf)
        if resultado.endswith(".pdf"):
            with open(resultado, "rb") as arquivo_pdf:
                # O Robô envia o PDF de volta para si!
                bot.send_document(mensagem.chat.id, arquivo_pdf, caption=f"📄 Relatório Executivo de {nome_candidato} gerado com sucesso!")
            
            # Apaga o ficheiro do servidor após o envio para não ocupar espaço
            os.remove(resultado)
        else:
            # Se não encontrou o candidato, o gerador devolve um texto de erro
            bot.reply_to(mensagem, f"⚠️ {resultado}")
            
    except Exception as e:
        bot.reply_to(mensagem, f"❌ Ocorreu um erro no sistema: {e}")

print("🤖 Assistente Implantta está online no Telegram e a aguardar mensagens!")
bot.polling()
