import pytest
import allure
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Ofertas / Oportunidades")
@allure.story("Nuevo flujo E2E: Búsqueda de Oferta a 7 días y validación de UI")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el nuevo flujo de ofertas:
1. Login silencioso (vía fixture).
2. Selección de la pestaña Ofertas (href='#tabOpportunity').
3. Ingreso de fecha dinámica (hoy + 7 días) y cierre del calendario clickeando fuera.
4. Uso de los selectores custom (TomSelect) para parámetros de viaje y habitación.
5. Validación de la carga de imágenes por defecto y estructura HTML (h6).
6. Avance a la pantalla final y validación de la tabla de resumen.
""")
def test_ofertas_nuevo_flujo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    def seleccionar_en_tomselect(parent_class, valor):
        """Helper para interactuar con los selectores custom, encapsulado a su propio contenedor"""
        # 1. Clickeamos el control para abrir el desplegable
        control = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f".{parent_class} .ts-control")))
        control.click()
        time.sleep(0.5) 
        
        # 2. Buscamos la opción ESTRICTAMENTE dentro del parent_class para evitar falsos positivos
        xpath_opcion = f"//div[contains(@class, '{parent_class}')]//div[contains(@class, 'option') and text()='{valor}']"
        opcion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion)))
        opcion.click()

    try:
        with allure.step("1 a 5. Navegar, ingresar fecha y buscar"):
            # Click pestaña
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabOpportunity']"))).click()
            
            # Fecha dinámica
            fecha_oferta = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
            input_fecha = wait.until(EC.element_to_be_clickable((By.ID, "txtOpportunityCalendar")))
            input_fecha.clear()
            input_fecha.send_keys(fecha_oferta)
            
            # Clic neutro para cerrar calendario
            body = driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element_with_offset(body, 0, 0).click().perform()
            time.sleep(0.5)
            
            # Botón buscar
            wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMainSlider$ctl00$ctrlOpportunitySearchControl$btnSearch"))).click()
            
            # CAPTURA PASO 1
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Realizada", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 a 9. Seleccionar parámetros de viaje (4) y tipo de habitación (2)"):
            # Parámetros de viaje
            seleccionar_en_tomselect("container-travel-paremeters", "4")
            
            # Tipo de habitación (ahora sí, buscando el "2" literal dentro de su contenedor)
            seleccionar_en_tomselect("container-type-room-paremeter", "2")
            
            # CAPTURA PASO 2
            allure.attach(driver.get_screenshot_as_png(), name="2_Parametros_Seleccionados", attachment_type=allure.attachment_type.PNG)

        with allure.step("10 y 11. Avanzar y validar contenido del acordeón (Imagen y H6)"):
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lnkNext"))).click()
            
            acordeon = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "accordion-content")))
            
            # Validación de la imagen default
            img_divs = acordeon.find_elements(By.XPATH, ".//div[contains(@style, 'no_image_86_0.png')]")
            assert len(img_divs) > 0, "Validación fallida: No se encontró el div con la imagen 'no_image_86_0.png'."
            
            # Validación del H6
            h6_elements = acordeon.find_elements(By.CSS_SELECTOR, "h6.h6style")
            assert len(h6_elements) > 0, "Validación fallida: No se encontró el tag <h6> con la clase 'h6style'."
            
            # CAPTURA PASO 3
            allure.attach(driver.get_screenshot_as_png(), name="3_Acordeon_Validado", attachment_type=allure.attachment_type.PNG)

        with allure.step("12 y 13. Avanzar y validar la existencia de la tabla final"):
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lnkNext"))).click()
            
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")),
                message="Validación fallida: No se encontró la tabla de resumen final."
            )

            # CAPTURA PASO 4
            allure.attach(driver.get_screenshot_as_png(), name="4_Tabla_Final_Validada", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        # Captura de error
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_en_Nuevo_Flujo_Ofertas", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
