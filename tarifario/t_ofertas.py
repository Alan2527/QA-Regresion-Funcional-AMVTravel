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
        # 4 Modal (FIX REAL)
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):

            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(., 'Ver detalle')]"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", btn_detalle)

            # Esperar que el modal exista
            modal = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))

            # Esperar que sea visible
            wait.until(EC.visibility_of(modal))

            # Esperar animación bootstrap (fade show)
            wait.until(lambda d: "show" in modal.find_element(
                By.XPATH, "./ancestor::div[contains(@class,'modal')]"
            ).get_attribute("class"))

            assert modal.is_displayed(), "El modal no se mostró correctamente"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()

            # Esperar que cierre
            wait.until(EC.invisibility_of_element(modal))

        # =========================
        # 5 Toggle VALIDACIÓN EXACTA
        # =========================
        with allure.step("5. Validar toggle Ver/Cerrar Tarifario"):

            SELECTOR_BTN = "a.accordeon-header.tariff-detail.tariff-view-table.toggle-asigned"

            def get_btn():
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_BTN)))

            def get_text(btn):
                return btn.text.strip()

            def has_icon(btn, icon_class):
                try:
                    btn.find_element(By.CSS_SELECTOR, f"i.{icon_class.replace(' ', '.')}")
                    return True
                except:
                    return False

            # -------- ESTADO INICIAL --------
            btn = get_btn()

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(1)

            assert get_text(btn) == "Ver Tarifario", f"Texto incorrecto: {get_text(btn)}"
            assert has_icon(btn, "zmdi zmdi-chevron-down"), "Falta ícono flecha abajo"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Ver_Tarifario_OK",
                attachment_type=allure.attachment_type.PNG
            )

            # -------- CLICK → CERRAR --------
            driver.execute_script("arguments[0].click();", btn)

            wait.until(EC.staleness_of(btn))
            esperar_fin_de_carga()

            btn = get_btn()

            assert get_text(btn) == "Cerrar Tarifario", f"Texto incorrecto: {get_text(btn)}"
            assert has_icon(btn, "zmdi zmdi-chevron-up"), "Falta ícono flecha arriba"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Cerrar_Tarifario_OK",
                attachment_type=allure.attachment_type.PNG
            )

            # -------- CLICK → VOLVER A VER --------
            driver.execute_script("arguments[0].click();", btn)

            wait.until(EC.staleness_of(btn))
            esperar_fin_de_carga()

            btn = get_btn()

            assert get_text(btn) == "Ver Tarifario", f"Texto incorrecto: {get_text(btn)}"
            assert has_icon(btn, "zmdi zmdi-chevron-down"), "No volvió flecha abajo"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Vuelve_Ver_Tarifario_OK",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 6 Acordeón
        # =========================
        with allure.step("6. Apertura del acordeón y validación de tarifas"):

            btn_acordeon = wait.until(EC.element_to_be_clickable((
                By.ID, "accordeon-header-bfce9d58-98a4-4fe6-b706-6aa2e6e52730"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_acordeon)
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
                name="6_Detalle_Oferta_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )

        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
