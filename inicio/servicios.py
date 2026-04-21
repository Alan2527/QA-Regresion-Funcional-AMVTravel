import pytest
import allure
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Reservar Servicios")
@allure.story("Búsqueda, filtrado y reserva de excursión en Bariloche")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo End-to-End (E2E) de la reserva de un servicio:
1. Login silencioso y navegación a la pestaña de Servicios.
2. Búsqueda filtrada por Destino (Bariloche) y Tipo (Excursión).
3. Validación de la interfaz (UI) en las cards de resultados y el detalle interno.
4. Selección de cantidad de pasajeros.
5. Confirmación de reserva y validación final comprobando que el carrito sume 4 ítems.
6. Flujo de Finalización de Compra (Checkout) y carga de datos del pasajero.
""")
def test_reserva_servicio_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver) # Aseguramos que actions esté disponible

    # =========================================================================
    # PASOS ORIGINALES (MANTENIDOS SIN CAMBIOS)
    # =========================================================================
    with allure.step("1 a 5. Seleccionar pestaña Servicios, ingresar destino, tipo y buscar"):
        try:
            tab_servicios = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabServices']")), message="No se encontró la pestaña a[href='#tabServices']")
            tab_servicios.click()
            time.sleep(1)

            input_destino = wait.until(EC.presence_of_element_located((By.ID, "txtDestinationService")), message="No se encontró el input de Destino de Servicio")
            input_destino.clear()
            input_destino.send_keys("Bariloche")
            time.sleep(2)

            option_destino = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'San Carlos de Bariloche, Río Negro, Argentina')]")), message="No se desplegó la opción de Bariloche")
            option_destino.click()
            time.sleep(1)

            select_tipo_elem = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlSearchService_ddlServiceType")), message="No se encontró el select de Tipo de Servicio")
            select_tipo = Select(select_tipo_elem)
            select_tipo.select_by_visible_text("Excursión")

            allure.attach(driver.get_screenshot_as_png(), name="Tab_Destino_Servicios", attachment_type=allure.attachment_type.PNG)

            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlSearchService_lnkSearch")), message="No se encontró el botón de búsqueda")
            btn_buscar.click()
            time.sleep(3)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_Busqueda", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en la búsqueda inicial. Detalle: {str(e)}")

    with allure.step("6. Seleccionar pasajeros y agregar al carrito"):
        try:
            btn_detalles = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-view-details-service")), message="No se encontró el botón 'Ver Detalles' en los resultados")
            btn_detalles.click()
            time.sleep(2)

            input_pax = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id*='txtPaxQuantity']")), message="No se encontró el campo de cantidad de pasajeros")
            input_pax.clear()
            input_pax.send_keys("4")

            allure.attach(driver.get_screenshot_as_png(), name="Detalles_Servicio_Pax", attachment_type=allure.attachment_type.PNG)

            btn_carrito = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id*='lnkAddCart']")), message="No se encontró el botón de agregar al carrito")
            btn_carrito.click()
            time.sleep(2)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_Detalle", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al seleccionar pasajeros o agregar al carrito. Detalle: {str(e)}")

    with allure.step("7. Confirmar reserva y validar incremento en el carrito"):
        try:
            initial_cart_text = driver.find_element(By.ID, "lblCartCount").text.strip()
            initial_cart_count = int(initial_cart_text) if initial_cart_text.isdigit() else 0
            expected_count = initial_cart_count + 4

            btn_reservar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_lnkBookService")), message="No se encontró el botón de Reservar Servicio")
            btn_reservar.click()

            try:
                alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert.accept()
            except:
                pass 

            wait.until(
                lambda d: int(d.find_element(By.ID, "lblCartCount").text.strip() or 0) == expected_count,
                message=f"La reserva falló: El carrito no se actualizó al valor esperado ({expected_count})"
            )
            
            allure.attach(driver.get_screenshot_as_png(), name="Reserva_Exitosa_Carrito_Actualizado", attachment_type=allure.attachment_type.PNG)
            
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Carrito", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo la validación final del carrito. Detalle: {str(e)}")

    # =========================================================================
    # NUEVOS PASOS (CHECKOUT Y FINALIZACIÓN)
    # =========================================================================

    with allure.step("8. Desplegar carrito y clickear Finalizar"):
        cart_anchor = wait.until(EC.visibility_of_element_located((By.ID, "AncoreShoppingCart")))
        actions.move_to_element(cart_anchor).perform()
        time.sleep(1)
        
        btn_finalizar = wait.until(EC.element_to_be_clickable((By.ID, "btnFinalizar")))
        allure.attach(driver.get_screenshot_as_png(), name="8_Carrito_Desplegado", attachment_type=allure.attachment_type.PNG)
        btn_finalizar.click()

    with allure.step("9. Completar Referencia y Comentarios"):
        # Validar tabla
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
        
        # Completar Referencia
        driver.find_element(By.NAME, "ctl00$cphMain$txtReference").send_keys("Test Automático")
        
        # Comentario con fecha dinámica
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        msg = f"Este es un test autómatico ejecutado el día {fecha_actual}"
        driver.find_element(By.NAME, "ctl00$cphMain$txtComment").send_keys(msg)
        
        allure.attach(driver.get_screenshot_as_png(), name="9_Referencia_y_Comentarios", attachment_type=allure.attachment_type.PNG)
        
        # Click en Continuar (btn success apreload)
        driver.find_element(By.CSS_SELECTOR, "a.btn.btn-success.apreload").click()

    with allure.step("10. Cargar Datos de Pasajeros y Comentarios de Servicio"):
        # Validar tabla cargada
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
        
        # Comentarios por servicio
        driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl0$ctrlBookingServiceDetailControl$txtDetail").send_keys("Comentario 1")
        driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl1$ctrlBookingServiceDetailControl$txtDetail").send_keys("Comentario 2")
        
        # Datos Pasajero Alan QA
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtName").send_keys("Alan")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtSurName").send_keys("QA")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtPassport").send_keys("PAS123456789")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtBirthday").send_keys("02061990")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtNationality").send_keys("Argentino")
        
        # Pax Quantity y Términos
        pax_q = driver.find_element(By.ID, "ctl00_cphMain_txtPaxQuantity")
        pax_q.clear()
        pax_q.send_keys("2")
        
        checkbox = driver.find_element(By.ID, "ctl00_cphMain_cbxTermsAndConditions")
        if not checkbox.is_selected():
            checkbox.click()
            
        allure.attach(driver.get_screenshot_as_png(), name="10_Carga_Pasajeros_Final", attachment_type=allure.attachment_type.PNG)
        
        # Guardar Reserva
        driver.find_element(By.ID, "ctl00_cphMain_btnSaveBook").click()

    with allure.step("11. Validar Éxito de Reserva"):
        # Esperar y validar tablas de confirmación
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
        wait.until(EC.presence_of_element_located((By.ID, "tableTab2")))
        
        allure.attach(driver.get_screenshot_as_png(), name="11_Reserva_Finalizada_OK", attachment_type=allure.attachment_type.PNG)
