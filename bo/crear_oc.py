import pytest
import allure
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def safe_send_keys(wait, locator, value, retries=3):
    """Reintenta interacción para evitar stale element"""
    for i in range(retries):
        try:
            elem = wait.until(EC.element_to_be_clickable(locator))
            elem.click()
            elem.clear()
            elem.send_keys(value)
            return
        except StaleElementReferenceException:
            if i == retries - 1:
                raise
            time.sleep(1)


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
        driver.set_window_size(1936, 1048)

        user = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not user or not password:
            pytest.fail("Faltan variables")

        wait.until(EC.visibility_of_element_located((By.ID, "txtUser"))).send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()

        wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))
        allure.attach(driver.get_screenshot_as_png(), "1_Login", allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN
    # ==========================================
    with allure.step("2. Navegación"):
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".open li:nth-child(3) span"))).click()

        allure.attach(driver.get_screenshot_as_png(), "2_Navegacion", allure.attachment_type.PNG)

    # ==========================================
    # 3. NUEVO
    # ==========================================
    with allure.step("3. Nuevo"):
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Nuevo"))).click()
        allure.attach(driver.get_screenshot_as_png(), "3_Nuevo", allure.attachment_type.PNG)

    # ==========================================
    # 4. COMBOS
    # ==========================================
    with allure.step("4. PaymentRef"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs"))))\
            .select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")

    with allure.step("5. Currency"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency"))))\
            .select_by_visible_text("USD")

        allure.attach(driver.get_screenshot_as_png(), "4_Combos", allure.attachment_type.PNG)

    # ==========================================
    # 5. CLIENTE
    # ==========================================
    with allure.step("6. Abrir modal cliente"):
        try:
            driver.execute_script("arguments[0].click();",
                                  wait.until(EC.presence_of_element_located((By.ID, "txtCustomer"))))
        except:
            pass

        try:
            driver.execute_script("arguments[0].click();",
                                  driver.find_element(By.CSS_SELECTOR, ".icon-magnifier"))
        except:
            pass

    with allure.step("7. Buscar cliente"):
        search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        search.clear()
        search.send_keys("hectours")

    with allure.step("8. Seleccionar cliente"):
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dataCustomers tbody tr")))

        fila = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[@id='dataCustomers']/tbody/tr/td[2][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'hectours')]"
        )))

        driver.execute_script("arguments[0].click();", fila)

        # 🔥 CLAVE: esperar refresh del DOM
        time.sleep(2)

        allure.attach(driver.get_screenshot_as_png(), "5_Cliente", allure.attachment_type.PNG)

    # ==========================================
    # 6. DATOS (SEPARADO + ROBUSTO)
    # ==========================================

    with allure.step("9. Seleccionar caja"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1"))))\
            .select_by_visible_text("CAJA CHICA U$D")

    with allure.step("10. Ingresar detalle"):
        safe_send_keys(wait, (By.ID, "txtDetail"), "Test automático")

    with allure.step("11. Ingresar monto"):
        safe_send_keys(wait, (By.ID, "txtAmount1"), "2000")

        allure.attach(driver.get_screenshot_as_png(), "6_Datos", allure.attachment_type.PNG)

    # ==========================================
    # 7. GUARDAR
    # ==========================================
    with allure.step("12. Guardar"):
        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnSave"))))
        time.sleep(3)

        allure.attach(driver.get_screenshot_as_png(), "7_Guardado", allure.attachment_type.PNG)

    # ==========================================
    # 8. IMPUTAR
    # ==========================================
    with allure.step("13. Imputar"):
        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((
                                  By.CSS_SELECTOR,
                                  "#ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending_ctrl4_lnkAsignarTotal > .icon-check"
                              ))))
        time.sleep(2)

        allure.attach(driver.get_screenshot_as_png(), "8_Imputado", allure.attachment_type.PNG)

    # ==========================================
    # 9. APROBAR
    # ==========================================
    with allure.step("14. Aprobar"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))).click()

        wait.until(EC.element_to_be_clickable((By.ID, "txtReceiptDate"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(5) > .day:nth-child(2)"))).click()

        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))))

        time.sleep(3)
        allure.attach(driver.get_screenshot_as_png(), "9_Aprobado", allure.attachment_type.PNG)
