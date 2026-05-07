import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Traslados Completa (Capturas, Modales y Tooltips)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Traslados:
1. Navegación y búsqueda con destino Cachi.
2. Validación de estados del botón Ver/Cerrar Tarifario con capturas.
3. Validación de modal Proveedores (usando selector btn-download-word).
4. Validación de modal Detalle (idéntico a Hoteles).
5. Validación de Tooltips al final del flujo.
""")
def test_tarifario_traslados(logged_in_driver):
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
        # ==========================================
        # 1-3. NAVEGACIÓN Y BÚSQUEDA
        # ==========================================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Traslados"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_traslados = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#transfer"]')))
            driver.execute_script("arguments[0].click();", btn_traslados)
            esperar_fin_de_carga()

        with allure.step("3. Cambiar destino a Cachi y buscar"):
            cambiar_destino("Buenos Aires", "Cachi")
            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Cachi", attachment_type=allure.attachment_type.PNG)

        # =========================
        # HELPERS JAVASCRIPT
        # =========================
        def buscar_boton_ver():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('ver tarifario')) return links[i];
                }
                return null;
            """))

        def buscar_boton_cerrar():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('cerrar tarifario')) return links[i];
                }
                return null;
            """))
            
        def check_icono(elemento, direccion):
            return driver.execute_script(f"return arguments[0].querySelector('i[class*=\"chevron-{direccion}\"]') !== null;", elemento)

        # ==========================================
        # 4-6. CICLO DE VIDA DEL PANEL
        # ==========================================
        with allure.step("4. Validar estado inicial del botón Ver Tarifario"):
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", buscar_boton_ver())
            time.sleep(1.5) 
            assert check_icono(buscar_boton_ver(), "down")
            allure.attach(driver.get_screenshot_as_png(), name="2_Estado_Inicial_Ver", attachment_type=allure.attachment_type.PNG)

        with allure.step("5. Abrir Tarifario y validar tabla"):
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)
            
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            assert len(tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")) > 0
            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Abierto", attachment_type=allure.attachment_type.PNG)

        with allure.step("6. Cerrar Tarifario"):
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2)
            assert check_icono(buscar_boton_ver(), "down")
            allure.attach(driver.get_screenshot_as_png(), name="4_Tarifario_Cerrado", attachment_type=allure.attachment_type.PNG)

# ==========================================
        # 10. MODAL PROVEEDORES (SELECTORES REALES)
        # ==========================================
        with allure.step("10. Abrir modal de Proveedores y validar tabla"):
            # Buscamos el botón de apertura
            btn_prov = wait.until(EC.presence_of_element_located((
                By.XPATH, "//button[contains(@class, 'btn-download-word') and contains(@onclick, 'openSuppliersModal')]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_prov)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_prov)
            
            # 1. Esperamos el modal usando la clase del div padre que me pasaste
            modal_prov = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.suppliers-modal-content"
            )))
            time.sleep(1) # Pequeña pausa para que termine la animación
            
            # 2. Validamos que el body del modal tenga contenido
            modal_body = modal_prov.find_element(By.CSS_SELECTOR, ".suppliers-modal-body")
            tds = modal_body.find_elements(By.TAG_NAME, "td")
            
            # Validación flexible: si hay TDs valida que no estén vacíos, sino valida que haya texto en el body
            if len(tds) > 0:
                assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores está vacía."
            else:
                assert modal_body.text.strip() != "", "El modal de proveedores cargó sin texto/contenido."
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            
            # 3. Cerramos usando el botón de cierre específico
            btn_cerrar_prov = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, ".btn-close-suppliers"
            )))
            driver.execute_script("arguments[0].click();", btn_cerrar_prov)
            time.sleep(1.5) # Esperamos que el modal desaparezca antes de seguir al siguiente paso

        # ==========================================
        # 11. MODAL VER DETALLE (IDÉNTICO A HOTELES)
        # ==========================================
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

            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # ==========================================
        # 12-15. VALIDACIÓN DE TOOLTIPS Y OBSERVACIONES (FINAL)
        # ==========================================
        with allure.step("15. Validar Observación Prioritaria"):
            # Buscamos el contenedor div y validamos que el span interno tenga el texto exacto
            obs_span = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tariff-obs-item')]//span[contains(text(), 'Test observación prioritaria')]")))
            
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
            li_italian = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'Italian')]")))
            li_french = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'French')]")))
            
            assert li_italian.is_displayed() and li_french.is_displayed(), "No se encontraron los idiomas correctos en la lista del tooltip"
            
            allure.attach(driver.get_screenshot_as_png(), name="8_Tooltip_Idiomas", attachment_type=allure.attachment_type.PNG)

        with allure.step("14. Validar Tooltip de Operatividad"):
            icon_cal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph.ph-calendar-dots")))
            actions.move_to_element(icon_cal).perform()
            
            # Validamos el título y los textos exactos de las viñetas
            wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(), 'Operatividad')]")))
            li_dias = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'Días: lunes a miércoles, sábado a domingo')]")))
            li_temporada = wait.until(EC.presence_of_element_located((By.XPATH, "//ul//li[contains(text(), 'Temporada: enero a abril, agosto a diciembre')]")))
            
            assert li_dias.is_displayed() and li_temporada.is_displayed(), "No se encontraron los datos de operatividad en la lista del tooltip"
            
            allure.attach(driver.get_screenshot_as_png(), name="9_Tooltip_Calendario", attachment_type=allure.attachment_type.PNG)


    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Traslados", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Error en ejecución: {str(e)}")
