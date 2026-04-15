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
1. Navegación y búsqueda.
2. Validación del ciclo de vida del botón Ver/Cerrar Tarifario.
3. Validación de la tabla de tarifas.
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

    def cambiar_destino(destino_actual, nuevo_destino):
        xpath_dropdown = f"//div[contains(@class, 'ts-control') and contains(., '{destino_actual}')]"
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(1)

        xpath_opcion = f"//div[contains(@class, 'option') and contains(text(), '{nuevo_destino}')]"
        opcion = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opcion)))
        driver.execute_script("arguments[0].click();", opcion)
        esperar_fin_de_carga()

    # Helpers JS para los botones Ver/Cerrar
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

        with allure.step("2. Búsqueda con destino Cachi"):
            cambiar_destino("Buenos Aires", "Cachi")
            btn_buscar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()

        # ==========================================
        # BLOQUE 2: CICLO DE VIDA DEL BOTÓN (TOGGLE)
        # ==========================================
        with allure.step("3. Validar toggle Ver/Cerrar Tarifario"):
            # 3.1 Validar estado inicial "Ver"
            btn_ver = buscar_boton_ver()
            assert "ver" in btn_ver.text.strip().lower()
            
            # 3.2 Click y validar cambio a "Cerrar"
            driver.execute_script("arguments[0].click();", btn_ver)
            esperar_fin_de_carga()
            btn_cerrar = buscar_boton_cerrar()
            assert "cerrar" in btn_cerrar.text.strip().lower()
            
            # 3.3 Click y validar vuelta a "Ver"
            driver.execute_script("arguments[0].click();", btn_cerrar)
            time.sleep(1)
            btn_vuelta = buscar_boton_ver()
            assert "ver" in btn_vuelta.text.strip().lower()
            
            # Lo dejamos abierto para validar las tarifas
            driver.execute_script("arguments[0].click();", btn_vuelta)
            esperar_fin_de_carga()

        # ==========================================
        # BLOQUE 3: TABLA DE TARIFAS
        # ==========================================
        with allure.step("4. Validar tabla de tarifas pTariff"):
            tabla = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded")))
            p_tariffs = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(p_tariffs) > 0, "No se encontraron elementos pTariff."
            allure.attach(driver.get_screenshot_as_png(), name="Tarifas_CenaShow", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # BLOQUE 4: MODALES
        # ==========================================
        with allure.step("5. Validar Modal Proveedores"):
            btn_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Ver Proveedores')])[1]")))
            driver.execute_script("arguments[0].click();", btn_prov)
            modal_prov = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show, .modal.in")))
            assert any(td.text.strip() != "" for td in modal_prov.find_elements(By.TAG_NAME, "td"))
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        with allure.step("6. Validar Modal Ver Detalle"):
            btn_detalle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tariff-op-detail-btn")))
            driver.execute_script("arguments[0].click();", btn_detalle)
            modal_detalle = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content")))
            assert modal_detalle.is_displayed()
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # ==========================================
        # BLOQUE 5: TOOLTIPS (AL FINAL)
        # ==========================================
        with allure.step("7. Validar Tooltip de Duración"):
            icono = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            actions.move_to_element(icono).pause(1).perform()
            tooltip = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(., 'Duración estimada')]")))
            assert tooltip.is_displayed()

        with allure.step("8. Validar Tooltip de Idiomas"):
            icono = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-translate")))
            actions.move_to_element(icono).pause(1).perform()
            tooltip = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[.//strong[contains(text(), 'Idiomas')]]")))
            assert "Español" in tooltip.text
            assert "English" in tooltip.text

        with allure.step("9. Validar Tooltip de Operatividad"):
            icono = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-calendar-dots")))
            actions.move_to_element(icono).pause(1).perform()
            tooltip = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[.//strong[contains(text(), 'Operatividad')]]")))
            assert "lunes" in tooltip.text.lower()
            allure.attach(driver.get_screenshot_as_png(), name="Tooltips_Final", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_CenaShow", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Fallo el test: {str(e)}")
