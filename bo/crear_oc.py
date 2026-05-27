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
    # 2. NAVEGACIÓN MÓDULO TESORERÍA
    # ==========================================
    with allure.step("2. Navegar a Cuentas por Cobrar > Orden de Cobro"):
        menu_tesoreria = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-accordion:nth-child(4) > a > span")))  
        menu_tesoreria.click()  
        
        link_orden_cobro = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".open li:nth-child(3) span")))  
        link_orden_cobro.click()  
        allure.attach(driver.get_screenshot_as_png(), name="2_Bandeja_Ordenes_Cobro", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 3. APERTURA DE FORMULARIO
    # ==========================================
    with allure.step("3. Iniciar creación de Nueva Orden de Cobro"):
        btn_nuevo = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Nuevo")))  
        btn_nuevo.click()  
        allure.attach(driver.get_screenshot_as_png(), name="3_Formulario_Nuevo", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 4. CONFIGURACIÓN DE LISTAS DESPLEGABLES
    # ==========================================
    with allure.step("4. Seleccionar Referencia de Pago y Moneda (USD)"):
        dropdown_refs = wait.until(EC.element_to_be_clickable((By.ID, "ddPaymentRefs")))  
        select_refs = Select(dropdown_refs)  
        select_refs.select_by_visible_text("01C - TRANSFERENCIA CLIENTE DEL EXTERIOR 000001")  

        dropdown_currency = wait.until(EC.element_to_be_clickable((By.ID, "ddCurrency")))  
        select_curr = Select(dropdown_currency)  
        select_curr.select_by_visible_text("USD")  
        allure.attach(driver.get_screenshot_as_png(), name="4_Combos_Configurados", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 5. INTERACCIÓN CON MODAL DE CLIENTES (REFACTORIZADO)
    # ==========================================
    with allure.step("5. Buscar y seleccionar Cliente en el modal"):
        # Intento 1: Clic por JS en el input para forzar el trigger del modal
        try:
            input_customer = wait.until(EC.presence_of_element_located((By.ID, "txtCustomer")))
            driver.execute_script("arguments[0].click();", input_customer)
        except Exception:
            pass
        
        # Intento 2: Clic en la lupa (.icon-magnifier) que es el disparador real del HTML
        try:
            lupa_trigger = driver.find_element(By.CSS_SELECTOR, ".icon-magnifier")
            driver.execute_script("arguments[0].click();", lupa_trigger)
        except Exception:
            pass

        # Esperar y capturar el cuadro de búsqueda usando selectores en cascada por si falla uno
        selectores_busqueda = [
            (By.XPATH, "//div[@id='dataCustomers_filter']//input"),
            (By.CSS_SELECTOR, "#dataCustomers_filter .form-control"),
            (By.CSS_SELECTOR, "input[type='search']")
        ]
        
        search_input = None
        for selector in selectores_busqueda:
            try:
                search_input = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(selector))
                if search_input:
                    break
            except Exception:
                continue

        # Si tras los intentos no apareció el buscador, guardamos la pantalla para ver qué quedó colgado
        if not search_input:
            allure.attach(driver.get_screenshot_as_png(), name="ERROR_Modal_No_Abrio", attachment_type=allure.attachment_type.PNG)
            pytest.fail("El modal de clientes no se abrió o el cuadro de búsqueda cambió de selector.")

        # Si llegó acá, el modal abrió bien. Operamos el filtro:
        search_input.click()  
        search_input.clear()
        search_input.send_keys("hecto")  
        
        # Sincronización asincrónica de DataTables
        primera_celda_xpath = "//table[@id='dataCustomers']/tbody/tr[1]/td[2]"
        wait.until(EC.text_to_be_present_in_element((By.XPATH, primera_celda_xpath), "hecto"))
        
        # Clic directo a la fila filtrada
        fila_cliente = wait.until(EC.element_to_be_clickable((By.XPATH, primera_celda_xpath)))
        driver.execute_script("arguments[0].click();", fila_cliente)
        
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="5_Cliente_Seleccionado", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 6. DEFINICIÓN DE MONTOS Y FLUJO DE CAJA
    # ==========================================
    with allure.step("6. Completar Tipo de Caja, Detalle y Monto"):
        dropdown_cash = wait.until(EC.element_to_be_clickable((By.ID, "ddCashFlow1")))  
        select_cash = Select(dropdown_cash)  
        select_cash.select_by_visible_text("CAJA CHICA U$D")  
        
        input_detail = wait.until(EC.visibility_of_element_located((By.ID, "txtDetail")))  
        input_detail.clear()
        input_detail.send_keys("Test automático")  
        
        input_amount = wait.until(EC.visibility_of_element_located((By.ID, "txtAmount1")))  
        input_amount.clear()
        input_amount.send_keys("2000")  
        allure.attach(driver.get_screenshot_as_png(), name="6_Datos_Orden_Completados", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 7. GUARDADO DEL ENCABEZADO
    # ==========================================
    with allure.step("7. Guardar encabezado de la Orden de Cobro"):
        btn_save = wait.until(EC.element_to_be_clickable((By.ID, "btnSave")))  
        driver.execute_script("arguments[0].click();", btn_save)  
        time.sleep(3)  
        allure.attach(driver.get_screenshot_as_png(), name="7_Encabezado_Guardado", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 8. IMPUTACIÓN DE SALDOS PENDIENTES
    # ==========================================
    with allure.step("8. Realizar imputación de saldos (Asignar Total)"):
        btn_asignar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMain_ctrlChargeOrderAllocationControl_lvPending_ctrl4_lnkAsignarTotal > .icon-check")))  
        driver.execute_script("arguments[0].click();", btn_asignar)  
        time.sleep(2)
        allure.attach(driver.get_screenshot_as_png(), name="8_Imputacion_Saldos_OK", attachment_type=allure.attachment_type.PNG)  

    # ==========================================
    # 9. FLUJO DE APROBACIÓN FINAL
    # ==========================================
    with allure.step("9. Procesar aprobación e ingresar Fecha de Recibo"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnApprove"))).click()  
        
        wait.until(EC.element_to_be_clickable((By.ID, "txtReceiptDate"))).click()  
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "tr:nth-child(5) > .day:nth-child(2)"))).click()  
        
        btn_confirm_approve = wait.until(EC.element_to_be_clickable((By.ID, "btnApprove")))  
        driver.execute_script("arguments[0].click();", btn_confirm_approve)  
        time.sleep(3)  
        allure.attach(driver.get_screenshot_as_png(), name="9_Orden_Aprobada_Final", attachment_type=allure.attachment_type.PNG)
