import pytest

from selenium import webdriver

from selenium.webdriver.chrome.options import Options



@pytest.fixture(scope="function")

def driver():

    options = Options()

    

    # --- 1. CONFIGURACIÓN DE IDENTIDAD (Anti-Bot) ---

    # Usamos el modo headless "new", que es casi imposible de detectar

    options.add_argument("--headless=new") 

    

    # Ocultamos que el navegador es controlado por Selenium

    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_experimental_option('useAutomationExtension', False)

    

    # User-agent de un Chrome real en Windows para que TN no sospeche

    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")



    # --- 2. CONFIGURACIÓN DE ESTABILIDAD ---

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--window-size=1920,1080")

    

    driver = webdriver.Chrome(options=options)

    

    # --- 3. VELOCIDAD (Bloqueo de recursos pesados) ---

    # Bloqueamos imágenes y trackers, pero dejamos pasar CSS y fuentes para que se vea bien

    #driver.execute_cdp_cmd("Network.setBlockedURLs", {

     #   "urls": [

      #      "*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp", 

       #     "*google-analytics.com*", "*doubleclick.net*", 

        #    "*ads*", "*video*", "*metrics*"

        #]

    #})

    #driver.execute_cdp_cmd("Network.enable", {})

    

    # --- 4. PARCHE FINAL DE JAVASCRIPT ---

    # Borramos el rastro de la propiedad 'navigator.webdriver'

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    

    yield driver

    

    driver.quit()
