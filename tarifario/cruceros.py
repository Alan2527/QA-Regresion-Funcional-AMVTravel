import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cruceros - Flujo Funcional")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Flujo de prueba siguiendo los 9 pasos definidos:
1. Login.
2. Navegación a solapa Cruceros.
3. Filtro por ciudad Ushuaia.
4. Validación de resultados de búsqueda.
5. Verificación de texto inicial botón 'Ver Tarifario'.
6. Apertura y verificación de botón 'Cerrar Tarifario'.
7. Validación de tabla de tarifas (con espera dinámica de contenido).
8. Cierre y verificación de retorno a botón 'Ver Tarifario'.
9. Validación de iconos y tooltips.
""")
def test_tarifario_cruceros(logged_in_driver):
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
        time.sleep(1.5)

    try:
        # ==========================================
        # 1. LOGIN (Manejado por el fixture)
        # ==========================================

        # ==========================================
        # 2. CLICK EN SOLAPA CRUCEROS
        # ==========================================
        with allure.step("2. Navegar a solapa Cruceros"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()
            
            btn_solapa = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#cruise"]')))
            driver.execute_script("arguments[0].click();", btn_solapa)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Solapa_Cruceros", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 3. FILTRAR CIUDAD USHUAIA
        # ==========================================
        with allure.step("3. Filtrar ciudad Ushuaia"):
            xpath_dropdown = "//div[contains(@class, 'ts-control') and contains(., 'Buenos Aires')]"
            dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
            driver.execute_script("arguments[0].click();", dropdown)
            
            opcion = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Ushuaia')]")))
            driver.execute_script("arguments[0].click();", opcion)
            esperar_fin_de_carga()
            
            btn_buscar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()

        # ==========================================
        # 4. VALIDAR RESULTADO DE BÚSQUEDA
        # ==========================================
        with allure.step("4. Validar resultados de búsqueda"):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tariff-list-item, #cruise")))
            allure.attach(driver.get_screenshot_as_png(), name="2_Resultados_Busqueda", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 5. VALIDAR BOTÓN "VER TARIFARIO"
        # ==========================================
        with allure.step("5. Validar existencia del botón 'Ver Tarifario'"):
            btn_ver = wait.until(lambda d: d.execute_script("""
                return [...document.querySelectorAll('a')].find(a => a.innerText.toLowerCase().includes('ver tarifario'));
            """))
            assert "ver" in btn_ver.get_attribute("innerText").lower()
            allure.attach(driver.get_screenshot_as_png(), name="3_Boton_Ver_Tarifario", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 6. CLICK Y VALIDAR "CERRAR TARIFARIO"
        # ==========================================
        with allure.step("6. Click en Ver y validar cambio a 'Cerrar Tarifario'"):
            driver.execute_script("arguments[0].click();", btn_ver)
            esperar_fin_de_carga()
            
            btn_cerrar = wait.until(lambda d: d.execute_script("""
                return [...document.querySelectorAll('a')].find(a => a.innerText.toLowerCase().includes('cerrar tarifario'));
            """))
            assert "cerrar" in btn_cerrar.get_attribute("innerText").lower()
            allure.attach(driver.get_screenshot_as_png(), name="4_Boton_Cerrar_Tarifario", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 7. VALIDAR TABLA DE TARIFARIO
        # ==========================================
        with allure.step("7. Validar tabla de tarifas"):
            # Pequeño scroll para asegurar visibilidad
            driver.execute_script("window.scrollBy(0, 250);")
            time.sleep(1)

            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped']"
            )))
            
            # SOLUCIÓN AL ERROR 0 > 0: Espera dinámica a que los precios carguen dentro de la tabla
            p_tariffs = wait.until(lambda d: tabla.find_elements(By.CSS_SELECTOR, "p.pTariff"))
            
            assert len(p_tariffs) > 0, "Se abrió la tabla pero no se encontraron elementos pTariff (precios)."
            allure.attach(driver.get_screenshot_as_png(), name="5_Tabla_Tarifas_Cargada", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 8. CERRAR Y VALIDAR RETORNO A "VER"
        # ==========================================
        with allure.step("8. Click en Cerrar y validar retorno a 'Ver Tarifario'"):
            driver.execute_script("arguments[0].click();", btn_cerrar)
            time.sleep(2) # Tiempo para animación de cierre
            
            btn_vuelta = wait.until(lambda d: d.execute_script("""
                return [...document.querySelectorAll('a')].find(a => a.innerText.toLowerCase().includes('ver tarifario'));
            """))
            assert "ver" in btn_vuelta.get_attribute("innerText").lower()
            allure.attach(driver.get_screenshot_as_png(), name="6_Boton_Vuelta_Ver", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 9. VALIDAR ICONOS Y TOOLTIPS
        # ==========================================
        with allure.step("9. Validar iconos y tooltips"):
            # Re-abrimos para que los iconos sean visibles en la captura
            driver.execute_script("arguments[0].click();", btn_vuelta)
            esperar_fin_de_carga()
            
            icon_clock = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.fa-clock, i.ph-clock")))
            actions.move_to_element(icon_clock).pause(1.5).perform()
            
            allure.attach(driver.get_screenshot_as_png(), name="7_Tooltip_Final", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_CRITICO_CRUCEROS", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Error en el flujo de Cruceros: {str(e)}")
