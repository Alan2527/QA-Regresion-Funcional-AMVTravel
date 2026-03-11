import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. TU FIXTURE BASE ---
@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    
    yield driver
    driver.quit()

# --- 2. EL NUEVO FIXTURE DE LOGIN SILENCIOSO ---
@pytest.fixture(scope="function")
def logged_in_driver(driver):
    wait = WebDriverWait(driver, 15)
    
    # Traemos las credenciales de los secretos de GitHub
    usuario = os.environ.get("AMV_USER")
    password = os.environ.get("AMV_PASS")

    if not usuario or not password:
        pytest.fail("Faltan las credenciales en las variables de entorno para el login silencioso")

    # Navegación y Login rápido por detrás
    driver.get("https://qa.amv.travel/")
    wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin"))).click()
    
    input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))
    input_user.clear()
    input_user.send_keys(usuario)
    
    input_pass = driver.find_element(By.ID, "txtPassword")
    input_pass.clear()
    input_pass.send_keys(password)
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@value='Ingresar']"))).click()
    
    # Esperamos a que la carga inicial del sistema pase
    time.sleep(3) 
    
    yield driver

# =================================================================
# ALLURE ENVIRONMENT
# =================================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Hook de pytest que se ejecuta al finalizar toda la suite de pruebas.
    Genera el archivo environment.properties para el reporte de Allure.
    """
    # Esta es la carpeta por defecto donde Allure guarda los resultados (los archivos .json)
    allure_dir = "allure-results" 
    
    # Nos aseguramos de que la carpeta exista antes de intentar crear el archivo
    if not os.path.exists(allure_dir):
        os.makedirs(allure_dir)
        
    env_file = os.path.join(allure_dir, "environment.properties")
    
    # Escribimos las variables que queremos que aparezcan en el panel "Environment"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("Navegador=Chrome (Headless)\n")
        f.write("Entorno=QA\n")
        f.write("URL_Frontend=https://qa.amv.travel/\n")
        f.write("URL_Backoffice=https://qa.bo.amv.travel\n")
        f.write("Sistema=Motor_Multidestinos\n")
        f.write("Framework=Pytest+Selenium\n")
