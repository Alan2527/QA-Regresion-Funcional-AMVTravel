import pytest
import allure
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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
    wait = WebDriverWait(driver, 15)  #[cite: 2]

    # ==========================================
    # 1. LOGIN SEGURO
    # ==========================================
    with allure.step("1. Login en el BackOffice"):
        driver.get("https://qa.bo.amv.travel/login")  #[cite: 1, 2]
        driver.set_window_size(1936, 1048)  #[cite: 1]
        
        usuario = os.environ.get("AMV_USER")  #[cite: 2]
        password = os.environ.get("BO_PASS")  #[cite: 2]

        if not usuario or not password:
            pytest.fail("Error de configuración: Faltan las variables de entorno AMV_USER o BO_PASS.")  #[cite: 2]

        wait.until(EC.visibility_of_element_located((By.ID, "txtUser"))).send_keys(usuario)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()  #[cite: 1]
        
        wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))
        allure.attach(driver.get_screenshot_as_png(), name="1_Login_Exitoso", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 2. NAVEGACIÓN MÓDULO TESORERÍA
    # ==========================================
    with allure.step("2. Navegar a Cuentas por Cobrar > Orden de Cobro"):
        menu_tesoreria = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span")))  #[cite: 1]
        menu_tesoreria.click()  #[cite: 1]
        
        link_orden_cobro = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".open li:nth-child(3) span")))  #[cite: 1]
        link_orden_cobro.click()  #[cite: 1]
        allure.attach(driver.get_screenshot_as_png(), name="2_Bandeja_Ordenes_Cobro", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 3. APERTURA DE FORMULARIO
    # ==========================================
    with allure.step("3. Iniciar creación de Nueva Orden de Cobro"):
        btn_nuevo = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Nuevo")))  #[cite: 1]
        btn_nuevo.click()  #[cite: 1]
        allure.attach(driver.get_screenshot_as_png(), name="3_Formulario_Nuevo", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 4. CONFIGURACIÓN DE LISTAS DESPLEGABLES
    # ==========================================
    with allure.step("4. Seleccionar Referencia de Pago y Moneda (USD)"):
        dropdown_refs = wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs")))  #[cite: 1]
        select_refs = Select(dropdown_refs)  #[cite: 2]
        select_refs.select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")  #[cite: 1]

        dropdown_currency = wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency")))  #[cite: 1]
        select_curr = Select(dropdown_currency)  #[cite: 2]
        select_curr.select_by_visible_text("USD")  #[cite: 1]
        allure.attach(driver.get_screenshot_as_png(), name="4_Combos_Configurados", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 5. INTERACCIÓN CON MODAL DE CLIENTES
    # ==========================================
    with allure.step("5. Buscar y seleccionar Cliente en el modal"):
        wait.until(EC.element_to_be_clickable((By.ID, "txtCustomer"))).click()  #[cite: 1]
        
        magnifier = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".icon-magnifier")))  #[cite: 1]
        actions = ActionChains(driver)
        actions.move_to_element(magnifier).perform()  #[cite: 1]
        
        body = driver.find_element(By.CSS_SELECTOR, "body")  #[cite: 1]
        actions.move_to_element_with_offset(body, 0, 0).perform()  #[cite: 1]
        
        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#dataCustomers_filter .form-control")))  #[cite: 1]
        search_input.click()  #[cite: 1]
        search_input.send_keys("hecto")  #[cite: 1]
        
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".even > td:nth-child(2)"))).click()  #[cite: 1]
        allure.attach(driver.get_screenshot_as_png(), name="5_Cliente_Seleccionado", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 6. DEFINICIÓN DE MONTOS Y FLUJO DE CAJA
    # ==========================================
    with allure.step("6. Completar Tipo de Caja, Detalle y Monto"):
        dropdown_cash = wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1")))  #[cite: 1]
        select_cash = Select(dropdown_cash)  #[cite: 2]
        select_cash.select_by_visible_text("CAJA CHICA U$D")  #[cite: 1]
        
        input_detail = wait.until(EC.visibility_of_element_located((By.ID, "txtDetail")))  #[cite: 1]
        input_detail.clear()
        input_detail.send_keys("Test automático")  #[cite: 1]
        
        input_amount = wait.until(EC.visibility_of_element_located((By.ID, "txtAmount1")))  #[cite: 1]
        input_amount.clear()
        input_amount.send_keys("2000")  #[cite: 1]
        allure.attach(driver.get_screenshot_as_png(), name="6_Datos_Orden_Completados", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 7. GUARDADO DEL ENCABEZADO
    # ==========================================
    with allure.step("7. Guardar encabezado de la Orden de Cobro"):
        btn_save = wait.until(EC.element_to_be_clickable((By.ID, "btnSave")))  #[cite: 1]
        driver.execute_script("arguments[0].click();", btn_save)  #[cite: 2]
        time.sleep(3)  #[cite: 2]
        allure.attach(driver.get_screenshot_as_png(), name="7_Encabezado_Guardado", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 8. IMPUTACIÓN DE SALDOS PENDIENTES
    # ==========================================
    with allure.step("8. Realizar imputación de saldos (Asignar Total)"):
        btn_asignar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending_ctrl4_lnkAsignarTotal > .icon-check")))  #[cite: 1]
        driver.execute_script("arguments[0].click();", btn_asignar)  #[cite: 2]
        time.sleep(2)
        allure.attach(driver.get_screenshot_as_png(), name="8_Imputacion_Saldos_OK", attachment_type=allure.attachment_type.PNG)  #[cite: 2]

    # ==========================================
    # 9. FLUJO DE APROBACIÓN FINAL
    # ==========================================
    with allure.step("9. Procesar aprobación e ingresar Fecha de Recibo"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))).click()  #[cite: 1]
        
        wait.until(EC.element_to_be_clickable((By.ID, "txtReceiptDate"))).click()  #[cite: 1]
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(5) > .day:nth-child(2)"))).click()  #[cite: 1]
        
        btn_confirm_approve = wait.until(EC.element_to_be_clickable((By.ID, "btnApprove")))  #[cite: 1]
        driver.execute_script("arguments[0].click();", btn_confirm_approve)  #[cite: 2]
        time.sleep(3)  #[cite: 2]
        allure.attach(driver.get_screenshot_as_png(), name="9_Orden_Aprobada_Final", attachment_type=allure.attachment_type.PNG)  #[cite: 2]
