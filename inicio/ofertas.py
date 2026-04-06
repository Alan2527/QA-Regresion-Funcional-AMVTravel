import pytest
import allure
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Ofertas")
@allure.story("Nuevo flujo E2E: Validación exhaustiva y agregado al Carrito")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo End-to-End (E2E) de la cotización de un circuito (Oferta):
1. Login silencioso y navegación a la pestaña de Ofertas.
2. Ingreso de fecha (hoy + 7 días) y cierre del calendario.
3. Uso de los selectores para parámetros de viaje y habitación.
4. Bucle dinámico que despliega CADA acordeón de itinerario y valida su contenido (Hoteles, Servicios, Servicios opcionales).
5. Despliegue y validación estructural del acordeón 'Resumen de precios'.
6. Avance a la pantalla final y validación VISUAL de la tabla de resumen.
7. Agregado de la oferta al carrito de compras y validación de éxito.
""")
def test_ofertas_nuevo_flujo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    def seleccionar_en_tomselect(parent_class, valor):
        control = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f".{parent_class} .ts-control")))
        control.click()
        time.sleep(0.5) 
        
        opcion = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//div[contains(@class, '{parent_class}')]//div[contains(@class, 'option') and text()='{valor}']"
        )))
        opcion.click()

    try:
        with allure.step("1. Navegar a la sección de Ofertas"):
            btn_ofertas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='offers/default.aspx']")))
            driver.execute_script("arguments[0].click();", btn_ofertas)
            wait.until(EC.invisibility_of_element_located((By.ID, "wpreloader_overlay")))

        with allure.step("2. Seleccionar fecha de viaje (7 días en el futuro)"):
            fecha_viaje = datetime.now() + timedelta(days=7)
            dia = str(fecha_viaje.day)
            
            input_fecha = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_txtDateFrom")))
            input_fecha.click()
            
            xpath_dia = f"//div[@class='datepicker-days']//td[not(contains(@class, 'old')) and not(contains(@class, 'new')) and text()='{dia}']"
            dia_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dia)))
            dia_element.click()

            body = driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element(body).click().perform()

        with allure.step("3, 4 y 5. Configurar pasajeros"):
            seleccionar_en_tomselect("ddAdults", "2")
            seleccionar_en_tomselect("ddChildren", "0")
            seleccionar_en_tomselect("ddInfants", "0")

        with allure.step("6 y 7. Configurar Habitaciones"):
            seleccionar_en_tomselect("ddRooms", "1")
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_btnApplyParams"))).click()

        with allure.step("8 y 9. Ejecutar Búsqueda y esperar resultados"):
            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_btnSearch")))
            btn_buscar.click()
            wait.until(EC.invisibility_of_element_located((By.ID, "wpreloader_overlay")))
            time.sleep(2) 

            allure.attach(driver.get_screenshot_as_png(), name="1_Resultados_Cargados", attachment_type=allure.attachment_type.PNG)

        with allure.step("10 y 11. Recorrer todos los días del itinerario y validar Hoteles, Servicios y Opcionales"):
            botones_acordeon = wait.until(EC.presence_of_all_elements_located((
                By.XPATH, "//div[@class='panel-group']//h4[@class='panel-title']/a[not(contains(., 'Resumen de precios'))]"
            )))

            for index, btn in enumerate(botones_acordeon):
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                
                if "collapsed" in btn.get_attribute("class") or btn.get_attribute("aria-expanded") == "false":
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                
                panel_content = btn.find_element(By.XPATH, "../../following-sibling::div[contains(@class, 'panel-collapse')]")
                
                try:
                    acc_content = panel_content.find_element(By.CSS_SELECTOR, "div.accordion-content")
                except:
                    acc_content = panel_content
                    
                h4_internos = acc_content.find_elements(By.TAG_NAME, "h4")
                textos_h4 = [h.text.strip() for h in h4_internos]
                
                if "Hoteles" in textos_h4:
                    assert len(acc_content.find_elements(By.CSS_SELECTOR, "h6.h6style")) > 0, f"Día {index+1}: Falta el h6 del hotel."
                    assert len(acc_content.find_elements(By.TAG_NAME, "img")) > 0, f"Día {index+1}: No se renderizó la imagen del hotel."
                    assert len(acc_content.find_elements(By.XPATH, ".//*[contains(@class, 'fa-map-marker')] | .//a[contains(translate(., 'MAPA', 'mapa'))]")) > 0, f"Día {index+1}: Falta el enlace o icono del mapa."
                    
                if "Servicios" in textos_h4:
                    elementos_servicio = acc_content.find_elements(By.XPATH, ".//h4[contains(text(), 'Servicios')]/following-sibling::*[1]")
                    assert len(elementos_servicio) > 0, f"Día {index+1}: El h4 'Servicios' existe pero no tiene contenido debajo."
                    
                if "Servicios opcionales" in textos_h4:
                    elementos_opcionales = acc_content.find_elements(By.XPATH, ".//h4[contains(text(), 'Servicios opcionales')]/following-sibling::*[1]")
                    assert len(elementos_opcionales) > 0, f"Día {index+1}: El h4 'Servicios opcionales' existe pero no tiene contenido debajo."

        with allure.step("12. Desplegar y validar contenido de 'Resumen de precios'"):
            btn_resumen = wait.until(EC.presence_of_element_located((
                By.XPATH, "//h4[@class='panel-title']/a[contains(., 'Resumen de precios')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_resumen)
            time.sleep(0.5)
            
            if "collapsed" in btn_resumen.get_attribute("class") or btn_resumen.get_attribute("aria-expanded") == "false":
                driver.execute_script("arguments[0].click();", btn_resumen)
                time.sleep(1)
                
            panel_resumen = btn_resumen.find_element(By.XPATH, "../../following-sibling::div[contains(@class, 'panel-collapse')]")
            
            tablas_resumen = panel_resumen.find_elements(By.TAG_NAME, "table")
            assert len(tablas_resumen) > 0, "Error crítico: No se encontró la <table> dentro del Resumen de precios."
            
            filas_resumen = tablas_resumen[0].find_elements(By.TAG_NAME, "tr")
            assert len(filas_resumen) > 1, "La tabla de Resumen de precios se renderizó vacía."
            
            celdas_resumen = tablas_resumen[0].find_elements(By.XPATH, ".//td | .//th")
            assert len(celdas_resumen) > 0, "Las filas de la tabla de Resumen de precios no contienen datos."

        with allure.step("13 y 14. Avanzar al paso final y validar tabla general"):
            btn_siguiente = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lnkNext")))
            driver.execute_script("arguments[0].click();", btn_siguiente)
            
            wait.until(
                lambda d: any(tabla.is_displayed() for tabla in d.find_elements(By.CSS_SELECTOR, "table.table.table-bordered.table-striped")),
                message="Validación fallida: Ninguna tabla de resumen final se hizo visible en la última pantalla."
            )
            time.sleep(1)

        # =========================
        # NUEVO BLOQUE: CARRITO
        # =========================
        with allure.step("15 y 16. Sumar al Carrito de compras y validar éxito"):
            # Buscar el botón de agregar al carrito (XPath amplio para atajar distintas nomenclaturas)
            btn_agregar_carrito = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@id, 'btnAddCart')] | //button[contains(translate(., 'CARRITO', 'carrito'), 'carrito')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_agregar_carrito)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn_agregar_carrito)

            # Esperamos que desaparezca el preloader si lo hay
            wait.until(EC.invisibility_of_element_located((By.ID, "wpreloader_overlay")))

            # VALIDACIÓN: Buscamos un mensaje de éxito, un modal, o validamos que la URL haya cambiado al checkout
            # Esto usa un selector amplio buscando mensajes típicos de Bootstrap o de la app
            mensaje_exito = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//*[contains(@class, 'alert-success') or contains(@class, 'toast') or contains(translate(text(), 'ÉXITO', 'éxito'), 'éxito') or contains(@id, 'cart-badge')]"
            )))
            
            assert mensaje_exito.is_displayed(), "El producto no se agregó al carrito o no se mostró el mensaje de confirmación."

            # Captura final del triunfo E2E
            allure.attach(driver.get_screenshot_as_png(), name="5_Agregado_Al_Carrito", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Ofertas", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
