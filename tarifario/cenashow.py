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
        # BLOQUE 2: APERTURA Y VALIDACIÓN DE BOTÓN
        # ==========================================
        with allure.step("3. Abrir Tarifario y validar cambio de texto"):
            btn_ver = buscar_boton_ver()
            
            # Validamos texto inicial
            assert "ver" in btn_ver.get_attribute("innerText").lower()
            
            # Abrimos
            driver.execute_script("arguments[0].click();", btn_ver)
            esperar_fin_de_carga()
            
            # Validamos que ahora dice Cerrar
            btn_cerrar = buscar_boton_cerrar()
            assert "cerrar" in btn_cerrar.get_attribute("innerText").lower()
            
            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Abierto_Confirmado", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # BLOQUE 3: TABLA DE TARIFAS (SIN RE-CIERRE)
        # ==========================================
        with allure.step("4. Validar tabla de tarifas pTariff"):
            # Esperamos que la tabla sea visible después del clic anterior
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped']"
            )))
            
            # Scroll suave para que la tabla esté en el centro de la captura
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tabla)
            time.sleep(1)
            
            p_tariffs = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(p_tariffs) > 0, "No se encontraron elementos pTariff en la tabla."
            allure.attach(driver.get_screenshot_as_png(), name="4_Tabla_Tarifas_OK", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # BLOQUE 4: MODALES
        # ==========================================
        with allure.step("5. Validar Modal Proveedores"):
            btn_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Ver Proveedores')])[1]")))
            driver.execute_script("arguments[0].click();", btn_prov)
            
            modal_prov = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show, .modal.in")))
            allure.attach(driver.get_screenshot_as_png(), name="5_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1.5)

        with allure.step("6. Validar Modal Ver Detalle"):
            btn_detalle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tariff-op-detail-btn")))
            driver.execute_script("arguments[0].click();", btn_detalle)
            
            modal_detalle = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content")))
            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_Detalle", attachment_type=allure.attachment_type.PNG)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1.5)

        # ==========================================
        # BLOQUE 5: TOOLTIPS
        # ==========================================
        with allure.step("7. Validar Tooltips"):
            icono_reloj = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            actions.move_to_element(icono_reloj).pause(1).perform()
            allure.attach(driver.get_screenshot_as_png(), name="7_Tooltip_Duracion", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_EN_PASO", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Fallo en el flujo: {str(e)}")
