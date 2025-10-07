#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fixed script to properly fill Portuguese translations in .po file
This handles multiline strings and proper .po file format
"""

import re

PT_TRANSLATIONS = {
    "Free JPG to PDF Converter | Convert Images to PDF Instantly": "Conversor Gratuito de JPG para PDF | Converta Imagens para PDF Instantaneamente",
    "Free JPG to PDF Converter | Professional Image to PDF Tool": "Conversor Gratuito de JPG para PDF | Ferramenta Profissional",
    "Transform JPG, PNG, and other images into professional PDF documents instantly. Free online converter with no registration, unlimited conversions, and perfect quality preservation.": "Transforme JPG, PNG e outras imagens em documentos PDF profissionais instantaneamente. Conversor online gratuito sem registro, conversões ilimitadas e preservação de qualidade perfeita.",
    "Home": "Início",
    "Features": "Recursos",
    "FAQ": "Perguntas Frequentes",
    "Contact": "Contato",
    "About jpg2pdf.link": "Sobre jpg2pdf.link",
    "Professional image to PDF conversion tool. Free, fast, and secure.": "Ferramenta profissional de conversão de imagem para PDF. Gratuita, rápida e segura.",
    "Quick Links": "Links Rápidos",
    "JPG to PDF Converter": "Conversor de JPG para PDF",
    "Privacy Policy": "Política de Privacidade",
    "Terms of Service": "Termos de Serviço",
    "All rights reserved": "Todos os direitos reservados",
    "Free JPG to PDF Converter - Convert Images Online": "Conversor Gratuito de JPG para PDF - Converta Imagens Online",
    "Turn your JPG and PNG images into PDF files. Free tool, no signup needed. Works on phone and computer.": "Transforme suas imagens JPG e PNG em arquivos PDF. Ferramenta gratuita, sem necessidade de cadastro. Funciona em telefone e computador.",
    "Turn JPG Images into PDF Files": "Transforme Imagens JPG em Arquivos PDF",
    "Free converter that works in your browser. No signup, no software to install.": "Conversor gratuito que funciona no seu navegador. Sem cadastro, sem software para instalar.",
    "Drop your images here": "Solte suas imagens aqui",
    "or click to browse files": "ou clique para procurar arquivos",
    "Select Images": "Selecionar Imagens",
    "Private": "Privado",
    "Files deleted after 24 hours": "Arquivos excluídos após 24 horas",
    "files": "arquivos",
    "Add more": "Adicionar mais",
    "Clear": "Limpar",
    "Convert to PDF": "Converter para PDF",
    "Converting...": "Convertendo...",
    "Why I Built This": "Por Que Criei Isso",
    "I got tired of downloading random software just to convert a couple photos to PDF. You know the routine - you need to submit something for work or school, and suddenly you're installing programs that want permissions for everything on your computer.": "Cansei de baixar softwares aleatórios apenas para converter algumas fotos em PDF. Você conhece a rotina - precisa enviar algo para o trabalho ou escola, e de repente está instalando programas que querem permissões para tudo no seu computador.",
    "This tool does one thing: takes your images and puts them in a PDF. No account signup, no email collection, no upsells for premium features. I make enough from a few ads to keep the servers running.": "Esta ferramenta faz uma coisa: pega suas imagens e as coloca em um PDF. Sem cadastro de conta, sem coleta de e-mail, sem vendas de recursos premium. Ganho o suficiente com alguns anúncios para manter os servidores funcionando.",
    "It's Actually Fast": "É Realmente Rápido",
    "Most converters are slow because they're handling hundreds of people on cheap servers. I've waited 10 minutes before for a simple conversion - that's ridiculous. This usually takes under 5 seconds. If it's slower, something's probably wrong.": "A maioria dos conversores é lenta porque está lidando com centenas de pessoas em servidores baratos. Já esperei 10 minutos antes por uma conversão simples - isso é ridículo. Isso geralmente leva menos de 5 segundos. Se for mais lento, provavelmente há algo errado.",
    "Your Images Won't Look Worse": "Suas Imagens Não Ficarão Piores",
    "Some sites compress your images to save money on storage. You upload a clear photo and get back a blurry mess. I don't do that. Your image goes in, gets wrapped in PDF format, comes out looking identical.": "Alguns sites comprimem suas imagens para economizar dinheiro em armazenamento. Você envia uma foto clara e recebe de volta uma bagunça borrada. Eu não faço isso. Sua imagem entra, é envolvida em formato PDF, sai com aparência idêntica.",
    "What You're Getting": "O Que Você Está Recebendo",
    "Files upload through encryption and get deleted after 24 hours. I can't see what you're converting.": "Os arquivos são enviados por criptografia e excluídos após 24 horas. Não posso ver o que você está convertendo.",
    "No Limits": "Sem Limites",
    "Convert 5 files or 500. There's no daily cap or paywall.": "Converta 5 arquivos ou 500. Não há limite diário ou paywall.",
    "Works Anywhere": "Funciona Em Qualquer Lugar",
    "Phone, tablet, computer - doesn't matter. It's just a website.": "Telefone, tablet, computador - não importa. É apenas um site.",
    "Quick": "Rápido",
    "Usually done in under 5 seconds. The servers are optimized for speed.": "Geralmente feito em menos de 5 segundos. Os servidores são otimizados para velocidade.",
    "Different Formats": "Diferentes Formatos",
    "JPG, PNG, GIF, BMP, WebP - they all work.": "JPG, PNG, GIF, BMP, WebP - todos funcionam.",
    "No Signup": "Sem Cadastro",
    "Just use it. No account, no email, no password.": "Apenas use. Sem conta, sem e-mail, sem senha.",
    "How to Use This": "Como Usar Isso",
    "Pick Your Images": "Escolha Suas Imagens",
    "Click the upload box or drag files from your desktop. You can select multiple at once - hold Ctrl (Windows) or Command (Mac) while clicking. Works with JPG, PNG, GIF, BMP, and WebP. Max 2GB per file.": "Clique na caixa de upload ou arraste arquivos da sua área de trabalho. Você pode selecionar vários de uma vez - segure Ctrl (Windows) ou Command (Mac) enquanto clica. Funciona com JPG, PNG, GIF, BMP e WebP. Máximo de 2GB por arquivo.",
    "Check Your Files": "Verifique Seus Arquivos",
    "You'll see thumbnails of everything you uploaded. They'll appear in your PDF in this same order. Remove any mistakes by clicking the X, or add more files if you forgot something.": "Você verá miniaturas de tudo que enviou. Eles aparecerão em seu PDF nesta mesma ordem. Remova quaisquer erros clicando no X, ou adicione mais arquivos se esqueceu algo.",
    "Download the PDF": "Baixar o PDF",
    "Hit convert and wait a couple seconds. You'll go to a download page where you can grab your PDF. The file stays available for 24 hours if you need it again.": "Clique em converter e aguarde alguns segundos. Você irá para uma página de download onde pode pegar seu PDF. O arquivo fica disponível por 24 horas se você precisar dele novamente.",
    "Common Questions": "Perguntas Comuns",
    "How long does the JPG to PDF conversion process actually take?": "Quanto tempo realmente leva o processo de conversão de JPG para PDF?",
    "Usually 2-5 seconds per image. Ten photos takes about 20-30 seconds total. Huge files or slow internet might add some time, but it's rare for anything to take over a minute.": "Geralmente 2-5 segundos por imagem. Dez fotos levam cerca de 20-30 segundos no total. Arquivos grandes ou internet lenta podem adicionar algum tempo, mas é raro algo levar mais de um minuto.",
    "Is there a limit on how many files I can convert per day or month?": "Existe um limite de quantos arquivos posso converter por dia ou mês?",
    "Nope. Use it as much as you want. I've seen people convert thousands of files over several months. No daily caps, no monthly quotas, no paid upgrades.": "Não. Use o quanto quiser. Já vi pessoas converterem milhares de arquivos ao longo de vários meses. Sem limites diários, sem cotas mensais, sem atualizações pagas.",
    "Can I convert multiple JPG images into a single PDF file?": "Posso converter várias imagens JPG em um único arquivo PDF?",
    "Yes! You can select multiple JPG images at once, and they will all be combined into a single PDF document. The images will appear in the order you selected them. This is perfect for creating multi-page documents from scanned images or photo collections.": "Sim! Você pode selecionar várias imagens JPG de uma vez, e todas serão combinadas em um único documento PDF. As imagens aparecerão na ordem em que você as selecionou. Isso é perfeito para criar documentos de várias páginas a partir de imagens digitalizadas ou coleções de fotos.",
    "Do I need to install any software to use this JPG to PDF converter?": "Preciso instalar algum software para usar este conversor de JPG para PDF?",
    "No installation needed! This is a web-based tool that works directly in your browser. It's compatible with Chrome, Firefox, Safari, Edge, and all modern browsers on Windows, Mac, Linux, Android, and iOS. Just visit the website and start converting.": "Nenhuma instalação necessária! Esta é uma ferramenta baseada na web que funciona diretamente no seu navegador. É compatível com Chrome, Firefox, Safari, Edge e todos os navegadores modernos no Windows, Mac, Linux, Android e iOS. Basta visitar o site e começar a converter.",
    "What happens to my files after I upload them to your server?": "O que acontece com meus arquivos depois que os envio para o seu servidor?",
    "You upload through encryption, I convert them to PDF, you download it. The files sit on my server for 24 hours in case you need them again, then they're automatically deleted. No backups, no archives.": "Você envia por criptografia, eu os converto para PDF, você baixa. Os arquivos ficam no meu servidor por 24 horas caso você precise deles novamente, então são automaticamente excluídos. Sem backups, sem arquivos.",
    "English": "Inglês",
    "Portuguese": "Português",
    "Spanish": "Espanhol",
    "German": "Alemão",
    "Indonesian": "Indonésio",
    "French": "Francês",
    "Turkish": "Turco",
}

def process_po_file():
    po_file = 'locale/pt/LC_MESSAGES/django.po'
    
    print(f"Reading {po_file}...")
    
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    translated_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts with msgid
        if line.startswith('msgid "'):
            # Extract the msgid value (handle multiline)
            msgid_value = line[7:-2]  # Remove 'msgid "' and '"\n'
            
            # Check if there are continuation lines
            j = i + 1
            while j < len(lines) and lines[j].startswith('"') and not lines[j].startswith('msgstr'):
                msgid_value += lines[j][1:-2]  # Remove quotes and newline
                j += 1
            
            # Now j should be at msgstr line
            if j < len(lines) and lines[j].startswith('msgstr "'):
                msgstr_value = lines[j][8:-2]  # Extract msgstr value
                
                # Check if msgstr is empty
                if msgstr_value == '':
                    # Look for translation
                    if msgid_value in PT_TRANSLATIONS:
                        translation = PT_TRANSLATIONS[msgid_value]
                        
                        # Write msgid lines
                        for k in range(i, j):
                            new_lines.append(lines[k])
                        
                        # Write translated msgstr
                        new_lines.append(f'msgstr "{translation}"\n')
                        
                        translated_count += 1
                        print(f"  ✓ Translated: {msgid_value[:60]}...")
                        
                        # Skip to next entry
                        i = j + 1
                        continue
        
        # If not translated, keep original line
        new_lines.append(line)
        i += 1
    
    # Write back
    print(f"\nWriting translations to {po_file}...")
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✓ Success! Translated {translated_count} strings")
    print("\nNext steps:")
    print("1. Run: django-admin compilemessages")
    print("2. Run: python manage.py runserver")
    print("3. Test: http://127.0.0.1:8000/pt/")
    print("4. Hard refresh with Ctrl+Shift+R")

if __name__ == '__main__':
    try:
        process_po_file()
    except FileNotFoundError:
        print("Error: locale/pt/LC_MESSAGES/django.po not found")
        print("Run: django-admin makemessages -l pt")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()