import time
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Ofertas Completa (Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
def test_tarifario_ofertas(logged_in_driver):

    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(),'CARGANDO','cargando'),'cargando') or contains(@class,'loading')]"
            )))
        except:
            pass

        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof jQuery==='undefined') || (jQuery.active===0);"
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

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_buscar)
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

            XPATH_DETALLE = "//a[@href='javascript:void(0);' and contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')]"

            def get_btn_detalle():
                return wait.until(EC.presence_of_element_located((By.XPATH, XPATH_DETALLE)))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", get_btn_detalle())
            time.sleep(1)

            driver.execute_script("arguments[0].click();", get_btn_detalle())

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))

            time.sleep(1)

            assert modal_detalle.is_displayed(), "El modal de detalle de la oferta no se renderizó."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            wait.until(EC.invisibility_of_element(modal_detalle))
            time.sleep(1)

        # =========================
        # 5 ABRIR LA TARJETA PRINCIPAL (El paso que faltaba)
        # =========================
        with allure.step("5. Expandir la tarjeta principal de la oferta"):
            
            btn_main = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id*='lnk']"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_main)
            time.sleep(1)
            
            # Esto obliga a la web a inyectar el acordeón "Ver Tarifario" en el HTML
            driver.execute_script("arguments[0].click();", btn_main)
            esperar_fin_de_carga()

        # =========================
        # 6 Toggle VALIDACIÓN EXACTA Y TABLA
        # =========================
        with allure.step("6. Validar toggle Ver/Cerrar Tarifario y Tabla"):

            # Ahora el selector sí existe porque ya abrimos la tarjeta
            SELECTOR_BTN = "a.accordeon-header.tariff-detail"

            def get_btn():
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_BTN)))

            def get_text():
                return get_btn().get_attribute("textContent").strip()

            def has_icon(icon_class):
                try:
                    get_btn().find_element(By.CSS_SELECTOR, f"i.{icon_class.replace(' ', '.')}")
                    return True
                except:
                    return False

            # -------- ESTADO INICIAL --------
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", get_btn())
            time.sleep(1)

            assert get_text() == "Ver Tarifario", f"Texto incorrecto: {get_text()}"
            assert has_icon("zmdi zmdi-chevron-down"), "Falta ícono flecha abajo"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Ver_Tarifario_OK",
                attachment_type=allure.attachment_type.PNG
            )

            # -------- CLICK → CERRAR --------
            driver.execute_script("arguments[0].click();", get_btn())

            wait.until(lambda d: get_text() == "Cerrar Tarifario", message="El botón no cambió a 'Cerrar Tarifario'")
            time.sleep(1)

            assert has_icon("zmdi zmdi-chevron-up"), "Falta ícono flecha arriba"

            # Validamos la tabla ya que está abierto
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))

            tarifas = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(tarifas) > 0, "No hay tarifas en la tabla"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Cerrar_Tarifario_OK_Y_Tabla",
                attachment_type=allure.attachment_type.PNG
            )

            # -------- CLICK → VOLVER A VER --------
            driver.execute_script("arguments[0].click();", get_btn())

            wait.until(lambda d: get_text() == "Ver Tarifario", message="El botón no volvió a 'Ver Tarifario'")
            time.sleep(1)

            assert has_icon("zmdi zmdi-chevron-down"), "No volvió flecha abajo"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Vuelve_Ver_Tarifario_OK",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
