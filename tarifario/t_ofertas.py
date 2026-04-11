import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Ofertas Completa (Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Ofertas:
1. Login y navegación a la solapa Ofertas.
2. Búsqueda con destino Buenos Aires.
3. Validación del modal "Ver Detalle".
4. Ingreso al detalle de la oferta (con validación de toggle Ver/Cerrar).
5. Apertura del acordeón específico y validación de la tabla de tarifas.
""")
def test_tarifario_ofertas(logged_in_driver):
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

    try:
        # =========================
        # Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Ofertas"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_ofertas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#opportunity"]')))
            driver.execute_script("arguments[0].click();", btn_ofertas)
            esperar_fin_de_carga()

        # =========================
        # Filtro y búsqueda
        # =========================
        with allure.step("3. Buscar ofertas en Buenos Aires"):
            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Ofertas_BUE",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Validación Modal "Ver Detalle"
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')] | //a[contains(@class, 'tariff-op-detail-btn')]"
            )))
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle de la oferta no se renderizó."
            time.sleep(1)

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # =========================
        # Detalle Oferta y Acordeón (Tarifario)
        # =========================
        with allure.step("5. Ingresar al detalle de la oferta y validar botón Ver/Cerrar"):
            btn_oferta = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_oferta)
            time.sleep(1)
            
            # --- INICIO NUEVA VALIDACIÓN: TOGGLE BOTÓN VER/CERRAR TARIFARIO ---
            texto_inicial = btn_oferta.text.strip().lower()
            assert "ver" in texto_inicial, f"Error: El botón inicialmente dice '{texto_inicial}' en vez de 'Ver...'"

            # Primer Clic: Abrir
            driver.execute_script("arguments[0].click();", btn_oferta)
            esperar_fin_de_carga()
            
            # Espera dinámica: aguanta hasta que el texto del botón cambie (max 15s por el WebDriverWait global)
            wait.until(lambda d: "cerrar" in btn_oferta.text.strip().lower())
            time.sleep(1) # Pausa extra por estabilidad de renderizado

            texto_abierto = btn_oferta.text.strip().lower()
            assert "cerrar" in texto_abierto, f"Error: El botón no cambió a 'Cerrar...', dice '{texto_abierto}'"

            # Segundo Clic: Cerrar
            driver.execute_script("arguments[0].click();", btn_oferta)
            
            # Espera dinámica: aguanta hasta que vuelva a decir 'ver'
            wait.until(lambda d: "ver" in btn_oferta.text.strip().lower())
            time.sleep(1)

            texto_cerrado = btn_oferta.text.strip().lower()
            assert "ver" in texto_cerrado, f"Error: El botón no volvió a 'Ver...', quedó en '{texto_cerrado}'"

            # Tercer Clic: Volver a abrir para continuar la prueba
            driver.execute_script("arguments[0].click();", btn_oferta)
            esperar_fin_de_carga()
            wait.until(lambda d: "cerrar" in btn_oferta.text.strip().lower())
            time.sleep(1)
            # --- FIN NUEVA VALIDACIÓN ---

        with allure.step("6. Apertura del acordeón específico y validación de tarifas"):
            # Buscamos el acordeón específico solicitado por ID
            btn_acordeon = wait.until(EC.element_to_be_clickable((
                By.ID, "accordeon-header-bfce9d58-98a4-4fe6-b706-6aa2e6e52730"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_acordeon)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_acordeon)
            
            # Esperamos a que la animación de Bootstrap despliegue el acordeón
            time.sleep(2)

            # Validamos la tabla de tarifas ahora que es visible
            tabla_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(p_tariffs) > 0, "No se encontró ningún elemento pTariff en la tabla de la oferta."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Detalle_Oferta_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
