import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Excursiones")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre la primera parte del flujo de Tarifario - Excursiones:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Cambio a la solapa Excursiones.
3. Modificación del filtro de destino (de Buenos Aires a Bariloche).
4. Ejecución de la búsqueda.
""")
def test_tarifario_excursiones_corto(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    # 🌟 HELPER CLAVE: Pausa absoluta antibugs (Reutilizado de paquetes)
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
            
        time.sleep(1) # Un segundito de gracia para que el navegador dibuje todo

    def cambiar_destino(destino_actual, nuevo_destino):
        """Abre el dropdown de destino buscando el texto actual, y clickea la nueva opción"""
        # Buscamos el control desplegable que actualmente contiene el texto 'Buenos Aires'
        xpath_dropdown = f"//div[contains(@class, 'ts-control') and contains(., '{destino_actual}')]"
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(1) # Pausa para que se despliegue el menú
        
        # Buscamos y clickeamos la opción 'Bariloche'
        xpath_opcion = f"//div[contains(@class, 'option') and contains(text(), '{nuevo_destino}')]"
        opcion = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opcion)))
        driver.execute_script("arguments[0].click();", opcion)
        esperar_fin_de_carga() # Al cambiar de ciudad el sistema suele hacer una minicarga

    try:
        with allure.step("1 a 3. Navegar a Tarifario y solapa Excursiones"):
            # 2. Click en Tarifario
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            # 3. Click en Excursiones
            btn_excursiones = wait.until(EC.element_to_be_clickable((By.ID, "a-excursions")))
            driver.execute_script("arguments[0].click();", btn_excursiones)
            esperar_fin_de_carga()

        with allure.step("4 y 5. Cambiar destino a Bariloche y Buscar"):
            # 4. Cambiar filtro de Buenos Aires a Bariloche
            cambiar_destino("Buenos Aires", "Bariloche")
            
            # 5. Click en Buscar
            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].click();", btn_buscar)
            esperar_fin_de_carga()
            
            # Captura para comprobar que se aplicó el filtro y se buscó correctamente
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Excursiones_Bariloche", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Excursiones", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
