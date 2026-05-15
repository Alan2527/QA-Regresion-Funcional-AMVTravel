import pytest
import allure
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Reservas BackOffice")
@allure.story("Generación de File desde Inbox")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este test valida el flujo de creación de un File a partir de un registro en el Inbox del BO:
1. Login administrativo.
2. Navegación a la Bandeja de Entrada (Inbox) de Reservas.
3. Selección del primer registro pendiente.
4. Asignación de País (Argentina) y Nombre de Grupo.
5. Guardado y validación de persistencia de datos.
6. Validación de carga de tablas de Destinos y Totales.
""")
def test_generar_file_desde_inbox(driver):
    wait = WebDriverWait(driver, 15)

    # ==========================================
    # 1. LOGIN
    # ==========================================
    with allure.step("1. Login en el BackOffice"):
        driver.get("https://qa.bo.amv.travel/login")
        
        usuario = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not usuario or not password:
            pytest.fail("Error de configuración: Faltan las variables de entorno AMV_USER o BO_PASS.")

        wait.until(EC.visibility_of_element_located((By.ID, "txtUser"))).send_keys(usuario)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        wait.until(EC.url_to_be("https://qa.bo.amv.travel/main"))

    # ==========================================
    # 2 y 3. NAVEGACIÓN AL INBOX
    # ==========================================
    with allure.step("2 y 3. Navegar a Reservas > Bandeja de Entrada"):
        menu_reservas = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Reservas')]")))
        menu_reservas.click()
        
        link_inbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://qa.bo.amv.travel/booking/files/inbox/10']")))
        link_inbox.click()

    # ==========================================
    # 4. ABRIR EL PRIMER REGISTRO
    # ==========================================
    with allure.step("4. Clickear en el primer registro disponible de la tabla"):
        # Usamos [1] en XPath para asegurarnos de agarrar estrictamente el primero
        btn_primer_registro = wait.until(EC.element_to_be_clickable((By.XPATH, "(//a[contains(@class, 'btn btn-sm usepreload')])[1]")))
        driver.execute_script("arguments[0].click();", btn_primer_registro)
        
        # Esperamos a que la nueva pantalla empiece a cargar (podemos esperar a que aparezca el botón de guardar)
        wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMain$btnSave")))

        # ==========================================
        # 5 y 6. COMPLETAR FORMULARIO
        # ==========================================
        with allure.step("5 y 6. Completar datos iniciales (País y Nombre de Grupo)"):
            # Elegir Argentina en el Select usando el ID ddBranch
            dropdown_pais = wait.until(EC.element_to_be_clickable((By.ID, "ddBranch")))
            select = Select(dropdown_pais)
            select.select_by_visible_text("Argentina")

            # Escribir el nombre del grupo
            input_grupo = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$cphMain$txtGroupName")))
            input_grupo.clear()
            input_grupo.send_keys("TEST AUTOMÁTICO")

            allure.attach(driver.get_screenshot_as_png(), name="Pais_NombreGrupo", attachment_type=allure.attachment_type.PNG)

    # ==========================================
    # 7 y 8. VALIDAR TABLA DETALLE Y GUARDAR
    # ==========================================
    with allure.step("7 y 8. Validar detalle de Inbox y Guardar"):
        # 7. Validar tabla de detalle
        tabla_detalle = wait.until(EC.visibility_of_element_located((By.ID, "tblInboxDetail")))
        assert tabla_detalle.is_displayed(), "La tabla tblInboxDetail no está visible."
        
        allure.attach(driver.get_screenshot_as_png(), name="Formulario_Completado", attachment_type=allure.attachment_type.PNG)

        # 8. Guardar
        btn_save = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMain$btnSave")))
        driver.execute_script("arguments[0].click();", btn_save)
        
        # Pequeña espera para que el postback de ASP.NET procese el guardado
        time.sleep(3) 

    # ==========================================
    # 9, 10 y 11. VALIDACIONES FINALES
    # ==========================================
    with allure.step("9. Validar que el nombre del grupo se haya guardado"):
        # ASP.NET a veces cambia ligeramente los IDs. Usamos un contains por seguridad, pero buscando tu ID.
        input_grupo_guardado = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@id, 'txtGroupName')]")))
        
        # Para los inputs, el texto escrito adentro se lee con el atributo 'value', no con .text
        valor_guardado = input_grupo_guardado.get_attribute("value")
        assert "TEST AUTOMÁTICO" in valor_guardado, f"El nombre del grupo no se guardó. Valor actual: {valor_guardado}"

    with allure.step("10 y 11. Validar carga de tablas de Destinos y Totales"):
        # 10. Validar tabla Destinos
        tabla_destinos = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='updFileDestinations']//table[contains(@class, 'table-striped')]")))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tabla_destinos)
        assert tabla_destinos.is_displayed(), "La tabla de Destinos no se renderizó correctamente."
        allure.attach(driver.get_screenshot_as_png(), name="Tabla_Destinos_OK", attachment_type=allure.attachment_type.PNG)

        # 11. Validar tabla Totales
        tabla_totales = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='updFileTotals']//table[contains(@class, 'table-striped')]")))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tabla_totales)
        assert tabla_totales.is_displayed(), "La tabla de Totales no se renderizó correctamente."
        allure.attach(driver.get_screenshot_as_png(), name="Tabla_Totales_OK", attachment_type=allure.attachment_type.PNG)

        # 12. Validar tabla Totales
        tabla_costos = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='updCostBySupplier']//table[contains(@class, 'table-striped')]")))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tabla_costos)
        assert tabla_totales.is_displayed(), "La tabla de Costos no se renderizó correctamente."
        allure.attach(driver.get_screenshot_as_png(), name="Tabla_Costos_OK", attachment_type=allure.attachment_type.PNG)
