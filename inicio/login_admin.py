import pytest
import allure
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Login")
@allure.story("Login de usuario Administrador")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
Este caso de prueba valida el acceso principal al sistema web de reservas con perfil Administrador.
Es un flujo BLOQUEANTE ya que el resto de las pruebas E2E dependen de una sesión válida con permisos elevados.
1. Navegación a qa.amv.travel.
2. Inyección de credenciales seguras mediante GitHub Secrets.
3. Validación de ingreso exitoso al portal interno.
4. Validación de perfil Admin comprobando la existencia de los selectores de simulación de agencia.
""")
def test_login_admin(driver):
    wait = WebDriverWait(driver, 15)[cite: 4]

    with allure.step("1. Ingresar a qa.amv.travel y click en Login"):
        driver.get("https://qa.amv.travel/")[cite: 4]
        
        # Esperamos a que el enlace esté clickeable y le hacemos click
        btn_login = wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin")))[cite: 4]
        btn_login.click()[cite: 4]

    with allure.step("2 y 3. Escribir credenciales seguras"):
        # Obtenemos las credenciales desde las variables de entorno (GitHub Secrets)
        usuario = os.environ.get("AMV_USER")[cite: 4]
        password = os.environ.get("AMV_PASS")[cite: 4]

        # Cortamos la prueba inmediatamente si GitHub no nos pasó las variables
        if not usuario or not password:
            pytest.fail("Error de seguridad: Faltan las credenciales AMV_USER o AMV_PASS in el entorno.")[cite: 4]

        # Esperamos a que el input de usuario aparezca
        input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))[cite: 4]
        input_user.clear()[cite: 4]
        input_user.send_keys(usuario)[cite: 4]
        
        input_pass = driver.find_element(By.ID, "txtPassword")[cite: 4]
        input_pass.clear()[cite: 4]
        input_pass.send_keys(password)[cite: 4]
        
        # Guardamos la captura en Allure justo antes de hacer clic
        allure.attach(driver.get_screenshot_as_png(), name="Credenciales_Completas", attachment_type=allure.attachment_type.PNG)[cite: 4]

    with allure.step("4. Click en el botón Ingresar"):
        # Esperamos presencia en el DOM garantizando que el elemento existe independientemente de las animaciones
        btn_ingresar = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
        
        # Forzamos el click a través de JavaScript para evitar fallas headless de Tailwind/ASP.NET
        driver.execute_script("arguments[0].click();", btn_ingresar)
        
        # Damos unos segundos para que se resuelva el inicio de sesión y cargue la vista interna
        time.sleep(3)[cite: 4] 

    with allure.step("5. Validar sesión de Admin (Selectores de Agencia y Usuario)"):
        # Validamos el selector de Agencia
        selector_agencia = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency"
        )))[cite: 4]
        
        # Validamos el selector de Usuario
        selector_usuario = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser"
        )))[cite: 4]

        # Aserciones para confirmar que los elementos no solo existen en el DOM, sino que son visibles
        assert selector_agencia.is_displayed(), "Fallo la validación Admin: No se visualiza el selector de simulación de Agencia."[cite: 4]
        assert selector_usuario.is_displayed(), "Fallo la validación Admin: No se visualiza el selector de simulación de Usuario."[cite: 4]

        # Tomamos la captura final demostrando que estamos logueados y con la UI de Administrador
        allure.attach(driver.get_screenshot_as_png(), name="Validacion_Exitosa_Admin", attachment_type=allure.attachment_type.PNG)[cite: 4]
