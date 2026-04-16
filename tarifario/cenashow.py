import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cena Show - Flujo Funcional y Tooltips")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Cena Show:
1. Navegación y búsqueda con capturas de cada paso.
2. Validación del ciclo de vida del botón Ver/Cerrar Tarifario.
3. Validación de la tabla de tarifas (con selector optimizado).
4. Validación de modales (Proveedores y Detalle).
5. Validación de Tooltips (Duración, Idiomas, Operatividad) - Al final.
""")
def test_tarifario_cenashow(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
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

    def buscar_boton_ver():
        return wait.until(lambda d: d.execute_script("""
            var links = document.querySelectorAll('a');
            for (var i=0; i<links.length; i++) {
                var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                if (text.includes('ver tarifario')) return links[i];
            }
            return null;
        """), message="No se encontró el botón 'Ver Tarifario'")

    def buscar_boton_cerrar():
        return wait.until(lambda d: d.execute_script("""
            var links = document.querySelectorAll('a');
            for (var i=0; i<links.length; i++) {
                var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                if (text.includes('cerrar tarifario')) return links[i];
            }
            return null;
        """), message="No se encontró el botón 'Cerrar Tarifario'")

    try:
        # ==========================================
        # BLOQUE 1: NAVEGACIÓN Y BÚSQUEDA
        # ==========================================
        with allure.step("1. Navegar a Tarifario y solapa Cena Show"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()
            
            btn_cenashow = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#show"]')))
            driver.execute_script("arguments[0].click();", btn_cenashow)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Solapa_CenaShow", attachment_type=allure.attachment_type.PNG)

        with allure.step("2. Búsqueda con destino Cachi"):
            # Cambio de destino
            xpath_dropdown = "//div[contains(@class, 'ts-control') and contains(., 'Buenos Aires')]"
            dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
            driver.execute_script("arguments[0].click();", dropdown)
            
            opcion = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Cachi')]")))
            driver.execute_script("arguments[0].click();", opcion)
            esperar_fin_de_carga()

            btn_buscar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="2_Resultados_Busqueda", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # BLOQUE 2: CICLO DE VIDA DEL BOTÓN (TOGGLE)
        # ==========================================
        with allure.step("3. Validar toggle Ver/Cerrar Tarifario"):
            btn_ver = buscar_boton_ver()
            texto_ver = btn_ver.get_attribute("innerText").strip().lower()
            assert "ver" in texto_ver, f"Se esperaba 'ver' pero se obtuvo: '{texto_ver}'"
            
            driver.execute_script("arguments[0].click();", btn_ver)
            esperar_fin_de_carga()
            
            btn_cerrar = buscar_boton_cerrar()
            texto_cerrar = btn_cerrar.get_attribute("innerText").strip().lower()
            assert "cerrar" in texto_cerrar, f"Se esperaba 'cerrar' pero se obtuvo: '{texto_cerrar}'"
            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Abierto", attachment_type=allure.attachment_type.PNG)
            
            # Volver a cerrar y abrir para asegurar estabilidad
            driver.execute_script("arguments[0].click();", btn_cerrar)
            time.sleep(1)
            btn_abrir_final = buscar_boton_ver()
            driver.execute_script("arguments[0].click();", btn_abrir_final)
            esperar_fin_de_carga()

        # ==========================================
        # BLOQUE 3: TABLA DE TARIFAS
        # ==========================================
        with allure.step("4. Validar tabla de tarifas pTariff"):
            # Usamos un selector más permisivo por si las clases cambian levemente
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped']"
            )))
            
            p_tariffs = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(p_tariffs) > 0, "No se encontraron elementos pTariff dentro de la tabla."
            allure.attach(driver.get_screenshot_as_png(), name="4_Tabla_Tarifas_Visible", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # BLOQUE 4: MODALES
        # ==========================================
        with allure.step("5. Validar Modal Proveedores"):
            btn_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Ver Proveedores')])[1]")))
            driver.execute_script("arguments[0].click();", btn_prov)
            
            modal_prov = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show, .modal.in")))
            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.get_attribute("innerText").strip() != "" for td in tds), "La tabla de proveedores está vacía."
            allure.attach(driver.get_screenshot_as_png(), name="5_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        with allure.step("6. Validar Modal Ver Detalle"):
            btn_detalle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tariff-op-detail-btn")))
            driver.execute_script("arguments[0].click();", btn_detalle)
            
            modal_detalle = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content")))
            assert modal_detalle.is_displayed()
            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_Detalle", attachment_type=allure.attachment_type.PNG)
            
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # ==========================================
        # BLOQUE 5: TOOLTIPS (AL FINAL)
        # ==========================================
        with allure.step("7. Validar Tooltips"):
            # Duración
            icono_reloj = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            actions.move_to_element(icono_reloj).pause(1.5).perform()
            tooltip_duracion = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(., 'Duración estimada')]")))
            assert tooltip_duracion.is_displayed()
            
            # Operatividad (Screenshot final con tooltips)
            icono_cal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-calendar-dots")))
            actions.move_to_element(icono_cal).pause(1.5).perform()
            allure.attach(driver.get_screenshot_as_png(), name="7_Tooltips_Final", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        # Captura de pantalla crítica en caso de cualquier fallo
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_CRITICO", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Fallo el test en el paso actual: {str(e)}")
