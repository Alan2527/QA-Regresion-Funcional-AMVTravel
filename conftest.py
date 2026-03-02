import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="function")
def driver():
    options = Options()
    
    # --- 1. CONFIGURACIÓN DE EJECUCIÓN ---
    # Mantenemos el modo headless porque es obligatorio para que funcione en 
    # los servidores de GitHub Actions (ubuntu-latest no tiene interfaz gráfica).
    options.add_argument("--headless=new") 
    
    # --- 2. CONFIGURACIÓN DE ESTABILIDAD (Docker / CI-CD) ---
    # Estos tres parámetros son vitales para que Chrome no crashee en Linux
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    
    yield driver
    
    driver.quit()
