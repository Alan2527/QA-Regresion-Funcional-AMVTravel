import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Excursiones Completa (Tarifas, Modales y Tooltips al final)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Excursiones:
1. Login y navegación a Excursiones.
2. Búsqueda con destino Cachi.
3. Validación del estado inicial del botón Ver Tarifario.
4. Apertura del panel principal, sub-grupos (si existen) y validación de la tabla.
5. Cierre del panel y validación del retorno al estado inicial.
6. Validación Independiente del modal "Ver Proveedores".
7. Validación Independiente del modal "Ver Detalle".
8. Validación Independiente de Tooltips (Duración, Idiomas, Operatividad) al final del flujo.
""")
def test_tarifario(logged_in_driver):
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
        with allure.step("1 a 2. Navegar a Tarifario y solapa Excursiones"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_excursiones = wait.until(EC.element_to_be_clickable((By.ID, "a-excursions")))
            driver.execute_script("arguments[0].click();", btn_excursiones)
            esperar_fin_de_carga()

        # =========================
        # 3 Filtro y búsqueda
        # =========================
        with allure.step("3. Cambiar destino a Cachi y buscar"):
            cambiar_destino("Buenos Aires", "Cachi")

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Cachi",
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

        # ==========================================
        # BLOQUE 1: VALIDACIÓN CICLO DE VIDA DEL PANEL
        # ==========================================

        # =========================
        # 4 Validar estado inicial Ver Tarifario
        # =========================
        with allure.step("4. Validar estado inicial del botón Ver Tarifario"):
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", buscar_boton_ver())
            time.sleep(1.5) 

            boton_ver_fresco = buscar_boton_ver()
            assert check_icono(boton_ver_fresco, "down"), "Falta el ícono de flecha hacia abajo en Ver Tarifario"
            allure.attach(driver.get_screenshot_as_png(), name="2_Estado_Inicial_Ver_Tarifario", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 5 Clickear en Ver Tarifario
        # =========================
        with allure.step("5. Click en Ver Tarifario para desplegar el panel principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)

        # =========================
        # 6 Validar Cerrar, Abrir Sub-Grupo (Opcional) y Leer Tabla
        # =========================
        with allure.step("6. Validar botón Cerrar Tarifario, desplegar tarifas y validar la tabla"):
            boton_cerrar_fresco = buscar_boton_cerrar()
            assert check_icono(boton_cerrar_fresco, "up"), "Falta el ícono de flecha hacia arriba en Cerrar Tarifario"

            grupo_tarifas = driver.execute_script("""
                var headers = document.querySelectorAll('a.tariff-detail-group-name');
                for (var i=0; i<headers.length; i++) {
                    var text = (headers[i].textContent || headers[i].innerText || "").toLowerCase();
                    if (text.includes('tarifas')) {
                        return headers[i];
                    }
                }
                return null;
            """)
            
            if grupo_tarifas:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", grupo_tarifas)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", grupo_tarifas)
                time.sleep(2) 

            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))

            tarifas = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(tarifas) > 0, "No hay tarifas en la tabla"
            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Y_Tabla_Abiertos", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 7 Cierre Tarifario
        # =========================
        with allure.step("7. Cerrar el acordeón principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2.5) 
            
        # =========================
        # 8 Validar estado Ver Tarifario nuevamente
        # =========================
        with allure.step("8. Validar que el botón retornó a Ver Tarifario"):
            boton_ver_finalisimo = buscar_boton_ver()
            assert check_icono(boton_ver_finalisimo, "down"), "Falta el ícono de flecha hacia abajo en el cierre final"
            allure.attach(driver.get_screenshot_as_png(), name="4_Cierre_Final_OK", attachment_type=allure.attachment_type.PNG)


        # ==========================================
        # BLOQUE 2: VALIDACIÓN DE MODALES (INDEPENDIENTES)
        # ==========================================

        with allure.step("9. Abrir modal de Proveedores desde el listado y validar datos"):
            actions.move_by_offset(0, 0).perform()
            
            btn_proveedores = wait.until(EC.presence_of_element_located((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_proveedores)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            modal_prov = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal"
            )))
            time.sleep(3) 

            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores cargó vacía."

            allure.attach(driver.get_screenshot_as_png(), name="5_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1.5)
            esperar_fin_de_carga()

        with allure.step("10. Click en botón Ver Detalle y validar apertura de modal de detalle"):
            
            # ---------------------------------------------------------
            # SELECTOR ROBUSTO POR CLASE Y TEXTO
            # ---------------------------------------------------------
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@class, 'tariff-op-detail-btn') and contains(text(), 'Ver Detalle')]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            time.sleep(1) 
            driver.execute_script("arguments[0].click();", btn_detalle)

            # Esperamos a que el modal se haga visible
            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle de operatividad no se renderizó."
            time.sleep(1)

            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()


        # ==========================================
        # 12-15. VALIDACIÓN DE TOOLTIPS Y OBSERVACIONES (FINAL)
        # ==========================================
        with allure.step("15. Validar Observación Prioritaria"):
            # Buscamos el contenedor div y validamos que el span interno tenga el texto exacto
            obs_span = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tariff-obs-item')]//span[contains(text(), 'tet')]")))
            
            assert obs_span.is_displayed(), "El div de observación o su texto no son visibles en pantalla"
            
            allure.attach(driver.get_screenshot_as_png(), name="10_Observacion_Prioritaria", attachment_type=allure.attachment_type.PNG)
            
        with allure.step("12. Validar Tooltip de Duración"):
            icon_clock = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph.ph-clock")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", icon_clock)
            actions.move_to_element(icon_clock).perform()
            
            # Esperamos a que el tooltip HTML se inyecte y sea visible
            tooltip_duracion = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.tariff-op-tooltip")))
            assert "Duración estimada del servicio" in tooltip_duracion.text, f"Texto de duración incorrecto. Actual: {tooltip_duracion.text}"
            
            allure.attach(driver.get_screenshot_as_png(), name="7_Tooltip_Duracion", attachment_type=allure.attachment_type.PNG)

        with allure.step("13. Validar Tooltip de Idiomas"):
            icon_lang = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph.ph-translate")))
            actions.move_to_element(icon_lang).perform()
            
            # Validamos la estructura interna del tooltip (strong y los li dentro del ul)
            wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(), 'Idiomas')]")))
            li_italian = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'Español')]")))
            li_french = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'English')]")))
            
            assert li_italian.is_displayed() and li_french.is_displayed(), "No se encontraron los idiomas correctos en la lista del tooltip"
            
            allure.attach(driver.get_screenshot_as_png(), name="8_Tooltip_Idiomas", attachment_type=allure.attachment_type.PNG)

        with allure.step("14. Validar Tooltip de Operatividad"):
            icon_cal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph.ph-calendar-dots")))
            actions.move_to_element(icon_cal).perform()
            
            # Validamos el título y los textos exactos de las viñetas
            wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(), 'Operatividad')]")))
            li_temporada = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'Temporada: enero, marzo, mayo, julio, septiembre, noviembre')]")))
            
            assert li_temporada.is_displayed(), "No se encontraron los datos de operatividad en la lista del tooltip"
            
            allure.attach(driver.get_screenshot_as_png(), name="9_Tooltip_Calendario", attachment_type=allure.attachment_type.PNG)



    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Traslados", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Error en ejecución: {str(e)}")
