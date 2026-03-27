import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@allure.feature("Tarifario")
@allure.story("Consulta de Excursiones")
def test_tarifario_excursiones(logged_in_driver):

    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)

    def esperar_fin_de_carga():
        time.sleep(2)
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        except:
            pass

    try:
        # =========================
        # Navegación
        # =========================
        with allure.step("Ir a Tarifario > Excursiones"):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"))).click()
            esperar_fin_de_carga()

            wait.until(EC.element_to_be_clickable((By.ID, "a-excursions"))).click()
            esperar_fin_de_carga()

        # =========================
        # Buscar excursiones
        # =========================
        with allure.step("Buscar excursión"):
            btn_buscar = wait.until(EC.element_to_be_clickable((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            btn_buscar.click()

            esperar_fin_de_carga()

        # =========================
        # Entrar a detalle
        # =========================
        with allure.step("Abrir detalle"):
            btn_excursion = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            btn_excursion.click()

            esperar_fin_de_carga()

        # =========================
        # Validar tabla
        # =========================
        with allure.step("Validar tarifas"):
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table"
            )))

            assert tabla.is_displayed()

        # =========================
        # Click proveedores (FIX REAL)
        # =========================
        with allure.step("Abrir proveedores"):

            btn_proveedores = wait.until(EC.presence_of_element_located((
                By.XPATH, "//button[contains(@onclick,'openSuppliersModal')]"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_proveedores)
            time.sleep(1)

            # 🔥 MULTI-ESTRATEGIA (ANTI FLAKY)
            try:
                btn_proveedores.click()
            except:
                try:
                    ActionChains(driver).move_to_element(btn_proveedores).click().perform()
                except:
                    driver.execute_script("arguments[0].click();", btn_proveedores)

            esperar_fin_de_carga()

            # Validar modal
            tabla_proveedores = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.suppliers-table"
            )))

            assert tabla_proveedores.is_displayed()

        allure.attach(driver.get_screenshot_as_png(), name="OK", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="ERROR", attachment_type=allure.attachment_type.PNG)
        raise e
