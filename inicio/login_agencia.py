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
Este caso de prueba valida el acceso al sistema con credenciales de Agencia.
Asegura que la sesión se inicie correctamente pero valida estrictamente que
los controles exclusivos de Administrador (simulación de agencia) NO sean visibles.
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

    with allure.step("4. Click en el botón Ingresar"):
        btn_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@value='Ingresar']")))
        btn_ingresar.click()
        
        time.sleep(3) 

    with allure.step("5. Validar sesión de Agencia (Verificar que NO existan selectores Admin)"):
        selectores_agencia = driver.find_elements(By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency")
        selectores_usuario = driver.find_elements(By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser")

        if len(selectores_agencia) > 0:
            assert not selectores_agencia[0].is_displayed(), "Vulnerabilidad UI: El selector de Agencia está visible para un usuario Agencia."
        
        if len(selectores_usuario) > 0:
            assert not selectores_usuario[0].is_displayed(), "Vulnerabilidad UI: El selector de Usuario está visible para un usuario Agencia."

        allure.attach(driver.get_screenshot_as_png(), name="Validacion_Exitosa_Agencia", attachment_type=allure.attachment_type.PNG)
