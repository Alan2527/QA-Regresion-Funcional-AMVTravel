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
@allure.description("""
Este caso de prueba cubre el flujo End-to-End (E2E) completo de la reserva de un servicio:
1. Login y navegación a Servicios.
2. Búsqueda y filtrado en Bariloche.
3. Confirmación de reserva y validación de incremento en carrito.
4. Finalización de reserva (Checkout).
5. Carga de datos de referencia, comentarios y datos del pasajero (Alan QA).
6. Confirmación final y validación de tablas de éxito.
""")
def test_reserva_servicio_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    # --- FLUJO ORIGINAL DE BÚSQUEDA Y SELECCIÓN ---
    with allure.step("1 a 5. Seleccionar pestaña Servicios, ingresar destino, tipo y buscar"):
        try:
            tab_servicios = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabServices']")))
            tab_servicios.click()

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
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Busqueda_Inicial", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en la búsqueda: {str(e)}")

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
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Confirmacion_Carrito", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo la validación del carrito: {str(e)}")

    # --- NUEVOS PASOS SOLICITADOS ---

    with allure.step("8. Ir al carrito y Finalizar"):
        try:
            cart_anchor = wait.until(EC.visibility_of_element_located((By.ID, "AncoreShoppingCart")))
            actions.move_to_element(cart_anchor).perform()
            time.sleep(1)
            
            btn_finalizar = wait.until(EC.element_to_be_clickable((By.ID, "btnFinalizar")))
            allure.attach(driver.get_screenshot_as_png(), name="8_Dropdown_Carrito", attachment_type=allure.attachment_type.PNG)
            btn_finalizar.click()
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Ir_A_Finalizar", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al clickear Finalizar: {str(e)}")

    with allure.step("9. Completar Referencia y Comentarios"):
        try:
            # Validar existencia de tabla
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
            
            # Completar Referencia
            input_ref = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMain$txtReference")))
            input_ref.send_keys("Test Automático")
            
            # Completar Comentario con fecha dinámica
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            textarea_comment = driver.find_element(By.NAME, "ctl00$cphMain$txtComment")
            textarea_comment.send_keys(f"Este es un test autómatico ejecutado el día {fecha_actual}")
            
            allure.attach(driver.get_screenshot_as_png(), name="9_Referencia_Comentarios", attachment_type=allure.attachment_type.PNG)
            
            # Click en botón success apreload
            btn_success = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "apreload")))
            btn_success.click()
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Referencia_Comentarios", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en referencia/comentarios: {str(e)}")

    with allure.step("10. Cargar Comentarios de Servicio y Datos de Pasajeros"):
        try:
            # Validar tabla nuevamente
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
            
            # Comentarios específicos
            input_coment1 = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMain$lvBooking$ctrl0$ctrlBookingServiceDetailControl$txtDetail")))
            input_coment1.send_keys("Comentario 1")
            
            input_coment2 = driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl1$ctrlBookingServiceDetailControl$txtDetail")
            input_coment2.send_keys("Comentario 2")
            
            # Datos del Pasajero
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtName").send_keys("Alan")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtSurName").send_keys("QA")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtPassport").send_keys("PAS123456789")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtBirthday").send_keys("02061990")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtNationality").send_keys("Argentino")
            
            # Cantidad de pax y Checkbox
            input_pax_final = driver.find_element(By.ID, "ctl00_cphMain_txtPaxQuantity")
            input_pax_final.clear()
            input_pax_final.send_keys("2")
            
            check_terms = driver.find_element(By.ID, "ctl00_cphMain_cbxTermsAndConditions")
            if not check_terms.is_selected():
                check_terms.click()
            
            allure.attach(driver.get_screenshot_as_png(), name="10_Datos_Pasajeros_Completos", attachment_type=allure.attachment_type.PNG)
            
            # Click en Save Book
            btn_save = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_btnSaveBook")))
            btn_save.click()
            
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Carga_Pasajeros", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al cargar datos del pasajero: {str(e)}")

    with allure.step("11. Validación Final de Reserva"):
        try:
            # Validar existencia de ambas tablas
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-striped")))
            wait.until(EC.presence_of_element_located((By.ID, "tableTab2")))
            
            allure.attach(driver.get_screenshot_as_png(), name="11_Reserva_Finalizada_Exito", attachment_type=allure.attachment_type.PNG)
            
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Final", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"La reserva no se confirmó correctamente: {str(e)}")
