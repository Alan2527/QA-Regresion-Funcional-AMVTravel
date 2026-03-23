import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@allure.feature("Tarifario")
@allure.story("Consulta de Excursiones")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Excursiones:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Cambio a la solapa Excursiones.
3. Modificación del filtro de destino (de Buenos Aires a Bariloche).
4. Ejecución de la búsqueda (Foco y Enter).
5. Ingreso al detalle de la primera excursión encontrada (ID dinámico).
6. Validación de la tabla de tarifas.
7. Apertura y validación del modal de Proveedores.
""")
def test_tarifario_excursiones(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loading') or contains(@class, 'spinner')]")))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script("return (typeof Sys === 'undefined') || (typeof Sys.WebForms === 'undefined') || (Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack() === false);"))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script("return (typeof jQuery === 'undefined') || (jQuery.active === 0);"))
        except:
            pass
        time.sleep(1) 

    def cambiar_destino(destino_actual, nuevo_destino):
        xpath_dropdown = f"//div[contains(@class, 'ts-control') and contains(., '{destino_actual}')]"
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(1) 
        
        xpath_opcion = f"//div[contains(@class, 'option') and contains(text(), '{nuevo_destino}')]"
        opcion = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opcion)))
        driver.execute_script("arguments[0].click();", opcion)
        esperar_fin_de_carga() 

    try:
        with allure.step("1 a 3. Navegar a Tarifario y solapa Excursiones"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_excursiones = wait.until(EC.element_to_be_clickable((By.ID, "a-excursions")))
            driver.execute_script("arguments[0].click();", btn_excursiones)
            esperar_fin_de_carga()

        with allure.step("4 y 5. Cambiar destino a Bariloche y Buscar"):
            cambiar_destino("Buenos Aires", "Bariloche")
            
            # CORRECCIÓN VITAL: Hacemos foco en el botón y apretamos ENTER físico
            btn_buscar = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)
            esperar_fin_de_carga()
            
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Excursiones", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 y 7. Ingresar al detalle de la excursión y validar tabla de tarifas"):
            # CORRECCIÓN VITAL: Evitamos el GUID quemado en código y clickeamos el 1er resultado dinámico
            btn_excursion = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item1 a[id^='lnk']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_excursion)
            time.sleep(1)
            btn_excursion.send_keys(Keys.ENTER)
            esperar_fin_de_carga()
            
            # Validamos tabla
            tabla_detalle = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded")))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")
            
            assert len(p_tariffs) > 0, "Validación fallida: No se encontró ningún elemento <p> con clase 'pTariff'."
            
            allure.attach(driver.get_screenshot_as_png(), name="2_Detalle_Excursion_Validado", attachment_type=allure.attachment_type.PNG)

        with allure.step("8 y 9. Abrir modal de Proveedores y validar datos"):
            btn_proveedores = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Ver Proveedores']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_proveedores)
            time.sleep(1)
            btn_proveedores.send_keys(Keys.ENTER) # Homologamos el click a Enter también por seguridad
            
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))
            tds = driver.find_elements(By.CSS_SELECTOR, "table.suppliers-table td")
            
            texto_encontrado = any(td.text.strip() != "" for td in tds)
            assert texto_encontrado, "Validación fallida: La tabla de proveedores cargó vacía."
            
            time.sleep(1)
            allure.attach(driver.get_screenshot_as_png(), name="3_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Excursiones", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
