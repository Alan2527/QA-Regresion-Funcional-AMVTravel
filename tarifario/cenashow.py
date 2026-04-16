import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cena Show - Flujo Funcional Completo")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Flujo de prueba siguiendo los 9 pasos definidos:
1. Login.
2. Navegación a Cena Show.
3. Filtro por Cachi.
4. Validación de resultados.
5. Verificación de botón 'Ver Tarifario'.
6. Apertura y verificación de botón 'Cerrar Tarifario'.
7. Validación de tabla de tarifas.
8. Cierre y verificación de retorno a botón 'Ver Tarifario'.
9. Validación de iconos y tooltips.
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
        time.sleep(1.5)

    def obtener_texto_boton_js():
        # Busca cualquier link que contenga 'tarifario' para extraer su texto real
        return driver.execute_script("""
            var links = document.querySelectorAll('a');
            for (var i=0; i<links.length; i++) {
                var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                if (text.includes('tarifario')) return links[i].innerText.trim();
            }
            return "";
        """)

    try:
        # 1. Login (Ya manejado por el fixture logged_in_driver)

        # 2. Click en botón de Cena Show
        with allure.step("2. Navegar a solapa Cena Show"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()
            
            btn_cenashow = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#show"]')))
            driver.execute_script("arguments[0].click();", btn_cenashow)
            esperar_fin_de_carga()
            allure.attach(driver.get_screenshot_as_png(), name="Step_2_CenaShow", attachment_type=allure.attachment_type.PNG)

        # 3. Filtrar la ciudad de Cachi
        with allure.step("3. Filtrar por ciudad Cachi"):
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
            allure.attach(driver.get_screenshot_as_png(), name="Step_3_Filtro_Cachi", attachment_type=allure.attachment_type.PNG)

        # 4. Validar el resultado de esa búsqueda
        with allure.step("4. Validar resultados de búsqueda"):
            # Verificamos que al menos exista un resultado o el contenedor de resultados
            container = wait.until(EC.presence_of_element_located((By.ID, "show")))
            assert container.is_displayed(), "No se visualiza el contenedor de resultados de Cena Show."
            allure.attach(driver.get_screenshot_as_png(), name="Step_4_Resultados_Busqueda", attachment_type=allure.attachment_type.PNG)

        # 5. Validar que el botón se llame Ver Tarifario
        with allure.step("5. Validar texto 'Ver Tarifario'"):
            texto_btn = obtener_texto_boton_js()
            assert "ver tarifario" in texto_btn.lower(), f"Se esperaba 'Ver Tarifario', se encontró: '{texto_btn}'"
            allure.attach(driver.get_screenshot_as_png(), name="Step_5_Boton_Ver", attachment_type=allure.attachment_type.PNG)

        # 6. Clickear ese botón y validar que exista el botón Cerrar Tarifario
        with allure.step("6. Click en Ver y validar cambio a 'Cerrar Tarifario'"):
            btn_accion = wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    if (links[i].innerText.toLowerCase().includes('tarifario')) return links[i];
                }
            """))
            driver.execute_script("arguments[0].click();", btn_accion)
            esperar_fin_de_carga()
            
            texto_despues = obtener_texto_boton_js()
            assert "cerrar tarifario" in texto_despues.lower(), f"El botón no cambió a 'Cerrar', dice: '{texto_despues}'"
            allure.attach(driver.get_screenshot_as_png(), name="Step_6_Boton_Cerrar", attachment_type=allure.attachment_type.PNG)

        # 7. Validar la tabla de tarifario
        with allure.step("7. Validar existencia de tabla de tarifas"):
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table[class*='table-bordered'][class*='table-striped']"
            )))
            p_tariffs = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(p_tariffs) > 0, "Tabla abierta pero sin elementos pTariff."
            allure.attach(driver.get_screenshot_as_png(), name="Step_7_Tabla_Tarifas", attachment_type=allure.attachment_type.PNG)

        # 8. Clickear en Cerrar Tarifario y validar que exista el botón Ver Tarifario
        with allure.step("8. Click en Cerrar y validar retorno a 'Ver Tarifario'"):
            btn_cerrar = wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    if (links[i].innerText.toLowerCase().includes('cerrar')) return links[i];
                }
            """))
            driver.execute_script("arguments[0].click();", btn_cerrar)
            time.sleep(2) # Tiempo para la animación de cierre
            
            texto_final = obtener_texto_boton_js()
            assert "ver tarifario" in texto_final.lower(), f"El botón no volvió a 'Ver', dice: '{texto_final}'"
            allure.attach(driver.get_screenshot_as_png(), name="Step_8_Boton_Ver_Vuelta", attachment_type=allure.attachment_type.PNG)

        # 9. Validar los iconos y los tooltips
        with allure.step("9. Validar iconos y tooltips"):
            icono_reloj = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            actions.move_to_element(icono_reloj).pause(1.5).perform()
            
            tooltip = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(., 'Duración estimada')]")))
            assert tooltip.is_displayed(), "El tooltip de duración no apareció."
            allure.attach(driver.get_screenshot_as_png(), name="Step_9_Tooltips", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR_PASO_FALLIDO", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Fallo en el flujo: {str(e)}")
