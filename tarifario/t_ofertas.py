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
        # 1-2 Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Ofertas"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_ofertas = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'a[href="#opportunity"]'
            )))
            driver.execute_script("arguments[0].click();", btn_ofertas)
            esperar_fin_de_carga()

        # =========================
        # 3 Búsqueda
        # =========================
        with allure.step("3. Buscar ofertas en Buenos Aires"):
            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", btn_buscar)
            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Ofertas_BUE",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 4 Modal
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(., 'Ver detalle')]"
            )))

            driver.execute_script("arguments[0].click();", btn_detalle)

            modal = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))

            assert modal.is_displayed(), "El modal no se mostró"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # =========================
        # 5 Toggle REAL (FIX)
        # =========================
        with allure.step("5. Ingresar al detalle de la oferta y validar botón Ver/Cerrar"):

            # BOTÓN VER
            btn_ver = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(., 'Ver Tarifario')]"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_ver)
            time.sleep(1)

            # CLICK → abrir
            driver.execute_script("arguments[0].click();", btn_ver)
            esperar_fin_de_carga()

            # VALIDAR → aparece CERRAR
            btn_cerrar = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//a[contains(., 'Cerrar Tarifario')]"
            )))

            assert btn_cerrar.is_displayed(), "No apareció 'Cerrar Tarifario'"

            # CLICK → cerrar
            driver.execute_script("arguments[0].click();", btn_cerrar)

            # VALIDAR → vuelve VER
            wait.until(EC.visibility_of_element_located((
                By.XPATH, "//a[contains(., 'Ver Tarifario')]"
            )))

            # CLICK → abrir otra vez
            btn_ver = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(., 'Ver Tarifario')]"
            )))
            driver.execute_script("arguments[0].click();", btn_ver)

            wait.until(EC.visibility_of_element_located((
                By.XPATH, "//a[contains(., 'Cerrar Tarifario')]"
            )))

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Toggle_Ver_Cerrar",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 6 Acordeón
        # =========================
        with allure.step("6. Apertura del acordeón específico y validación de tarifas"):
            btn_acordeon = wait.until(EC.element_to_be_clickable((
                By.ID, "accordeon-header-bfce9d58-98a4-4fe6-b706-6aa2e6e52730"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_acordeon)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", btn_acordeon)
            time.sleep(2)

            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))

            tarifas = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(tarifas) > 0, "No hay tarifas en la tabla"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Detalle_Oferta_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
