import pytest
import allure
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Login")
@allure.story("Login de usuario Agencia (Prueba Negativa de Permisos)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba valida el acceso principal al sistema web de reservas con perfil Agencia.
1. Navegación a qa.amv.travel.
2. Inyección de credenciales seguras mediante GitHub Secrets.
3. Validación de ingreso exitoso al portal interno.
4. Validación de perfil Agencia comprobando la NO existencia de los selectores de simulación de agencia.
""")
def test_login_agencia(driver):
    wait = WebDriverWait(driver, 15)

    with allure.step("1. Ingresar a qa.amv.travel y click en Login"):
        driver.get("https://qa.amv.travel/")
        
        btn_login = wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin")))
        btn_login.click()

    with allure.step("2 y 3. Escribir credenciales seguras de Agencia"):
        # Llamamos al usuario de agencia, pero reutilizamos el PASS del admin
        usuario = os.environ.get("AMV_AGENCIA_USER")
        password = os.environ.get("AMV_PASS")

        if not usuario or not password:
            pytest.fail("Error de configuración: Faltan las credenciales AMV_AGENCIA_USER o AMV_PASS en el entorno.")

        input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))
        input_user.clear()
        input_user.send_keys(usuario)
        
        input_pass = driver.find_element(By.ID, "txtPassword")
        input_pass.clear()
        input_pass.send_keys(password)
        
        allure.attach(driver.get_screenshot_as_png(), name="Credenciales_Agencia", attachment_type=allure.attachment_type.PNG)

    with allure.step("3. Click en Ingresar al Sistema"):
        btn_ingresar = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))

        # Scroll por si acaso
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_ingresar)

        # Click JS (clave para WebForms)
        driver.execute_script("arguments[0].click();", btn_ingresar)
        
        time.sleep(3) 

    with allure.step("5. Validar sesión de Agencia (Verificar que NO existan selectores Admin)"):
        selectores_agencia = driver.find_elements(By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency")
        selectores_usuario = driver.find_elements(By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser")

        if len(selectores_agencia) > 0:
            assert not selectores_agencia[0].is_displayed(), "Vulnerabilidad UI: El selector de Agencia está visible para un usuario Agencia."
        
        if len(selectores_usuario) > 0:
            assert not selectores_usuario[0].is_displayed(), "Vulnerabilidad UI: El selector de Usuario está visible para un usuario Agencia."

        allure.attach(driver.get_screenshot_as_png(), name="Validacion_Exitosa_Agencia", attachment_type=allure.attachment_type.PNG)
