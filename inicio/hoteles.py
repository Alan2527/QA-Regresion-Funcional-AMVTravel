import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Reservar Hoteles")
@allure.story("Búsqueda, filtrado y reserva de hotel en Bariloche")
def test_reserva_hotel_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    with allure.step("1 a 3. Seleccionar pestaña Hoteles, ingresar destino y fechas"):
        try:
            # 1. Click en la pestaña de Hoteles
            tab_hoteles = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabHotels']")), message="No se encontró la pestaña a[href='#tabHotels']")
            tab_hoteles.click()
            time.sleep(1) 

            # 2. Destino (Manejo de Autocompletado)
            input_destino = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_ctrlHotelSearchControl_searchDestination")), message="No se encontró el input de Destino")
            input_destino.clear()
            # Escribimos solo una parte para disparar el buscador predictivo
            input_destino.send_keys("Bariloche")

            # Esperamos a que la lista desplegable muestre la opción correcta y la clickeamos
            opcion_destino = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Bariloche, Argentina')]")), message="No se desplegó la opción 'Bariloche, Argentina' en el autocompletado")
            opcion_destino.click()
            time.sleep(1) 

            # 3. Calendario
            input_calendario = driver.find_element(By.ID, "txtCalendar")
            input_calendario.clear()
            input_calendario.send_keys("03/03/2026 - 10/03/2026")
            
            allure.attach(driver.get_screenshot_as_png(), name="Tab_Destino_y_Fechas", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_1_a_3", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al ingresar destino o fechas. Detalle: {str(e)}")

    with allure.step("4 a 9. Configurar habitaciones y pasajeros"):
        try:
            # 4. Hover para abrir el dropdown de pasajeros
            btn_pasajeros = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'pink-btn') and contains(@class, 'passengerQuantity-botton')]")), message="No se encontró el botón de pasajeros")
            actions.move_to_element(btn_pasajeros).perform()
            time.sleep(1) 

            # 5. Sumar 2 habitaciones
            btn_rooms = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"QuantityModify(+1,'rooms')\"]")), message="No se encontró el botón para sumar habitaciones")
            actions.double_click(btn_rooms).perform()

            # 6. Sumar 2 adultos
            btn_adults = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"QuantityModify(1,'adults')\"]")), message="No se encontró el botón para sumar adultos")
            actions.double_click(btn_adults).perform()

            # 7. Sumar 2 menores
            btn_children = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"ChildrenModify(true)\"]")), message="No se encontró el botón para sumar menores")
            actions.double_click(btn_children).perform()
            time.sleep(1) 

            # 8. Edad menor 1
            select_edad1 = Select(driver.find_element(By.ID, "childrenAge1"))
            select_edad1.select_by_visible_text("9")

            # 9. Edad menor 2
            actions.move_to_element(btn_pasajeros).perform()
            time.sleep(0.5)
            select_edad2 = Select(driver.find_element(By.ID, "childrenAge2"))
            select_edad2.select_by_visible_text("11")
            
            allure.attach(driver.get_screenshot_as_png(), name="Configuracion_Pasajeros", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_4_a_9", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al configurar los pasajeros. Detalle: {str(e)}")

    with allure.step("10. Ejecutar Búsqueda y esperar resultados"):
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "btnSearch")), message="No se encontró el botón de Búsqueda").click()
            
            wait_largo = WebDriverWait(driver, 45)
            wait_largo.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Disponibilidad']")), message="La búsqueda superó los 45 segundos y no cargaron los filtros")
            time.sleep(2) 
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_10", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al ejecutar la búsqueda. Detalle: {str(e)}")

    with allure.step("11 a 15. Aplicar Filtros laterales"):
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='Disponibilidad']")), message="Filtro Disponibilidad no encontrado").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='Zona Catedral ']")), message="Filtro Zona Catedral no encontrado").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='Apart']")), message="Filtro Apart no encontrado").click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='Aire Acondicionado']")), message="Filtro Aire Acondicionado no encontrado").click()

            btn_aplicar_filtros = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphSideMain_lnkFilter")), message="Botón Aplicar Filtros no encontrado")
            driver.execute_script("arguments[0].click();", btn_aplicar_filtros)
            
            time.sleep(5) 
            allure.attach(driver.get_screenshot_as_png(), name="Filtros_Aplicados", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_11_a_15", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al clickear filtros. Detalle: {str(e)}")

    with allure.step("16. Validar panel de resultados"):
        try:
            panel_resultados = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_updMainPanel")), message="No cargó el panel de resultados principal")
            assert panel_resultados is not None, "El div de resultados no apareció."
            
            allure.attach(driver.get_screenshot_as_png(), name="Panel_Resultados_Validado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_16", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en validación del panel: {str(e)}")

    with allure.step("17. Validar componentes de la Card del Hotel y Ver Más"):
        try:
            assert driver.find_elements(By.CSS_SELECTOR, "img[style*='height: 200px']"), "Falta la imagen de la card"
            assert driver.find_elements(By.CSS_SELECTOR, "div[style*='font-size: 20px'] span"), "Falta el nombre del hotel"
            assert driver.find_elements(By.CSS_SELECTOR, "div.single-car-rating"), "Falta el rating en la card"
            assert driver.find_elements(By.CSS_SELECTOR, "div[style*='color: #6B72F2'] i"), "Falta la zona del hotel"
            assert driver.find_elements(By.CSS_SELECTOR, "div[style*='margin-top: 2px'] p"), "Falta la descripción del hotel"
            assert driver.find_elements(By.CSS_SELECTOR, "div#True.available-hotel"), "Falta indicador de disponibilidad"
            
            caja_precio = driver.find_element(By.CSS_SELECTOR, "div[style*='background-color: #444444']")
            assert "Desde" in caja_precio.text, "Falta el texto 'Desde' en la caja de precio"
            
            allure.attach(driver.get_screenshot_as_png(), name="Card_Hotel_Validada", attachment_type=allure.attachment_type.PNG)
            
            btn_ver_mas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#verMasbtn.btn.pink-btn.apreload")), message="No se encontró el botón 'Ver Más'")
            btn_ver_mas.click()
            time.sleep(3)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_17", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo al validar componentes de la Card. Detalle: {str(e)}")

    with allure.step("18. Validar información en el detalle del hotel"):
        try:
            assert wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.h2name")), message="No cargó el Detalle del Hotel (falta h2name)")
            assert driver.find_elements(By.CSS_SELECTOR, "div.rating.clearfix"), "Falta el rating"
            assert driver.find_elements(By.CSS_SELECTOR, "img.newSlide"), "Faltan las imágenes (newSlide)"
            assert driver.find_elements(By.XPATH, '//*[@id="aspnetForm"]/article/div[1]/div[2]/div[2]/div[4]'), "Falta la descripción principal"
            assert driver.find_elements(By.ID, "ctl00_cphMain_amenitiesList"), "Falta la lista de amenities"
            assert driver.find_elements(By.CSS_SELECTOR, "ul.nav.nav-tabs"), "Faltan los nav-tabs"
            assert driver.find_elements(By.CSS_SELECTOR, "h2.smallh2"), "Falta el nombre de la oferta (smallh2)"
            assert driver.find_elements(By.CSS_SELECTOR, "table.table.table-bordered.table-striped"), "Falta la tabla de precios/habitaciones"
            assert driver.find_elements(By.CSS_SELECTOR, "div.fleft"), "Faltan las políticas de cancelación"

            allure.attach(driver.get_screenshot_as_png(), name="Detalle_Hotel_Validado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_18", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo al validar los componentes internos del hotel. Detalle: {str(e)}")

    with allure.step("19. Sumar habitación"):
        try:
            btn_suma = wait.until(EC.element_to_be_clickable((By.ID, "72260-185813-105-1-2-Integration-26611-suma")), message="No se encontró el botón sumar habitación")
            btn_suma.click()
            time.sleep(1)
            allure.attach(driver.get_screenshot_as_png(), name="Habitacion_Sumada", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_19", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al sumar habitación. Detalle: {str(e)}")

    with allure.step("20 a 22. Validar input y confirmar reserva"):
        try:
            # 20. Validar que el input cambió (no es 0)
            input_cantidad = driver.find_element(By.ID, "185813")
            valor_input = input_cantidad.get_attribute("value")
            assert valor_input != "0", f"El input de cantidad sigue siendo 0. Valor actual: {valor_input}"

            # 21. Click en Guardar
            btn_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@onclick, 'Guardar(185813')]")), message="No se encontró el botón de Guardar Reserva")
            btn_guardar.click()

            # 22. Validar Alert y buscar errores
            alert = wait.until(EC.alert_is_present(), message="No apareció ningún alert de confirmación de reserva")
            texto_alert_original = alert.text
            texto_alert = texto_alert_original.lower()
            allure.attach(texto_alert_original, name="Texto_del_Alert", attachment_type=allure.attachment_type.TEXT)
            
            # Aceptamos el alert real para desbloquear el navegador
            alert.accept() 
            
            # --- INYECCIÓN JS (Truco para fotografiar el Alert) ---
            js_script = """
            var alertDiv = document.createElement('div');
            alertDiv.style.position = 'fixed';
            alertDiv.style.top = '20px';
            alertDiv.style.left = '50%';
            alertDiv.style.transform = 'translateX(-50%)';
            alertDiv.style.backgroundColor = '#f8f9fa';
            alertDiv.style.border = '1px solid #dee2e6';
            alertDiv.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
            alertDiv.style.padding = '20px';
            alertDiv.style.zIndex = '999999';
            alertDiv.style.fontFamily = 'system-ui, -apple-system, sans-serif';
            alertDiv.style.fontSize = '14px';
            alertDiv.style.color = '#212529';
            alertDiv.style.borderRadius = '0.25rem';
            alertDiv.style.minWidth = '300px';
            alertDiv.style.textAlign = 'center';
            alertDiv.innerHTML = '<strong>Mensaje del Sistema:</strong><br><br>' + arguments[0];
            document.body.appendChild(alertDiv);
            """
            driver.execute_script(js_script, texto_alert_original)
            time.sleep(1) # Damos tiempo a que se dibuje en pantalla
            # --------------------------------------------------------

            if "error" in texto_alert:
                allure.attach(driver.get_screenshot_as_png(), name="Error_En_Reserva", attachment_type=allure.attachment_type.PNG)
                pytest.fail(f"La reserva falló. El alert contiene un error: {texto_alert_original}")
            
            allure.attach(driver.get_screenshot_as_png(), name="Confirmacion_Exitosa", attachment_type=allure.attachment_type.PNG)
            
        except Exception as e:
            # Bloque de seguridad por si falla antes del alert
            try:
                driver.switch_to.alert.accept() 
            except:
                pass
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_20_a_22", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en la confirmación final de la reserva. Detalle: {str(e)}")
