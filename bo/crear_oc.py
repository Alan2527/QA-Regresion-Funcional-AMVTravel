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
@allure.description("""
Este test valida el flujo completo de generación, asignación e imputación de una Orden de Cobro:
1. Login administrativo con variables de entorno de forma segura.
2. Navegación al módulo de Orden de Cobro mediante el menú lateral.
3. Configuración de Referencia de Pago, Moneda y selección de Cliente desde modal.
4. Definición de Caja de Flujo, montos y guardado del encabezado.
5. Imputación de saldos pendientes confirmando la asignación total.
6. Aprobación del movimiento definiendo la fecha de recibo en el calendario.
""")
def test_crear_orden_cobro(driver):
    wait = WebDriverWait(driver, 15)

    # ==========================================
    # 1. LOGIN SEGURO
    # ==========================================
    with allure.step("1. Login en el BackOffice"):
        driver.get("https://qa.bo.amv.travel/login")
        driver.set_window_size(1936, 1048)

        usuario = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not usuario or not password:
            pytest.fail("Error de configuración: Faltan las variables de entorno AMV_USER o BO_PASS.")

        wait.until(EC.visibility_of_element_located((By.ID, "txtUser"))).send_keys(usuario)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()

        wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))
        allure.attach(driver.get_screenshot_as_png(), name="1_Login_Exitoso", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN
    # ==========================================
    with allure.step("2. Navegar a Cuentas por Cobrar > Orden de Cobro"):
        menu_tesoreria = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span")))
        menu_tesoreria.click()

        link_orden_cobro = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".open li:nth-child(3) span")))
        link_orden_cobro.click()

        allure.attach(driver.get_screenshot_as_png(), name="2_Bandeja_Ordenes_Cobro", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 3. NUEVO
    # ==========================================
    with allure.step("3. Iniciar creación de Nueva Orden de Cobro"):
        btn_nuevo = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Nuevo")))
        btn_nuevo.click()

        allure.attach(driver.get_screenshot_as_png(), name="3_Formulario_Nuevo", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 4. COMBOS
    # ==========================================
    with allure.step("4. Seleccionar Referencia de Pago y Moneda (USD)"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs")))) \
            .select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")

        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency")))) \
            .select_by_visible_text("USD")

        allure.attach(driver.get_screenshot_as_png(), name="4_Combos_Configurados", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 5. MODAL CLIENTE
    # ==========================================
    with allure.step("5. Buscar y seleccionar Cliente en el modal"):

        # Abrir modal
        try:
            input_customer = wait.until(EC.presence_of_element_located((By.ID, "txtCustomer")))
            driver.execute_script("arguments[0].click();", input_customer)
        except:
            pass

        try:
            lupa = driver.find_element(By.CSS_SELECTOR, ".icon-magnifier")
            driver.execute_script("arguments[0].click();", lupa)
        except:
            pass

        # Buscar input
        selectores = [
            (By.XPATH, "//div[@id='dataCustomers_filter']//input"),
            (By.CSS_SELECTOR, "#dataCustomers_filter .form-control"),
            (By.CSS_SELECTOR, "input[type='search']")
        ]

        search_input = None
        for sel in selectores:
            try:
                search_input = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(sel))
                break
            except:
                continue

        if not search_input:
            allure.attach(driver.get_screenshot_as_png(), name="ERROR_Modal", attachment_type=allure.attachment_type.PNG)
            pytest.fail("No se encontró el buscador del modal")

        # Filtrar
        search_input.click()
        search_input.clear()
        search_input.send_keys("hecto")

        # Esperar tabla cargada
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dataCustomers tbody tr")))

        # Esperar cliente (case insensitive)
        fila_cliente = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//table[@id='dataCustomers']/tbody/tr/td[2][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'hecto')]"
        )))

        driver.execute_script("arguments[0].click();", fila_cliente)

        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="5_Cliente_Seleccionado", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 6. DATOS
    # ==========================================
    with allure.step("6. Completar Tipo de Caja, Detalle y Monto"):
        Select(wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1")))) \
            .select_by_visible_text("CAJA CHICA U$D")

        wait.until(EC.visibility_of_element_located((By.ID, "txtDetail"))).send_keys("Test automático")

        monto = wait.until(EC.visibility_of_element_located((By.ID, "txtAmount1")))
        monto.clear()
        monto.send_keys("2000")

        allure.attach(driver.get_screenshot_as_png(), name="6_Datos", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 7. GUARDAR
    # ==========================================
    with allure.step("7. Guardar encabezado"):
        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnSave"))))
        time.sleep(3)

        allure.attach(driver.get_screenshot_as_png(), name="7_Guardado", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 8. IMPUTAR
    # ==========================================
    with allure.step("8. Imputar saldos"):
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
    with allure.step("9. Aprobar orden"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))).click()

        wait.until(EC.element_to_be_clickable((By.ID, "txtReceiptDate"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(5) > .day:nth-child(2)"))).click()

        driver.execute_script("arguments[0].click();",
                              wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))))

        time.sleep(3)
        allure.attach(driver.get_screenshot_as_png(), name="9_Aprobado", attachment_type=allure.attachment_type.PNG)
