import pytest
import allure
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Login BackOffice")
@allure.story("Login de usuario Administrador en BO")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
Este caso de prueba valida el acceso principal al BackOffice (BO).
Es un flujo BLOQUEANTE ya que el resto de las pruebas E2E del BO dependen de una sesión válida.
1. Navegación a qa.bo.amv.travel/login.
2. Inyección de credenciales seguras mediante GitHub Secrets.
3. Click en ingresar.
4. Validación de ingreso exitoso comprobando que la URL cambie a /main.
""")
def test_login_bo_admin(driver):
    wait = WebDriverWait(driver, 15)

    with allure.step("1. Ingresar a qa.bo.amv.travel/login"):
        driver.get("https://qa.bo.amv.travel/login")
        # Esperamos a que el form de login cargue visiblemente
        wait.until(EC.visibility_of_element_located((By.ID, "txtUser")))

    with allure.step("2. Escribir credenciales seguras"):
        # Reutilizamos AMV_USER. 
        # Si la contraseña del BO es la misma que la del Front, cambiá "BO_PASS" por "AMV_PASS"
        usuario = os.environ.get("BO_USER")
        password = os.environ.get("BO_PASS") 

        # Cortamos la prueba inmediatamente si GitHub no nos pasó las variables
        if not usuario or not password:
            pytest.fail("Error de seguridad: Faltan las credenciales (AMV_USER o BO_PASS) en el entorno.")

        input_user = driver.find_element(By.ID, "txtUser")
        input_user.clear()
        input_user.send_keys(usuario)
        
        input_pass = driver.find_element(By.ID, "txtPassword")
        input_pass.clear()
        input_pass.send_keys(password)
        
        # Guardamos la captura en Allure justo antes de hacer clic
        allure.attach(driver.get_screenshot_as_png(), name="Credenciales_BO_Completas", attachment_type=allure.attachment_type.PNG)

    with allure.step("3. Click en el botón Ingresar"):
        # Clickeamos el botón de ingreso
        btn_ingresar = wait.until(EC.element_to_be_clickable((By.ID, "btnLogin")))
        btn_ingresar.click()

    with allure.step("4. Validar ingreso exitoso (Cambio de URL)"):
        # Usamos el Expected Condition nativo para validar que la URL exacta sea la esperada
        try:
            wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))
        except Exception:
            # Si falla (por timeout o credenciales incorrectas), capturamos pantalla del error antes de morir
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Login_BO", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Falló la validación: La URL no cambió a /main. URL actual: {driver.current_url}")
        
        # Tomamos la captura final demostrando que estamos logueados en el Main
        allure.attach(driver.get_screenshot_as_png(), name="Validacion_Exitosa_BO", attachment_type=allure.attachment_type.PNG)
