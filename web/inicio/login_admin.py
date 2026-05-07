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
    wait = WebDriverWait(driver, 15)

    with allure.step("1. Ingresar a qa.amv.travel y click en Login"):
        driver.get("https://qa.amv.travel/")
        
        # Esperamos a que el enlace esté clickeable y le hacemos click
        btn_login = wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin")))
        btn_login.click()

    with allure.step("2 y 3. Escribir credenciales seguras"):
        # Obtenemos las credenciales desde las variables de entorno (GitHub Secrets)
        usuario = os.environ.get("AMV_USER")
        password = os.environ.get("AMV_PASS")

        # Cortamos la prueba inmediatamente si GitHub no nos pasó las variables
        if not usuario or not password:
            pytest.fail("Error de seguridad: Faltan las credenciales AMV_USER o AMV_PASS en el entorno.")

        # Esperamos a que el input de usuario aparezca
        input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))
        input_user.clear()
        input_user.send_keys(usuario)
        
        input_pass = driver.find_element(By.ID, "txtPassword")
        input_pass.clear()
        input_pass.send_keys(password)
        
        # Guardamos la captura en Allure justo antes de hacer clic
        allure.attach(driver.get_screenshot_as_png(), name="Credenciales_Completas", attachment_type=allure.attachment_type.PNG)

    with allure.step("4. Click en el botón Ingresar"):
        # Clickeamos el botón de ingreso
        btn_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@value='Ingresar']")))
        btn_ingresar.click()
        
        # Damos unos segundos para que se resuelva el inicio de sesión y cargue la vista interna
        time.sleep(3) 

    with allure.step("5. Validar sesión de Admin (Selectores de Agencia y Usuario)"):
        # Validamos el selector de Agencia
        selector_agencia = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency"
        )))
        
        # Validamos el selector de Usuario
        selector_usuario = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser"
        )))

        # Aserciones para confirmar que los elementos no solo existen en el DOM, sino que son visibles
        assert selector_agencia.is_displayed(), "Fallo la validación Admin: No se visualiza el selector de simulación de Agencia."
        assert selector_usuario.is_displayed(), "Fallo la validación Admin: No se visualiza el selector de simulación de Usuario."

        # Tomamos la captura final demostrando que estamos logueados y con la UI de Administrador
        allure.attach(driver.get_screenshot_as_png(), name="Validacion_Exitosa_Admin", attachment_type=allure.attachment_type.PNG)
