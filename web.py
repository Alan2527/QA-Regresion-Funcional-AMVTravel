import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Frontend AMV Travel")
@allure.story("Flujo de validación principal")
def test_flujo_amv_travel(driver):
    wait = WebDriverWait(driver, 15)

    with allure.step("1. Ingresar a qa.amv.travel y click en Login"):
        driver.get("https://qa.amv.travel/")
        
        # Esperamos a que el enlace esté clickeable y le hacemos click
        btn_login = wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin")))
        btn_login.click()

    with allure.step("2 y 3. Escribir credenciales"):
        # Esperamos a que el input de usuario aparezca (por si hay una animación o modal)
        input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))
        input_user.clear()
        input_user.send_keys("Pablo@amv.travel")
        
        input_pass = driver.find_element(By.ID, "txtPassword")
        input_pass.clear()
        input_pass.send_keys("amvtest123")
        
        # Captura opcional antes de enviar
        allure.attach(driver.get_screenshot_as_png(), name="Credenciales_Completas", attachment_type=allure.attachment_type.PNG)

    with allure.step("4. Click en el botón Ingresar"):
        # Usamos XPATH para encontrar cualquier elemento (input o button) con value="Ingresar"
        btn_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@value='Ingresar']")))
        btn_ingresar.click()
        
        # Espera breve para dar tiempo a que comience la carga del dashboard/home
        time.sleep(3) 
        allure.attach(driver.get_screenshot_as_png(), name="Post_Click_Ingresar", attachment_type=allure.attachment_type.PNG)

    # 5. Hasta acá llegamos por ahora.
