import pytest
import allure
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException


# =========================
# HELPERS ROBUSTOS
# =========================

def safe_click(wait, locator):
    for _ in range(5):
        try:
            elem = wait.until(EC.element_to_be_clickable(locator))
            elem.click()
            return
        except StaleElementReferenceException:
            time.sleep(1)
    raise Exception(f"No se pudo hacer click: {locator}")


def safe_send_keys(wait, locator, value):
    for _ in range(5):
        try:
            elem = wait.until(EC.visibility_of_element_located(locator))

            # Scroll al elemento
            wait._driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            time.sleep(0.5)

            elem.clear()
            elem.send_keys(value)
            return

        except (StaleElementReferenceException, ElementNotInteractableException):
            try:
                # 🔥 fallback JS
                elem = wait.until(EC.presence_of_element_located(locator))
                wait._driver.execute_script("arguments[0].value = arguments[1];", elem, value)
                return
            except:
                time.sleep(1)

    raise Exception(f"No se pudo escribir en: {locator}")


def wait_table_rows(wait, table_id):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"{table_id} tbody tr")))


# =========================
# TEST
# =========================

@allure.feature("Tesorería BackOffice")
@allure.story("Crear Orden de Cobro")
@allure.severity(allure.severity_level.CRITICAL)
def test_crear_orden_cobro(driver):

    wait = WebDriverWait(driver, 25)

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
        allure.attach(driver.get_screenshot_as_png(), "1_Login", allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN
    # ==========================================
    with allure.step("2. Navegación"):
        safe_click(wait, (By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span"))
        safe_click(wait, (By.CSS_SELECTOR, ".open li:nth-child(3) span"))

        allure.attach(driver.get_screenshot_as_png(), "2_Navegacion", allure.attachment_type.PNG)

    # ==========================================
    # 3. NUEVO
    # ==========================================
    with allure.step("3. Nuevo"):
        safe_click(wait, (By.LINK_TEXT, "Nuevo"))
        allure.attach(driver.get_screenshot_as_png(), "3_Nuevo", allure.attachment_type.PNG)

    # ==========================================
    # 4. PAYMENT REF
    # ==========================================
    with allure.step("4. PaymentRef"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs"))))\
            .select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")

        allure.attach(driver.get_screenshot_as_png(), "4_PaymentRef", allure.attachment_type.PNG)

    # ==========================================
    # 5. CURRENCY
    # ==========================================
    with allure.step("5. Currency"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency"))))\
            .select_by_visible_text("USD")

        allure.attach(driver.get_screenshot_as_png(), "5_Currency", allure.attachment_type.PNG)

    # ==========================================
    # 6. ABRIR MODAL
    # ==========================================
    with allure.step("6. Abrir modal cliente"):
        safe_click(wait, (By.ID, "txtCustomer"))

        try:
            safe_click(wait, (By.CSS_SELECTOR, ".icon-magnifier"))
        except:
            pass

        allure.attach(driver.get_screenshot_as_png(), "6_Modal", allure.attachment_type.PNG)

    # ==========================================
    # 7. BUSCAR
    # ==========================================
    with allure.step("7. Buscar cliente"):
        search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        search.clear()
        search.send_keys("hectours")

        allure.attach(driver.get_screenshot_as_png(), "7_Busqueda", allure.attachment_type.PNG)

    # ==========================================
    # 8. SELECCIONAR CLIENTE
    # ==========================================
    with allure.step("8. Seleccionar cliente"):
        wait_table_rows(wait, "#dataCustomers")

        fila = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[@id='dataCustomers']//td[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'hectours')]"
        )))

        driver.execute_script("arguments[0].click();", fila)

        # 🔥 esperar que cierre el modal
        wait.until(EC.invisibility_of_element_located((By.ID, "dataCustomers")))

        allure.attach(driver.get_screenshot_as_png(), "8_Cliente", allure.attachment_type.PNG)

    # ==========================================
    # 9. CAJA
    # ==========================================
    with allure.step("9. Caja"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1"))))\
            .select_by_visible_text("CAJA CHICA U$D")

        allure.attach(driver.get_screenshot_as_png(), "9_Caja", allure.attachment_type.PNG)

    # ==========================================
    # 10. DETALLE
    # ==========================================
    with allure.step("10. Detalle"):
        safe_send_keys(wait, (By.ID, "txtDetail"), "Test automático")

        allure.attach(driver.get_screenshot_as_png(), "10_Detalle", allure.attachment_type.PNG)

    # ==========================================
    # 11. MONTO
    # ==========================================
    with allure.step("11. Monto"):
        safe_send_keys(wait, (By.ID, "txtAmount1"), "2000")

        allure.attach(driver.get_screenshot_as_png(), "11_Monto", allure.attachment_type.PNG)

    # ==========================================
    # 12. GUARDAR
    # ==========================================
    with allure.step("12. Guardar"):
        safe_click(wait, (By.ID, "btnSave"))
        time.sleep(3)

        allure.attach(driver.get_screenshot_as_png(), "12_Guardado", allure.attachment_type.PNG)

    # ==========================================
    # 13. SCROLL A TABLA
    # ==========================================
    with allure.step("13. Scroll a tabla imputación"):

        tabla = wait.until(EC.presence_of_element_located((By.ID, "tblChargeOrderAllocation")))

        driver.execute_script("arguments[0].scrollIntoView(true);", tabla)
        time.sleep(2)

        allure.attach(driver.get_screenshot_as_png(), "13_Scroll", allure.attachment_type.PNG)

    # ==========================================
    # 14. VALIDAR Y CLICK BOTON FILA
    # ==========================================
    with allure.step("14. Click en botón de imputación"):

        # validar td esperado
        td = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "#tblChargeOrderAllocation td.text-center.sorting_1"
        )))

        # buscar botón dentro del td
        boton = td.find_element(By.CSS_SELECTOR, "a.btn.btn-sm.usepreload")

        driver.execute_script("arguments[0].click();", boton)

        # esperar carga (loader / cambio DOM)
        time.sleep(3)

        allure.attach(driver.get_screenshot_as_png(), "14_Click_Fila", allure.attachment_type.PNG)

    # ==========================================
    # 15. VALIDAR TABLA INTERNA
    # ==========================================
    with allure.step("15. Validar tabla interna"):

        tabla_interna = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            ".table.table-striped.table-bordered.table-hover.table-condensed.text-center.m-b-0"
        )))

        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            ".table.table-striped.table-bordered.table-hover.table-condensed.text-center.m-b-0 td.text-center"
        )))

        allure.attach(driver.get_screenshot_as_png(), "15_Tabla_Interna", allure.attachment_type.PNG)

    # ==========================================
    # 16. INGRESAR FECHA HOY
    # ==========================================
    from datetime import datetime

    with allure.step("16. Ingresar fecha actual"):

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        safe_send_keys(wait, (By.ID, "txtReceiptDate"), fecha_hoy)

        allure.attach(driver.get_screenshot_as_png(), "16_Fecha", allure.attachment_type.PNG)

    # ==========================================
    # 17. APROBAR Y APLICAR
    # ==========================================
    with allure.step("17. Aprobar y aplicar recibo"):

        boton_aprobar = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//input[@value='Aprobar & Aplicar Recibo']"
        )))

        driver.execute_script("arguments[0].click();", boton_aprobar)

        # esperar proceso
        time.sleep(4)

        allure.attach(driver.get_screenshot_as_png(), "17_Click_Aprobar", allure.attachment_type.PNG)

    # ==========================================
    # 18. VALIDAR QUE DESAPARECIÓ
    # ==========================================
    with allure.step("18. Validar botón desapareció"):

        wait.until(EC.invisibility_of_element_located((
            By.XPATH,
            "//input[@value='Aprobar & Aplicar Recibo']"
        )))

        allure.attach(driver.get_screenshot_as_png(), "18_Final", allure.attachment_type.PNG)
