import pytest
import allure
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


@allure.feature("Tesorería BackOffice")
@allure.story("Crear Orden de Cobro")
@allure.severity(allure.severity_level.CRITICAL)
def test_crear_orden_cobro(driver):
    wait = WebDriverWait(driver, 15)

    # ==========================================
    # 1. LOGIN
    # ==========================================
    with allure.step("1. Login en el BackOffice"):
        driver.get("https://qa.bo.amv.travel/login")
        driver.set_window_size(1936, 1048)

        usuario = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not usuario or not password:
            pytest.fail("Faltan variables de entorno")

        wait.until(EC.visibility_of_element_located((By.ID, "txtUser"))).send_keys(usuario)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()

        wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))
        allure.attach(driver.get_screenshot_as_png(), name="1_Login", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN
    # ==========================================
    with allure.step("2. Navegación"):
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".open li:nth-child(3) span"))).click()

        allure.attach(driver.get_screenshot_as_png(), name="2_Navegacion", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 3. NUEVO
    # ==========================================
    with allure.step("3. Nuevo"):
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Nuevo"))).click()

        allure.attach(driver.get_screenshot_as_png(), name="3_Nuevo", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 4. COMBOS
    # ==========================================
    with allure.step("4. Combos"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs"))))\
            .select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")

        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency"))))\
            .select_by_visible_text("USD")

        allure.attach(driver.get_screenshot_as_png(), name="4_Combos", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 5. CLIENTE
    # ==========================================
    with allure.step("5. Cliente"):
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

        search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search'])))
        search.send_keys("hectours")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dataCustomers tbody tr")))

        fila = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[@id='dataCustomers']/tbody/tr/td[2][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'hectours')]"
        )))

        driver.execute_script("arguments[0].click();", fila)

        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="5_Cliente", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 6. DATOS (FIX STALE)
    # ==========================================
    with allure.step("6. Datos"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1"))))\
            .select_by_visible_text("CAJA CHICA U$D")

        wait.until(EC.visibility_of_element_located((By.ID, "txtDetail"))).send_keys("Test automático")

        # 🔥 FIX CLAVE: re-buscar el input después del refresh del DOM
        wait.until(EC.presence_of_element_located((By.ID, "txtAmount1")))
        monto = wait.until(EC.element_to_be_clickable((By.ID, "txtAmount1")))

        monto.click()
        monto.clear()
        monto.send_keys("2000")

        allure.attach(driver.get_screenshot_as_png(), name="6_Datos", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 7. GUARDAR
    # ==========================================
    with allure.step("7. Guardar"):
        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnSave"))))

        time.sleep(3)
        allure.attach(driver.get_screenshot_as_png(), name="7_Guardado", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 8. IMPUTAR
    # ==========================================
    with allure.step("8. Imputar"):
        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((
                                  By.CSS_SELECTOR,
                                  "#ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending_ctrl4_lnkAsignarTotal > .icon-check"
                              ))))

        time.sleep(2)
        allure.attach(driver.get_screenshot_as_png(), name="8_Imputado", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 9. APROBAR
    # ==========================================
    with allure.step("9. Aprobar"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))).click()

        wait.until(EC.element_to_be_clickable((By.ID, "txtReceiptDate"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(5) > .day:nth-child(2)"))).click()

        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))))

        time.sleep(3)
        allure.attach(driver.get_screenshot_as_png(), name="9_Aprobado", attachment_type=allure.attachment_type.PNG)
