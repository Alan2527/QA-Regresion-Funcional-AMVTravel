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
Valida login Admin:
1. Navega al sitio
2. Hace click en login
3. Completa credenciales
4. Ingresa al sistema
5. Valida perfil admin
""")
def test_login_admin(driver):

    wait = WebDriverWait(driver, 20)

    # ==========================================
    # 1. IR A LA WEB
    # ==========================================
    with allure.step("1. Ingresar a la web y hacer click en Login"):
        driver.get("https://qa.amv.travel/")

        btn_login = wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin")))
        btn_login.click()

        allure.attach(driver.get_screenshot_as_png(), "1_click_login", allure.attachment_type.PNG)

    # ==========================================
    # 2. CREDENCIALES
    # ==========================================
    with allure.step("2. Ingresar credenciales"):
        usuario = os.environ.get("AMV_USER")
        password = os.environ.get("AMV_PASS")

        if not usuario or not password:
            pytest.fail("Faltan variables de entorno")

        input_user = wait.until(EC.visibility_of_element_located((By.ID, "txtUser")))
        input_user.clear()
        input_user.send_keys(usuario)

        input_pass = wait.until(EC.visibility_of_element_located((By.ID, "txtPassword")))
        input_pass.clear()
        input_pass.send_keys(password)

        allure.attach(driver.get_screenshot_as_png(), "2_credenciales", allure.attachment_type.PNG)

    # ==========================================
    # 3. CLICK LOGIN (FIX REAL)
    # ==========================================
    with allure.step("3. Click en Ingresar"):

        # Esperar que esté visible y habilitado
        btn_ingresar = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
        wait.until(lambda d: btn_ingresar.is_displayed() and btn_ingresar.is_enabled())

        # Scroll por si está tapado
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_ingresar)
        time.sleep(0.5)

        # Click por JS (evita problemas de overlay)
        driver.execute_script("arguments[0].click();", btn_ingresar)

        # Esperar navegación real
        wait.until(EC.url_contains("amv.travel"))

        allure.attach(driver.get_screenshot_as_png(), "3_post_login", allure.attachment_type.PNG)

    # ==========================================
    # 4. VALIDACIÓN ADMIN
    # ==========================================
    with allure.step("4. Validar perfil Admin"):

        selector_agencia = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ts-wrapper.ddGuestAgency"))
        )

        selector_usuario = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ts-wrapper.ddGuestUser"))
        )

        assert selector_agencia.is_displayed()
        assert selector_usuario.is_displayed()

        allure.attach(driver.get_screenshot_as_png(), "4_validacion_admin", allure.attachment_type.PNG)
