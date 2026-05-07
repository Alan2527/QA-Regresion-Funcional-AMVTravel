import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cruceros Completa (Tarifas y Modales)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Cruceros:
1. Login y navegación a Cruceros.
2. Búsqueda con destino Ushuaia.
3. Validación de ciclo de vida del botón Ver/Cerrar Tarifario.
4. Validación de la tabla de tarifas.
5. Validación de modales (Proveedores y Detalle).
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
        # 1-2. NAVEGACIÓN
        # ==========================================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Cruceros"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_cruceros = wait.until(EC.element_to_be_clickable((By.ID, "a-cruises")))
            driver.execute_script("arguments[0].click();", btn_cruceros)
            esperar_fin_de_carga()

        # ==========================================
        # 3. FILTRO Y BÚSQUEDA
        # ==========================================
        with allure.step("3. Cambiar destino a Ushuaia y buscar"):
            cambiar_destino("Buenos Aires", "Ushuaia")
            btn_buscar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Ushuaia", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 5. VALIDAR BOTÓN VER TARIFARIO
        # ==========================================
        with allure.step("5. Validar existencia del botón 'Ver Tarifario'"):
            btn_acordeon = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.tariff-view-table")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_acordeon)
            time.sleep(1)
            
            texto_inicial = btn_acordeon.get_attribute("innerText").lower()
            assert "ver" in texto_inicial, f"Se esperaba 'Ver Tarifario', se obtuvo: '{texto_inicial}'"
            allure.attach(driver.get_screenshot_as_png(), name="2_Estado_Inicial_Ver", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 6. CLICK VER Y VALIDAR CERRAR + TABLA
        # ==========================================
        with allure.step("6. Click en Ver Tarifario, validar tabla y botón Cerrar"):
            driver.execute_script("arguments[0].click();", btn_acordeon)
            esperar_fin_de_carga()
            
            # Validamos que el botón cambió a Cerrar
            wait.until(lambda d: "cerrar" in btn_acordeon.get_attribute("innerText").lower())
            
            # Validamos la tabla (clase div.tariff-detail-list que pasaste)
            tabla_detalle = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.tariff-detail-list")))
            p_tariffs = wait.until(lambda d: tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff"))
            assert len(p_tariffs) > 0, "No se encontraron tarifas p.pTariff en la tabla."
            
            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Abierto_Y_Tabla", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 8. CLICK CERRAR Y VALIDAR VER
        # ==========================================
        with allure.step("8. Click en Cerrar Tarifario y validar retorno a 'Ver'"):
            driver.execute_script("arguments[0].click();", btn_acordeon)
            time.sleep(2) # Espera para animación de cierre
            
            texto_final = btn_acordeon.get_attribute("innerText").lower()
            assert "ver" in texto_final, f"El botón no volvió a 'Ver', dice: '{texto_final}'"
            allure.attach(driver.get_screenshot_as_png(), name="4_Tarifario_Cerrado_Vuelta_A_Ver", attachment_type=allure.attachment_type.PNG)

        # ==========================================
        # 10. MODAL PROVEEDORES
        # ==========================================
        with allure.step("10. Abrir modal de Proveedores"):
            btn_prov = wait.until(EC.presence_of_element_located((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_prov)
            driver.execute_script("arguments[0].click();", btn_prov)

            modal_prov = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal")))
            time.sleep(2)
            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores está vacía."
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # ==========================================
        # 11. MODAL VER DETALLE
        # ==========================================
        with allure.step("11. Click en botón Ver Detalle"):
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(translate(text(), 'VER DETALLE', 'ver detalle'), 'ver detalle')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal.show div.modal-content, div.modal.in div.modal-content"
            )))
            assert modal_detalle.is_displayed()
            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)
            
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_EJECUCION", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló: {str(e)}")
