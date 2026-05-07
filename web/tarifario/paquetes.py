import pytest
import allure
import time
import os  # Agregado para validar la existencia del archivo en el sistema
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Paquetes Completa (Tags, Tarifas y Modales)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Paquetes:
1. Login y navegación a la solapa Paquetes.
2. Búsqueda con destino Buenos Aires.
3. Validación del estado inicial del botón Ver Tarifario.
4. Apertura del panel principal, sub-acordeón de habitaciones y validación de la tabla de tarifas.
5. Cierre del panel y validación del retorno al estado inicial.
6. Validación Independiente del botón de Descarga de archivo (y existencia del archivo en la carpeta de descargas).
7. Validación Independiente del modal "Ver Detalle".
""")
def test_tarifario_hoteles(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loading') or contains(@class, 'spinner')]"
            )))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof Sys === 'undefined') || "
                "(typeof Sys.WebForms === 'undefined') || "
                "(Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack() === false);"
            ))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof jQuery === 'undefined') || (jQuery.active === 0);"
            ))
        except:
            pass
        time.sleep(1)

    def cambiar_destino(destino_actual, nuevo_destino):
        xpath_dropdown = f"//div[contains(@class, 'ts-control') and contains(., '{destino_actual}')]"
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(1)

        xpath_opcion = f"//div[contains(@class, 'option') and contains(text(), '{nuevo_destino}')]"
        opcion = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opcion)))
        driver.execute_script("arguments[0].click();", opcion)

        esperar_fin_de_carga()

    try:
        # =========================
        # 1-2 Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Paquetes"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_paquetes = wait.until(EC.element_to_be_clickable((By.ID, "a-tours")))
            driver.execute_script("arguments[0].click();", btn_paquetes)
            esperar_fin_de_carga()

        # =========================
        # 3 Filtro y búsqueda
        # =========================
        with allure.step("3. Cambiar destino a Buenos Aires y buscar"):
            cambiar_destino("Buenos Aires", "Buenos Aires")

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_BuenosAires_Paquetes",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # HELPERS INFALIBLES JAVASCRIPT
        # =========================
        def buscar_boton_ver():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('ver tarifario')) {
                        return links[i];
                    }
                }
                return null;
            """), message="No se encontró el botón 'Ver Tarifario'.")

        def buscar_boton_cerrar():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('cerrar tarifario')) {
                        return links[i];
                    }
                }
                return null;
            """), message="No se encontró el botón 'Cerrar Tarifario'.")

        def check_icono(elemento, direccion):
            return driver.execute_script(f"return arguments[0].querySelector('i[class*=\"chevron-{direccion}\"]') !== null;", elemento)


        # =========================
        # 5 Validar estado inicial Ver Tarifario
        # =========================
        with allure.step("5. Validar estado inicial del botón Ver Tarifario"):
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", buscar_boton_ver())
            time.sleep(1.5)

            boton_ver_fresco = buscar_boton_ver()
            assert check_icono(boton_ver_fresco, "down"), "Falta el ícono de flecha hacia abajo en Ver Tarifario"
            allure.attach(driver.get_screenshot_as_png(), name="3_Estado_Inicial_Ver_Tarifario", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 6 Clickear en Ver Tarifario
        # =========================
        with allure.step("6. Click en Ver Tarifario para desplegar el panel principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)

        # =========================
        # 7 Validar Cerrar, Abrir Sub-Grupo y Leer Tabla
        # =========================
        with allure.step("7. Validar botón Cerrar Tarifario, desplegar habitación y validar la tabla"):
            boton_cerrar_fresco = buscar_boton_cerrar()
            assert check_icono(boton_cerrar_fresco, "up"), "Falta el ícono de flecha hacia arriba en Cerrar Tarifario"

            btn_habitacion = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "a[id^='accordeon-header-']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_habitacion)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_habitacion)
            time.sleep(2)

            # Validamos que aparezca la tabla con tarifas O el mensaje de resultados vacíos
            wait.until(lambda d: 
                (len(d.find_elements(By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped'] p.pTariff")) > 0) or 
                (len(d.find_elements(By.CSS_SELECTOR, "p.tariff-empty-result")) > 0)
            , message="No se encontró ni la tabla con tarifas ni el mensaje de resultados vacíos.")

            allure.attach(driver.get_screenshot_as_png(), name="4_Tarifario_Y_Tabla_Abiertos", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 8 Cierre Tarifario
        # =========================
        with allure.step("8. Cerrar el acordeón principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2.5)

        # =========================
        # 9 Validar estado Ver Tarifario nuevamente
        # =========================
        with allure.step("9. Validar que el botón retornó a Ver Tarifario"):
            boton_ver_finalisimo = buscar_boton_ver()
            assert check_icono(boton_ver_finalisimo, "down"), "Falta el ícono de flecha hacia abajo en el cierre final"
            allure.attach(driver.get_screenshot_as_png(), name="5_Cierre_Final_OK", attachment_type=allure.attachment_type.PNG)


        # =========================
        # 10 Botón de descarga de archivo Word
        # =========================
        with allure.step("10. Clickear en botón de descarga y validar existencia de archivo .docx"):
            # Definimos la ruta de descargas (ajustar si el runner tiene una ruta personalizada)
            download_dir = os.path.expanduser("~/Downloads")
            
            # Capturamos lista de archivos antes de la descarga para comparar
            files_before = os.listdir(download_dir) if os.path.exists(download_dir) else []

            # Buscamos el botón por su clase específica
            btn_descarga = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "button.btn-download-word"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_descarga)
            time.sleep(1)
            
            # Validamos el tooltip antes de descargar
            assert btn_descarga.get_attribute("title") == "Descargar en formato Word", "El tooltip del botón no es correcto"
            
            driver.execute_script("arguments[0].click();", btn_descarga)

            # Polling para detectar el nuevo archivo descargado
            descarga_exitosa = False
            for i in range(15): # Esperamos hasta 15 segundos
                time.sleep(1)
                if os.path.exists(download_dir):
                    files_after = os.listdir(download_dir)
                    # Buscamos un archivo .docx que no estuviera antes
                    new_files = [f for f in files_after if f not in files_before and f.endswith(".docx")]
                    if new_files:
                        descarga_exitosa = True
                        break
            
            assert descarga_exitosa, "No se detectó la descarga del archivo .docx en la carpeta de descargas."
            
            allure.attach(driver.get_screenshot_as_png(), name="6_Captura_Boton_Descarga", attachment_type=allure.attachment_type.PNG)
            esperar_fin_de_carga()

        # =========================
        # 11 Modal Ver Detalle
        # =========================
        with allure.step("11. Click en botón Ver Detalle y validar apertura de modal de detalle"):
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(translate(text(), 'VER DETALLE', 'ver detalle'), 'ver detalle')]"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal.show div.modal-content, div.modal.in div.modal-content"
            )))

            assert modal_detalle.is_displayed(), "El modal de detalle no se renderizó."
            time.sleep(1)

            allure.attach(driver.get_screenshot_as_png(), name="7_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Paquetes",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
