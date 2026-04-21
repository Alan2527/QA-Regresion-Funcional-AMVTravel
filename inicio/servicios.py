import pytest
import allure
import time
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
""")
def test_reserva_servicio_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    with allure.step("1 a 5. Seleccionar pestaña Servicios, ingresar destino, tipo y buscar"):
        try:
            # 2. Click en la pestaña de Servicios
            tab_servicios = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabServices']")), message="No se encontró la pestaña a[href='#tabServices']")
            tab_servicios.click()
            time.sleep(1) 

            # 3. Dropdown Destino (Ciudad)
            btn_ciudad = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_updServicesCity .ts-control")), message="No se encontró el control del DDL de Ciudad")
            btn_ciudad.click()
            time.sleep(1) # Esperamos que se despliegue la lista
            opcion_bariloche = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Bariloche')] | //div[contains(text(), 'Bariloche')]")), message="No se encontró la opción 'Bariloche' en la lista")
            opcion_bariloche.click()
            time.sleep(1)

            # 4. Dropdown Tipo de Servicio (Opcionales)
            btn_tipo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_updServicesOptionals .ts-control")), message="No se encontró el control del DDL de Tipo de Servicio")
            btn_tipo.click()
            time.sleep(1) # Esperamos que se despliegue la lista
            opcion_excursion = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Excursión')] | //div[contains(text(), 'Excursión')]")), message="No se encontró la opción 'Excursión' en la lista")
            opcion_excursion.click()
            time.sleep(1)

            # --- CAPTURA PREVIA A LA BÚSQUEDA (Pasos 1 al 4 completados) ---
            allure.attach(driver.get_screenshot_as_png(), name="Formulario_Completo_Antes_Buscar", attachment_type=allure.attachment_type.PNG)

            # 5. Click en Buscar
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_btnSearch")), message="No se encontró el botón de Buscar (btnSearch)").click()
            
            # Espera larga para los resultados
            wait_largo = WebDriverWait(driver, 45)
            wait_largo.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.panelShadow.col-sm-6")), message="La búsqueda superó los 45 segundos y no cargaron los resultados de servicios")
            time.sleep(2)
            
            allure.attach(driver.get_screenshot_as_png(), name="Busqueda_Ejecutada", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_1_a_5", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al ingresar filtros de búsqueda. Detalle: {str(e)}")

    with allure.step("6. Validar panel de resultados (Cards de Servicios)"):
        try:
            # a. Validar que exista la card
            assert driver.find_elements(By.CSS_SELECTOR, "div.panelShadow.col-sm-6"), "No se encontró ningún div con la clase 'panelShadow col-sm-6'"
            
            # b, c, d, e, f. Validar componentes internos de la card
            assert driver.find_elements(By.CSS_SELECTOR, "img[style*='width: 450px']"), "Falta la imagen de 450x323px en la card"
            assert driver.find_elements(By.CSS_SELECTOR, "h4.h4Span"), "Falta el nombre del servicio (h4Span)"
            assert driver.find_elements(By.CSS_SELECTOR, "table[style*='text-align:center'], table[style*='text-align: center']"), "Falta la tabla de precios/tipo centrada"
            assert driver.find_elements(By.CSS_SELECTOR, "div.divservlimit"), "Falta la descripción del servicio (divservlimit)"
            assert driver.find_elements(By.CSS_SELECTOR, "a.apreload.btn.btnGray.pink-btn"), "Falta el botón de selección/ver más"
            
            allure.attach(driver.get_screenshot_as_png(), name="Resultados_Validados", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_6", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error en validación de las cards de servicio: {str(e)}")

    with allure.step("7 y 8. Click en servicio y validar detalle interno"):
        try:
            # 7. Click en el botón
            btn_seleccionar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.apreload.btn.btnGray.pink-btn")), message="No se encontró el botón para entrar al servicio")
            btn_seleccionar.click()
            time.sleep(3) # Espera a que cargue el detalle

            # 8. Validaciones de la vista de detalle
            assert wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.h3ServiceName")), message="No cargó el Detalle del Servicio (falta h3ServiceName)")
            assert driver.find_elements(By.CSS_SELECTOR, "img.popu"), "Falta la imagen del servicio (popu)"
            assert driver.find_elements(By.CSS_SELECTOR, "div.detailsdiv"), "Faltan los detalles del servicio (detailsdiv)"
            assert driver.find_elements(By.CSS_SELECTOR, "table.table.table-bordered.table-striped"), "Falta la tabla de precios detallada"

            allure.attach(driver.get_screenshot_as_png(), name="Detalle_Servicio_Validado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_7_a_8", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Fallo al ingresar o validar el detalle del servicio. Detalle: {str(e)}")

    with allure.step("9 y 10. Seleccionar pasajeros"):
        try:
            # 9. Primer select (Pax 1)
            select_pax_1 = Select(wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMainSlider$lvServiceRates$ctrl0$ctrlPaxQuantityControl$ddPax")), message="No se encontró el primer DDL de pasajeros"))
            select_pax_1.select_by_visible_text("2")

            # 10. Segundo select (Pax 2)
            select_pax_2 = Select(wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMainSlider$lvServiceRates$ctrl1$ctrlPaxQuantityControl$ddPax")), message="No se encontró el segundo DDL de pasajeros"))
            select_pax_2.select_by_visible_text("2")
            
            time.sleep(1)
            allure.attach(driver.get_screenshot_as_png(), name="Pasajeros_Seleccionados", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_9_a_10", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Error al seleccionar la cantidad de pasajeros. Detalle: {str(e)}")

    with allure.step("11 y 12. Confirmar reserva y validar incremento en el carrito"):
        try:
            # 1. Obtener el valor actual del carrito ANTES de reservar
            cart_element = wait.until(EC.presence_of_element_located((By.ID, "lblCartCount")), message="No se encontró el contador del carrito")
            initial_cart_text = cart_element.text.strip()
            # Si está vacío, lo tomamos como 0
            initial_cart_count = int(initial_cart_text) if initial_cart_text.isdigit() else 0
            expected_count = initial_cart_count + 4

            # 2. Hacer clic en el botón de Reservar final
            btn_reservar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_lnkBookService")), message="No se encontró el botón de Reservar Servicio")
            btn_reservar.click()

            # 3. Manejar el alert si es que el sistema tira uno al confirmar
            try:
                alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert.accept()
            except:
                pass # Si no hay alert, seguimos de largo

            # 4. Validar que el contador sumó 4
            wait.until(
                lambda d: int(d.find_element(By.ID, "lblCartCount").text.strip() or 0) == expected_count,
                message=f"La reserva falló: El carrito no se actualizó al valor esperado ({expected_count})"
            )
            
            # 5. Captura de éxito
            allure.attach(driver.get_screenshot_as_png(), name="Reserva_Exitosa_Carrito_Actualizado", attachment_type=allure.attachment_type.PNG)
            
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Carrito", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Ocurrió un error al validar el carrito. Detalle: {str(e)}")
