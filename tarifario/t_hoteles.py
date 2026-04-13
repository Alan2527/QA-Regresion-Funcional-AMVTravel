import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Hoteles Completa (Tags, Tarifas y Modales)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Hoteles:
1. Login y navegación a la solapa Hoteles.
2. Búsqueda con destino Cachi.
3. Validación estática del Tag "Hotel Recomendado".
4. Validación del estado inicial del botón Ver Tarifario.
5. Apertura del panel principal, sub-acordeón de habitaciones y tabla de tarifas.
6. Cierre del panel y validación del retorno al estado inicial.
7. Validación del modal "Ver Proveedores".
8. Validación del modal "Ver Detalle" (Solución al clic del modal dinámico).
""")
def test_tarifario_hoteles(logged_in_driver):
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
        with allure.step("1 a 2. Navegar a Tarifario y solapa Hoteles"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_hoteles = wait.until(EC.element_to_be_clickable((By.ID, "a-hotels")))
            driver.execute_script("arguments[0].click();", btn_hoteles)
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
        # BLOQUE 1: ELEMENTOS ESTÁTICOS
        # ==========================================
        with allure.step("4. Validar tag 'Hotel Recomendado'"):
            tag_recomendado = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.featured-tag")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tag_recomendado)
            assert tag_recomendado.is_displayed()

        # ==========================================
        # BLOQUE 2: CICLO DE VIDA DEL PANEL
        # ==========================================
        with allure.step("5. Validar estado inicial Ver Tarifario"):
            boton_ver = buscar_boton_ver()
            assert check_icono(boton_ver, "down")

        with allure.step("6. Click en Ver Tarifario"):
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)

        with allure.step("7. Desplegar habitación y validar tabla"):
            btn_habitacion = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[id^='accordeon-header-']")))
            driver.execute_script("arguments[0].click();", btn_habitacion)
            time.sleep(2) 

            tabla = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table-bordered")))
            assert len(tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")) > 0

        with allure.step("8. Cerrar Tarifario"):
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2)

        # ==========================================
        # BLOQUE 3: MODALES (INDEPENDIENTES)
        # ==========================================
        with allure.step("10. Modal Proveedores"):
            btn_prov = wait.until(EC.presence_of_element_located((
                By.XPATH, "//button[contains(text(), 'Ver Proveedores')]"
            )))
            driver.execute_script("arguments[0].click();", btn_prov)
            modal_prov = wait.until(EC.visibility_of_element_located((By.ID, "suppliersModal")))
            assert any(td.text.strip() != "" for td in modal_prov.find_elements(By.TAG_NAME, "td"))
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1.5)

        with allure.step("11. Click en Ver Detalle y validar modal"):
            # Usamos un selector basado en texto para mayor flexibilidad
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(translate(text(), 'VER DETALLE', 'ver detalle'), 'ver detalle')]"
            )))
            
            # Forzamos el clic por JS para asegurar que el evento onclick del modal se dispare
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            time.sleep(1) 
            driver.execute_script("arguments[0].click();", btn_detalle)

            # Esperamos a que el modal se haga visible (contemplando clases dinámicas)
            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal.show div.modal-content, div.modal.in div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle no se renderizó."
            allure.attach(driver.get_screenshot_as_png(), name="7_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)
            actions.send_keys(Keys.ESCAPE).perform()

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Test", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"Fallo: {str(e)}")
