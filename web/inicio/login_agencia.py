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
def test_login_admin(driver):
    wait = WebDriverWait(driver, 20)

    with allure.step("1. Ingresar a qa.amv.travel"):
        driver.get("https://qa.amv.travel/Login.aspx")

    with allure.step("2. Escribir credenciales"):
        usuario = os.environ.get("AMV_AGENCIA_USER")
        password = os.environ.get("AMV_PASS")

        if not usuario or not password:
            pytest.fail("Faltan credenciales en GitHub Secrets")

        input_user = wait.until(EC.visibility_of_element_located((By.ID, "txtUser")))
        input_user.clear()
        input_user.send_keys(usuario)

        input_pass = driver.find_element(By.ID, "txtPassword")
        input_pass.clear()
        input_pass.send_keys(password)

        allure.attach(driver.get_screenshot_as_png(), name="Credenciales", attachment_type=allure.attachment_type.PNG)

    with allure.step("3. Click en Ingresar al Sistema"):
        btn_ingresar = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))

        # Scroll por si acaso
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_ingresar)

        # Click JS (clave para WebForms)
        driver.execute_script("arguments[0].click();", btn_ingresar)

    with allure.step("4. Esperar login exitoso"):
        # Espera a que cambie la URL o aparezca algo del sistema interno
        wait.until(lambda d: "Login" not in d.current_url)

        # Alternativa más robusta (por si no cambia la URL):
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

        time.sleep(3)

    with allure.step("5. Validar sesión Admin"):
        selector_agencia = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency"))
        )
        selector_usuario = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser"))
        )

        assert selector_agencia.is_displayed(), "No se visualiza selector de Agencia"
        assert selector_usuario.is_displayed(), "No se visualiza selector de Usuario"

        allure.attach(driver.get_screenshot_as_png(), name="Login_OK", attachment_type=allure.attachment_type.PNG)
