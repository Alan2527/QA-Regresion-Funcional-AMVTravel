import os  # Agregado para validar la descarga de archivos
import time
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Ofertas Completa (Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
def test_tarifario_ofertas(logged_in_driver):

    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(),'CARGANDO','cargando'),'cargando') or contains(@class,'loading')]"
            )))
        except:
            pass

        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof jQuery==='undefined') || (jQuery.active===0);"
            ))
        except:
            pass

        time.sleep(1)

    try:
        # =========================
        # 1-2 Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Ofertas"):

            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_ofertas = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'a[href="#opportunity"]'
            )))
            driver.execute_script("arguments[0].click();", btn_ofertas)
            esperar_fin_de_carga()

        # =========================
        # 3 Búsqueda
        # =========================
        with allure.step("3. Buscar ofertas en Buenos Aires"):

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_buscar)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", btn_buscar)
            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Ofertas_BUE",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 4 Modal
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):

            XPATH_DETALLE = "//a[@href='javascript:void(0);' and contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')]"

            def get_btn_detalle():
                return wait.until(EC.presence_of_element_located((By.XPATH, XPATH_DETALLE)))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", get_btn_detalle())
            time.sleep(1)

            driver.execute_script("arguments[0].click();", get_btn_detalle())

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))

            time.sleep(1)

            assert modal_detalle.is_displayed(), "El modal de detalle de la oferta no se renderizó."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            wait.until(EC.invisibility_of_element(modal_detalle))
            time.sleep(1)

        # =========================
        # HELPERS DE BÚSQUEDA INDEPENDIENTE
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
            # Definimos la ruta de descargas
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

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
