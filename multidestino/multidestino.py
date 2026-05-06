import pytest
import allure
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Multidestinos")
@allure.story("Flujo completo de Reserva Multidestino (Triángulo Argentino)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo End-to-End de un paquete Multidestino:
1. Búsqueda de 'Triángulo Argentino'.
2. Selección de fechas, pasajeros y distribución de habitaciones.
3. Personalización del itinerario (Quitar y Agregar servicios opcionales).
4. Cambio de idioma de un servicio y validación de recargo en el precio.
5. Carga de datos de vuelo, pasajeros y confirmación de la reserva.
6. Validación en tabla de reservas.
""")
def test_reserva_multidestino(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    # Función auxiliar para esperar que desaparezcan los modales de carga
    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loader') or contains(@class, 'spinner') or @id='UpdateProgress1']"
            )))
            time.sleep(1) # Breve pausa estabilizadora
        except:
            pass

    try:
        # ==========================================
        # 1-2. NAVEGACIÓN A MULTIDESTINOS
        # ==========================================
        with allure.step("1 y 2. Navegar a la sección de Multidestinos"):
            btn_multidestino = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/online/tourall.aspx?country=10&city=5000&tour=0&resident=false']")))
            driver.execute_script("arguments[0].click();", btn_multidestino)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Pantalla_Multidestinos", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 3-4. BÚSQUEDA DEL PAQUETE
        # ==========================================
        with allure.step("3 y 4. Buscar 'Triángulo Argentino (8 días / 7 noches)'"):
            input_buscador = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Buscador de paquetes']")))
            input_buscador.clear()
            input_buscador.send_keys("Triángulo Argentino (8 días / 7 noches)")
            time.sleep(1)
            
            btn_buscar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pink-btn")))
            driver.execute_script("arguments[0].click();", btn_buscar)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="2_Resultados_Busqueda", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 5. VALIDACIÓN DEL RESULTADO
        # ==========================================
        with allure.step("5. Validar estructura del resultado de búsqueda"):
            card = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.customize-card")))
            img_view = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.customize-image-view")))
            details_left = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tours-details-content-left")))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
            
            assert card.is_displayed() and img_view.is_displayed() and details_left.is_displayed(), "No se encontraron los elementos de la tarjeta de resultado."
            allure.attach(driver.get_screenshot_as_png(), name="3_Validacion_Tarjeta", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 6. ENTRAR A COTIZACIÓN
        # ==========================================
        with allure.step("6. Clic en el botón para cotizar"):
            btn_cotizar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.update-cart-btn.apreload.pink-btn.custom-tourall-cotization")))
            driver.execute_script("arguments[0].click();", btn_cotizar)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="4_Pantalla_Cotizacion", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 7. CONFIGURACIÓN DE FECHA Y PASAJEROS
        # ==========================================
        with allure.step("7. Configurar Fecha (Hoy + 7 días) y Pasajeros"):
            # Calculamos la fecha
            fecha_futura = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
            
            # Ingresamos fecha usando JS para evitar bloqueos del datepicker
            input_fecha = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.coustomtour-form-date")))
            driver.execute_script(f"arguments[0].value = '{fecha_futura}';", input_fecha)
            # Forzamos el evento change por si dispara lógica AJAX
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", input_fecha)
            time.sleep(1)

            # Seleccionamos pax y distribución
            Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_ddPax")))).select_by_value("6")
            time.sleep(1)
            Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_ddSGL")))).select_by_value("1")
            Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_ddDBL")))).select_by_value("1")
            # Usamos CSS con finalización por si el ID tiene prefijos del asp.net
            Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id$='ddTPL']")))).select_by_value("1")
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Configuracion_Pasajeros", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 8. RECALCULAR / CONTINUAR
        # ==========================================
        with allure.step("8. Clic en botón rosa para calcular/continuar"):
            btn_calcular = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pink-btn.apreload")))
            driver.execute_script("arguments[0].click();", btn_calcular)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="6_Itinerario_Generado", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 9. QUITAR SERVICIOS "NO DISPONIBLE" (DINÁMICO)
        # ==========================================
        with allure.step("9. Quitar dinámicamente todos los servicios 'No disponible'"):
            # Usamos un mecanismo de seguridad para evitar un bucle infinito si algo falla en el clic
            intentos_maximos = 15 
            intentos = 0
            
            while intentos < intentos_maximos:
                # 1. Buscamos todos los H6 que tengan el texto "No disponible" (case-insensitive por seguridad)
                xpath_no_disp = "//h6[contains(@class, 'serviceTotalh6') and contains(translate(text(), 'NO DISPONIBLE', 'no disponible'), 'no disponible')]"
                servicios_no_disp = driver.find_elements(By.XPATH, xpath_no_disp)
                
                # Si la lista está vacía, significa que ya no quedan servicios no disponibles. ¡Salimos del bucle!
                if len(servicios_no_disp) == 0:
                    break
                
                # 2. Tomamos el PRIMERO de la lista actual
                h6_element = servicios_no_disp[0]
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", h6_element)
                
                # 3. Magia de XPath: Desde el h6, subimos por el HTML (ancestor) hasta encontrar el 
                # primer contenedor padre que tenga el botón de eliminar (lnkRemove), y agarramos ese botón.
                xpath_btn_remove = "./ancestor::*[.//a[contains(@id, 'lnkRemove')]][1]//a[contains(@id, 'lnkRemove')]"
                btn_remove = h6_element.find_element(By.XPATH, xpath_btn_remove)
                
                # 4. Clickeamos el botón de eliminar
                wait.until(EC.element_to_be_clickable(btn_remove))
                driver.execute_script("arguments[0].click();", btn_remove)
                
                # 5. Esperamos que el UpdatePanel (AJAX) termine de cargar
                esperar_fin_de_carga()
                time.sleep(1)  # Pequeña pausa estabilizadora del DOM
                
                intentos += 1
            
            # Validación de seguridad por si el bucle iteró demasiadas veces sin éxito
            assert intentos < intentos_maximos, "Se alcanzó el límite de intentos borrando servicios. El script se detuvo para evitar un bucle infinito."
            
            allure.attach(driver.get_screenshot_as_png(), name="7_Servicios_No_Disponibles_Quitados", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 10. AGREGAR SERVICIO OPCIONAL
        # ==========================================
        with allure.step("10. Agregar servicio opcional (Delta Premium)"):
            btn_add = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lvDestinations_ctrl0_lvServicesAdd_ctrl0_lnkAddServiceDefinitivo")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_add)
            driver.execute_script("arguments[0].click();", btn_add)
            esperar_fin_de_carga()

            # Validar que apareció en la tabla
            tabla_servicios = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="updData"]/div[4]/div[6]/table')))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tabla_servicios)
            assert "Delta Premium » Excursión" in tabla_servicios.text, "El servicio opcional no se agregó correctamente a la tabla."
            
            allure.attach(driver.get_screenshot_as_png(), name="8_Servicio_Agregado", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 11. CAMBIAR IDIOMA Y VALIDAR RECARGO (USD 672 -> USD 804)
        # ==========================================
        with allure.step("11. Cambiar idioma a Inglés y validar recargo de precio"):
            # Validamos el precio inicial (672)
            h6_precio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h6.h6style.serviceTotalh6")))
            precio_inicial = h6_precio.text
            assert "672" in precio_inicial, f"El precio inicial esperado era USD 672, pero se encontró: {precio_inicial}"

            # Cambiamos idioma a Inglés (Texto visible)
            select_idioma = Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_lvDestinations_ctrl0_lvServices_ctrl0_ddServiceLanguage"))))
            select_idioma.select_by_visible_text("Inglés")
            esperar_fin_de_carga()

            # Validamos el recargo por idioma (804)
            h6_precio_actualizado = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h6.h6style.serviceTotalh6")))
            precio_final = h6_precio_actualizado.text
            assert "804" in precio_final, f"El precio no se actualizó correctamente tras aplicar el recargo de idioma. Actual: {precio_final}"
            
            allure.attach(driver.get_screenshot_as_png(), name="9_Recargo_Idioma_Aplicado", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 12-13. INICIAR RESERVA
        # ==========================================
        with allure.step("12 y 13. Clic en Reservar y esperar pantalla"):
            btn_reservar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_lvTotales_ctrl0_lnkReservar")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_reservar)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_reservar)
            esperar_fin_de_carga()
            
            # Validamos que llegamos a la pantalla de reserva (ej: buscando un elemento clásico de esa vista)
            wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMain$btnSaveBook")))
            allure.attach(driver.get_screenshot_as_png(), name="10_Pantalla_Reserva", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 14. DATOS DEL VUELO
        # ==========================================
        with allure.step("14. Llenar datos de vuelo y observaciones"):
            dia_hoy = datetime.now().strftime("%d")
            
            input_vuelo = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$cphMain$lvDestinations$ctrl0$lvServices$ctrl1$txtNumFlightData")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_vuelo)
            input_vuelo.send_keys(f"TEST{dia_hoy}")

            input_hora = driver.find_element(By.NAME, "ctl00$cphMain$lvDestinations$ctrl0$lvServices$ctrl1$txtDepartureTimeData")
            input_hora.send_keys("10:30")

            input_obs = driver.find_element(By.NAME, "ctl00$cphMain$lvDestinations$ctrl0$lvServices$ctrl1$txtCommentData")
            input_obs.send_keys("Test automático")
            
            allure.attach(driver.get_screenshot_as_png(), name="11_Datos_Vuelo", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 15. DATOS PASAJEROS Y TÉRMINOS
        # ==========================================
        with allure.step("15. Llenar datos de pasajero y aceptar términos"):
            input_nombre = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$cphMain$lvPassengersData$ctrl0$txtName")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_nombre)
            input_nombre.send_keys("Alan")

            input_apellido = driver.find_element(By.NAME, "ctl00$cphMain$lvPassengersData$ctrl0$txtSurname")
            input_apellido.send_keys("Test Automático")

            # Checkbox T&C
            chk_terminos = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_cbxTermsAndConditions")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chk_terminos)
            driver.execute_script("arguments[0].click();", chk_terminos)
            
            allure.attach(driver.get_screenshot_as_png(), name="12_Datos_Pasajero_TyC", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 16-17. CONFIRMACIÓN Y VALIDACIÓN FINAL
        # ==========================================
        with allure.step("16 y 17. Guardar reserva y validar creación exitosa en tabla"):
            btn_save = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMain$btnSaveBook")))
            driver.execute_script("arguments[0].click();", btn_save)
            esperar_fin_de_carga()

            # Validar en la tabla de resultados/reservas buscando el <p> dentro del <td>
            xpath_pasajero = "//table[@id='tableTab2']//tbody//tr//td[contains(@class, 'center')]/p[contains(text(), 'Alan Test Automático')]"
            
            elemento_pasajero = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_pasajero)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elemento_pasajero)
            
            assert elemento_pasajero.is_displayed(), "La reserva no se encontró en la tabla final con el nombre ingresado."
            allure.attach(driver.get_screenshot_as_png(), name="13_Reserva_Exitosa", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Reserva_Multidestinos", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Error en ejecución: {str(e)}")
