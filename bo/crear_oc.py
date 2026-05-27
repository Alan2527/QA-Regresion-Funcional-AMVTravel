import pytest
import allure
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


# ================================
# HELPERS PRO
# ================================

def safe_click(wait, locator, retries=3):
    for _ in range(retries):
        try:
            elem = wait.until(EC.element_to_be_clickable(locator))
            elem.click()
            return
        except StaleElementReferenceException:
            continue
    raise Exception(f"No se pudo hacer click en {locator}")


def safe_send_keys(wait, locator, value, retries=3):
    for _ in range(retries):
        try:
            elem = wait.until(EC.element_to_be_clickable(locator))
            elem.clear()
            elem.send_keys(value)
            return
        except StaleElementReferenceException:
            continue
    raise Exception(f"No se pudo escribir en {locator}")


def wait_ajax_complete(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_table_rows(wait, table_selector):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector)))
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, f"{table_selector} tbody tr")) > 0)


# ================================
# TEST
# ================================

@allure.feature("Tesorería BackOffice")
@allure.story("Crear Orden de Cobro")
@allure.severity(allure.severity_level.CRITICAL)
def test_crear_orden_cobro(driver):

    wait = WebDriverWait(driver, 20)

    # ==========================================
    # 1. LOGIN
    # ==========================================
    with allure.step("1. Login"):
        driver.get("https://qa.bo.amv.travel/login")

        user = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not user or not password:
            pytest.fail("Faltan variables de entorno")

        safe_send_keys(wait, (By.ID, "txtUser"), user)
        safe_send_keys(wait, (By.ID, "txtPassword"), password)
        safe_click(wait, (By.ID, "btnLogin"))

        wait.until(EC.url_contains("/main"))
        allure.attach(driver.get_screenshot_as_png(), "login", allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN
    # ==========================================
    with allure.step("2. Navegación"):
        safe_click(wait, (By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span"))
        safe_click(wait, (By.CSS_SELECTOR, ".open li:nth-child(3) span"))

        allure.attach(driver.get_screenshot_as_png(), "nav", allure.attachment_type.PNG)

    # ==========================================
    # 3. NUEVO
    # ==========================================
    with allure.step("3. Nuevo"):
        safe_click(wait, (By.LINK_TEXT, "Nuevo"))
        allure.attach(driver.get_screenshot_as_png(), "nuevo", allure.attachment_type.PNG)

    # ==========================================
    # 4. COMBOS
    # ==========================================
    with allure.step("4. PaymentRef"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs"))))\
            .select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")

    with allure.step("5. Currency"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency"))))\
            .select_by_visible_text("USD")

    # ==========================================
    # 5. CLIENTE
    # ==========================================
    with allure.step("6. Abrir modal"):
        safe_click(wait, (By.ID, "txtCustomer"))

        try:
            safe_click(wait, (By.CSS_SELECTOR, ".icon-magnifier"))
        except:
            pass

    with allure.step("7. Buscar cliente"):
        search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        search.clear()
        search.send_keys("hectours")

    with allure.step("8. Seleccionar cliente"):
        wait_table_rows(wait, "#dataCustomers")

        fila = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[@id='dataCustomers']//td[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'hectours')]"
        )))

        driver.execute_script("arguments[0].click();", fila)

        # 🔥 esperar que el modal desaparezca (CLAVE REAL)
        wait.until(EC.invisibility_of_element_located((By.ID, "dataCustomers")))

    # ==========================================
    # 6. DATOS
    # ==========================================
    with allure.step("9. Caja"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1"))))\
            .select_by_visible_text("CAJA CHICA U$D")

    with allure.step("10. Detalle"):
        safe_send_keys(wait, (By.ID, "txtDetail"), "Test automático")

    with allure.step("11. Monto"):
        safe_send_keys(wait, (By.ID, "txtAmount1"), "2000")

        allure.attach(driver.get_screenshot_as_png(), "datos", allure.attachment_type.PNG)

    # ==========================================
    # 7. GUARDAR
    # ==========================================
    with allure.step("12. Guardar"):
        safe_click(wait, (By.ID, "btnSave"))

        # esperar que aparezca sección de imputación
        wait.until(EC.presence_of_element_located((
            By.ID,
            "ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending"
        )))

    # ==========================================
    # 8. IMPUTAR (PRO)
    # ==========================================
    with allure.step("13. Imputar"):

        wait_table_rows(wait, "#ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending")

        botones = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, ".icon-check"))

        if not botones:
            pytest.fail("No hay saldos para imputar")

        driver.execute_script("arguments[0].click();", botones[0])

        allure.attach(driver.get_screenshot_as_png(), "imputado", allure.attachment_type.PNG)

    # ==========================================
    # 9. APROBAR
    # ==========================================
    with allure.step("14. Aprobar"):
        safe_click(wait, (By.ID, "btnApprove"))

        safe_click(wait, (By.ID, "txtReceiptDate"))
        safe_click(wait, (By.CSS_SELECTOR, ".day"))

        safe_click(wait, (By.ID, "btnApprove"))

        allure.attach(driver.get_screenshot_as_png(), "aprobado", allure.attachment_type.PNG)
