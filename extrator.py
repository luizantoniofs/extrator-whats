from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuração do WebDriver
options = Options()
options.add_argument("--profile-directory=Default")  # Usa o perfil padrão do Chrome
options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção de bot
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove aviso de automação
options.add_experimental_option("useAutomationExtension", False)

# Inicializa o ChromeDriver
service = Service("C:\\Users\\TI-Lesco\\.wdm\\drivers\\chromedriver\\win64\\133.0.6943.98\\chromedriver-win32\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

try:
    # Abre o WhatsApp Web
    driver.get("https://web.whatsapp.com/")

    input("📷 Escaneie o QR Code no WhatsApp Web e pressione ENTER para continuar...")

    # Aguarda os chats carregarem completamente
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Lista de conversas')]"))
    )
    print("✅ Chats carregados com sucesso.")

    # Captura a lista de chats
    chats = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Lista de conversas')]/div")

    if not chats:
        print("⚠ Nenhum chat encontrado. Verifique se há mensagens disponíveis.")
        driver.quit()
        exit()

    # Abre o arquivo para salvar as conversas
    with open("conversas_whatsapp.txt", "w", encoding="utf-8") as file:
        for chat in chats:
            try:
                chat.click()
                time.sleep(3)  # Tempo para carregar a conversa

                # Captura o nome ou número do contato
                try:
                    contact_name = driver.find_element(By.CSS_SELECTOR, "header .ggj6brxn").text
                except:
                    contact_name = "Contato Desconhecido"

                # Captura todas as mensagens da conversa
                messages = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")

                file.write(f"\n{'='*50}\n")
                file.write(f"📌 Conversa com: {contact_name}\n")
                file.write(f"{'='*50}\n\n")

                for message in messages:
                    try:
                        timestamp_element = message.find_element(By.CSS_SELECTOR, "div.copyable-text")
                        timestamp = timestamp_element.get_attribute("data-pre-plain-text")
                        text = message.find_element(By.CSS_SELECTOR, "span.selectable-text").text

                        if text.strip():
                            file.write(f"{timestamp} {text}\n")
                    except Exception as e:
                        print(f"⚠ Erro ao capturar mensagem: {e}")

                file.write("\n")

            except Exception as e:
                print(f"⚠ Erro ao acessar chat: {e}")

    print("✅ Extração de conversas concluída! O arquivo 'conversas_whatsapp.txt' foi gerado.")

finally:
    print("🔚 Finalizando sessão...")
    driver.quit()
