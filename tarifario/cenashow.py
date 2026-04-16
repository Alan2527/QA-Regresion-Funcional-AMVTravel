import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cena Show - Flujo Funcional")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Siguiendo el modelo exitoso de Traslados:
1. Login y navegación.
2. Filtro Cachi.
3. Validación de botones Ver/Cerrar (Toggle).
4. Validación de tabla.
5. Captura de evidencia en cada paso.
6. Iconos y Tooltips al final.
""")
def test_tarifario_cenashow(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)  # Aumentamos a 20 como en Traslados
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
        # 2. CLICK EN BOTÓN DE CENA SHOW
        # ==========================================
        with allure.step("2. Navegar a solapa Cena Show"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()
            
            btn_solapa = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#show"]')))
            driver.execute_script("arguments[0].click();", btn_solapa)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Solapa_CenaShow", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 3. FILTRAR LA CIUDAD DE CACHI
        # ==========================================
        with allure.step("3. Filtrar ciudad Cachi"):
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

        # ==========================================
        # 4. VALIDAR RESULTADO DE BÚSQUEDA
        # ==========================================
        with allure.step("4. Validar resultados de búsqueda"):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tariff-list-item, #show")))
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
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped']"
            )))
            assert tabla.is_displayed()
            allure.attach(driver.get_screenshot_as_png(), name="5_Tabla_Tarifas", attachment_type=allure.attachment_type.PNG)

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
            # Dejamos abierto para ver tooltips si es necesario
            driver.execute_script("arguments[0].click();", btn_vuelta)
            esperar_fin_de_carga()
            
            icon_clock = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            actions.move_to_element(icon_clock).pause(1.5).perform()
            
            # Captura final con tooltip
            allure.attach(driver.get_screenshot_as_png(), name="7_Tooltip_Final", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_CRITICO", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Error en el flujo: {str(e)}")
