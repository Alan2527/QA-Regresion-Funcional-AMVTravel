import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cruceros Completa (Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Cruceros:
1. Login y navegación a la solapa Cruceros.
2. Búsqueda con destino Ushuaia.
3. Validación del modal "Ver Detalle".
4. Ingreso al detalle del crucero (con validación de toggle Ver/Cerrar).
5. Apertura del acordeón (cabinas/salidas) y validación de la tabla de tarifas.
""")
def test_tarifario_cruceros(logged_in_driver):
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

        # Usamos translate() para que la búsqueda ignore mayúsculas y minúsculas (Ushuaia/ushuaia)
        xpath_opcion = f"//div[contains(@class, 'option') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{nuevo_destino.lower()}')]"
        opcion = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opcion)))
        driver.execute_script("arguments[0].click();", opcion)

        esperar_fin_de_carga()

    try:
        # =========================
        # Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Cruceros"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_cruceros = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#cruise"]')))
            driver.execute_script("arguments[0].click();", btn_cruceros)
            esperar_fin_de_carga()

        # =========================
        # Filtro y búsqueda
        # =========================
        with allure.step("3. Cambiar destino a Ushuaia y buscar"):
            # Asumimos que "Buenos Aires" es el destino predeterminado en el dropdown al entrar
            cambiar_destino("Buenos Aires", "Ushuaia")

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Cruceros_Ushuaia",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Validación Modal "Ver Detalle"
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):
            # Contempla tanto el botón primario (estilo hotel) como el estándar (estilo excursión)
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')] | //a[contains(@class, 'tariff-op-detail-btn')]"
            )))
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle del crucero no se renderizó."
            time.sleep(1)

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # =========================
        # Detalle Crucero y Acordeón (Tarifario)
        # =========================
        with allure.step("5. Ingresar al detalle del crucero y validar botón Ver/Cerrar"):
            btn_crucero = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_crucero)
            time.sleep(1)
            
            # --- INICIO NUEVA VALIDACIÓN: TOGGLE BOTÓN VER/CERRAR TARIFARIO ---
            texto_inicial = btn_crucero.text.strip().lower()
            assert "ver" in texto_inicial, f"Error: El botón inicialmente dice '{texto_inicial}' en vez de 'Ver...'"

            driver.execute_script("arguments[0].click();", btn_crucero)
            esperar_fin_de_carga()
            time.sleep(1)

            texto_abierto = btn_crucero.text.strip().lower()
            assert "cerrar" in texto_abierto, f"Error: El botón no cambió a 'Cerrar...', dice '{texto_abierto}'"

            driver.execute_script("arguments[0].click();", btn_crucero)
            time.sleep(1)

            texto_cerrado = btn_crucero.text.strip().lower()
            assert "ver" in texto_cerrado, f"Error: El botón no volvió a 'Ver...', quedó en '{texto_cerrado}'"

            driver.execute_script("arguments[0].click();", btn_crucero)
            esperar_fin_de_carga()
            time.sleep(1)
            # --- FIN NUEVA VALIDACIÓN ---

        with allure.step("6. Apertura del acordeón y validación de tarifas"):
            # Buscamos y abrimos la primera opción del acordeón (dinámico)
            btn_acordeon = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[id^='accordeon-header-']"
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

            assert len(p_tariffs) > 0, "No se encontró ningún elemento pTariff en la tabla del crucero."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Detalle_Crucero_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Cruceros",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
