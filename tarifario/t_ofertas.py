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
        # HELPERS INFALIBLES PARA EL PASO 5
        # =========================
        # Usamos un XPath que busca el primer enlace con clase 'tariff-detail'. 
        # Esto ignora clases tramposas como 'toggle-asigned' que aparecen y desaparecen.
        def get_btn_tarifario():
            return wait.until(EC.presence_of_element_located((By.XPATH, "(//a[contains(@class, 'tariff-detail')])[1]")))

        def get_texto_tarifario():
            return driver.execute_script("return arguments[0].textContent;", get_btn_tarifario()).strip()

        # =========================
        # 5.1 Validar estado inicial Ver Tarifario
        # =========================
        with allure.step("5.1. Validar que el botón tenga el texto Ver Tarifario y el icono chevron-down"):
            
            boton = get_btn_tarifario()
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
            time.sleep(1)

            assert "Ver Tarifario" in get_texto_tarifario(), f"Texto incorrecto: {get_texto_tarifario()}"
            
            # Usamos find_elements (en plural) que devuelve una lista. Si está vacía, falla.
            iconos_down = boton.find_elements(By.XPATH, ".//i[contains(@class, 'zmdi-chevron-down')]")
            assert len(iconos_down) > 0, "Falta el ícono zmdi-chevron-down"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Paso1_Ver_Tarifario_Inicial",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 5.2 Clickear en ese a
        # =========================
        with allure.step("5.2. Clickear en el botón Ver Tarifario"):
            driver.execute_script("arguments[0].click();", get_btn_tarifario())
            # Pausa CLAVE de 2 segundos para que la animación de apertura en GitHub Actions termine
            time.sleep(2)

        # =========================
        # 5.3 Validar estado Cerrar Tarifario
        # =========================
        with allure.step("5.3. Validar que el botón tenga el texto Cerrar Tarifario y el icono chevron-up"):
            
            # Esperamos a que el texto cambie
            wait.until(lambda d: "Cerrar Tarifario" in get_texto_tarifario(), message="El texto nunca cambió a Cerrar Tarifario")
            
            assert "Cerrar Tarifario" in get_texto_tarifario(), f"Texto incorrecto: {get_texto_tarifario()}"
            
            iconos_up = get_btn_tarifario().find_elements(By.XPATH, ".//i[contains(@class, 'zmdi-chevron-up')]")
            assert len(iconos_up) > 0, "Falta el ícono zmdi-chevron-up"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Paso3_Cerrar_Tarifario",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 5.4 Clickear en ese a nuevamente
        # =========================
        with allure.step("5.4. Clickear en el botón Cerrar Tarifario"):
            driver.execute_script("arguments[0].click();", get_btn_tarifario())
            time.sleep(2)

        # =========================
        # 5.5 Validar estado Ver Tarifario
        # =========================
        with allure.step("5.5. Validar que el botón vuelva a tener el texto Ver Tarifario y el icono chevron-down"):
            
            wait.until(lambda d: "Ver Tarifario" in get_texto_tarifario(), message="El texto nunca volvió a Ver Tarifario")
            
            assert "Ver Tarifario" in get_texto_tarifario(), f"Texto incorrecto: {get_texto_tarifario()}"
            
            iconos_down_final = get_btn_tarifario().find_elements(By.XPATH, ".//i[contains(@class, 'zmdi-chevron-down')]")
            assert len(iconos_down_final) > 0, "Falta el ícono zmdi-chevron-down al volver al estado inicial"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Paso5_Vuelve_Ver_Tarifario",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
