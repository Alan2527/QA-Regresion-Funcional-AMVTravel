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
@allure.story("Búsqueda, filtrado y reserva completa de excursión")
@allure.severity(allure.severity_level.CRITICAL)
def test_reserva_servicio_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    # =========================================================================
    # PASOS ORIGINALES (NO TOCAR)
    # =========================================================================
    with allure.step("1 a 5. Seleccionar pestaña Servicios, ingresar destino, tipo y buscar"):
        try:
            tab_servicios = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabServices']")), message="No se encontró la pestaña a[href='#tabServices']")
            tab_servicios.click()
            
            # Revertido a tu lógica original de ID
            input_destino = wait.until(EC.presence_of_element_located((By.ID, "txtDestinationService")))
            input_destino.send_keys("San Carlos de Bariloche, Río Negro, Argentina")
            time.sleep(2)

            option_destino = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-menu-item div")))
            option_destino.click()

            select_tipo_elem = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlSearchService_ddlServiceType")))
            select_tipo = Select(select_tipo_elem)
            select_tipo.select_by_visible_text("Excursión")

            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlSearchService_lnkSearch")))
            btn_buscar.click()
            time.sleep(3)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Busqueda_Original", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en la búsqueda original: {str(e)}")

    with allure.step("6. Seleccionar pasajeros y agregar al carrito"):
        try:
            btn_detalles = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-view-details-service")))
            btn_detalles.click()

            input_pax = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id*='txtPaxQuantity']")))
            input_pax.clear()
            input_pax.send_keys("4")

            btn_carrito = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id*='lnkAddCart']")))
            btn_carrito.click()
            time.sleep(2)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Seleccion_Pax", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al agregar al carrito: {str(e)}")

    with allure.step("7. Confirmar reserva y validar incremento en el carrito"):
        try:
            initial_cart_text = driver.find_element(By.ID, "lblCartCount").text.strip()
            initial_cart_count = int(initial_cart_text) if initial_cart_text.isdigit() else 0
            expected_count = initial_cart_count + 4

            btn_reservar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_lnkBookService")))
            btn_reservar.click()

            try:
                alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert.accept()
            except:
                pass

            wait.until(lambda d: int(d.find_element(By.ID, "lblCartCount").text.strip() or 0) == expected_count)
            allure.attach(driver.get_screenshot_as_png(), name="7_Carrito_Actualizado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Carrito", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo la validación del carrito: {str(e)}")

    # =========================================================================
    # NUEVOS PASOS SOLICITADOS (CHECKOUT Y FINALIZACIÓN)
    # =========================================================================
    
    with allure.step("8. Ir al carrito y Finalizar"):
        cart_anchor = wait.until(EC.visibility_of_element_located((By.ID, "AncoreShoppingCart")))
        actions.move_to_element(cart_anchor).perform()
        time.sleep(1)
        
        btn_finalizar = wait.until(EC.element_to_be_clickable((By.ID, "btnFinalizar")))
        allure.attach(driver.get_screenshot_as_png(), name="8_Carrito_Desplegado", attachment_type=allure.attachment_type.PNG)
        btn_finalizar.click()

    with allure.step("9. Validar tabla y completar Referencia/Comentarios"):
        # Validar tabla
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")))
        
        # Referencia
        driver.find_element(By.NAME, "ctl00$cphMain$txtReference").send_keys("Test Automático")
        
        # Comentario con fecha dinámica
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        msg = f"Este es un test autómatico ejecutado el día {fecha_actual}"
        driver.find_element(By.NAME, "ctl00$cphMain$txtComment").send_keys(msg)
        
        allure.attach(driver.get_screenshot_as_png(), name="9_Checkout_Paso_1", attachment_type=allure.attachment_type.PNG)
        
        # Click en botón success apreload
        driver.find_element(By.CSS_SELECTOR, "a.btn.btn-success.apreload").click()

    with allure.step("10. Cargar comentarios de servicio y Datos de Pasajero"):
        # Validar tabla nuevamente
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")))
        
        # Comentarios por servicio
        driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl0$ctrlBookingServiceDetailControl$txtDetail").send_keys("Comentario 1")
        driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl1$ctrlBookingServiceDetailControl$txtDetail").send_keys("Comentario 2")
        
        # Datos del Pasajero Alan QA
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtName").send_keys("Alan")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtSurName").send_keys("QA")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtPassport").send_keys("PAS123456789")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtBirthday").send_keys("02061990")
        driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtNationality").send_keys("Argentino")
        
        # Cantidad de Pax y Términos
        driver.find_element(By.ID, "ctl00_cphMain_txtPaxQuantity").clear()
        driver.find_element(By.ID, "ctl00_cphMain_txtPaxQuantity").send_keys("2")
        
        checkbox = driver.find_element(By.ID, "ctl00_cphMain_cbxTermsAndConditions")
        if not checkbox.is_selected():
            checkbox.click()
            
        allure.attach(driver.get_screenshot_as_png(), name="10_Datos_Pasajero", attachment_type=allure.attachment_type.PNG)
        
        # Guardar reserva
        driver.find_element(By.ID, "ctl00_cphMain_btnSaveBook").click()

    with allure.step("11. Validación final de éxito"):
        # Validar las dos tablas finales
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")))
        wait.until(EC.presence_of_element_located((By.ID, "tableTab2")))
        
        allure.attach(driver.get_screenshot_as_png(), name="11_Reserva_Finalizada", attachment_type=allure.attachment_type.PNG)
