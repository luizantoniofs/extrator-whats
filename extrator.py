from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# 🔧 Configuração do WebDriver
options = Options()
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Inicializa o ChromeDriver
service = Service("C:\\Users\\TI-Lesco\\.wdm\\drivers\\chromedriver\\win64\\133.0.6943.98\\chromedriver-win32\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# 📅 Obtém a data de hoje
hoje = datetime.now().strftime("%H:%M")  # Obtém a hora atual para comparação
hoje_texto = "hoje"  # Como o WhatsApp Web exibe a data do dia

try:
    # Abre o WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    input("📷 Escaneie o QR Code no WhatsApp Web e pressione ENTER para continuar...")

    # ✅ Aguarda os chats carregarem (até 60 segundos)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='grid']"))
        )
        print("✅ Chats carregados com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao carregar os chats: {e}")
        driver.quit()
        exit()

    # 📂 Criando o arquivo de saída
    with open("conversas_do_dia.txt", "w", encoding="utf-8") as file:
        chats = driver.find_elements(By.XPATH, "//div[@role='grid']/div")

        if not chats:
            print("⚠ Nenhum chat encontrado. Verifique se há mensagens disponíveis.")
            driver.quit()
            exit()

        mensagens_extraidas = False  # Para verificar se extraímos algo

        for chat in chats:
            try:
                # 🔍 Obtém a data/hora da última mensagem desse chat
                try:
                    last_message_time = chat.find_element(By.XPATH, ".//div[contains(@class, '_2fq0t')]").text.strip()
                except:
                    last_message_time = ""

                print(f"📌 Verificando chat - Última mensagem: {last_message_time}")  # Debug

                # 🕒 Verifica se a última mensagem foi enviada **hoje**
                if last_message_time.lower() != hoje_texto and ":" not in last_message_time:
                    continue  # Se não for de hoje ou não for um horário, ignora

                # 🔍 Obtém o nome/número do contato
                try:
                    contact_name = chat.find_element(By.XPATH, ".//span[contains(@class, '_21S-L')]").text
                except:
                    contact_name = "Contato Desconhecido"

                print(f"✅ Acessando chat com: {contact_name}")

                chat.click()
                time.sleep(2)  # Espera carregar a conversa

                # 📩 Captura as mensagens da conversa
                messages = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
                mensagens_do_dia = []

                for message in messages:
                    try:
                        timestamp_element = message.find_element(By.CSS_SELECTOR, "div.copyable-text")
                        timestamp = timestamp_element.get_attribute("data-pre-plain-text").strip()

                        # Captura o conteúdo da mensagem
                        text = message.find_element(By.CSS_SELECTOR, "span.selectable-text").text

                        # 📅 Filtra mensagens que são de hoje
                        if "hoje" in timestamp.lower() or hoje in timestamp:
                            mensagens_do_dia.append(f"{timestamp} {text}")

                    except:
                        pass

                # 📂 Grava no arquivo apenas se houver mensagens do dia
                if mensagens_do_dia:
                    mensagens_extraidas = True  # Marcamos que ao menos um chat foi extraído
                    file.write(f"\n{'='*50}\n")
                    file.write(f"📌 Conversa com: {contact_name}\n")
                    file.write(f"{'='*50}\n\n")

                    for msg in mensagens_do_dia:
                        file.write(f"{msg}\n")

                    file.write("\n")

            except Exception as e:
                print(f"⚠ Erro ao acessar chat: {e}")

    # 🔎 Verificação final
    if not mensagens_extraidas:
        print("⚠ Nenhuma mensagem do dia foi encontrada. O arquivo pode estar vazio.")

    print("✅ Extração de mensagens do dia concluída! O arquivo 'conversas_do_dia.txt' foi gerado.")

finally:
    # 🚪 Fecha o navegador após a execução
    print("🔚 Finalizando sessão...")
    driver.quit()
