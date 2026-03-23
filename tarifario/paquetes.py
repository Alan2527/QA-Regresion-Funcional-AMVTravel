import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@allure.feature("Tarifario")
@allure.story("Consulta de Paquetes - Flujo Corto")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre la primera parte del flujo de Tarifario - Paquetes:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Búsqueda de paquetes con filtros por defecto (Argentina, Buenos Aires).
3. Validación de estructura de resultados en pantalla.
4. Ingreso al detalle del paquete (ID lnk2138).
""")
def test_tarifario_paquetes_corto(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    # 🌟 HELPER CLAVE: Pausa absoluta antibugs
    def esperar_fin_de_carga():
        # 1. Esperar a que la ruedita visual desaparezca
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loading') or contains(@class, 'spinner')]")))
        except:
            pass
        
        # 2. Esperar a que ASP.NET AJAX termine (Evita que el DOM se rompa o desaparezca)
        try:
            wait.until(lambda d: d.execute_script("return (typeof Sys === 'undefined') || (typeof Sys.WebForms === 'undefined') || (Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack() === false);"))
        except:
            pass
            
        # 3. Esperar a que jQuery termine sus animaciones y requests
        try:
            wait.until(lambda d: d.execute_script("return (typeof jQuery === 'undefined') || (jQuery.active === 0);"))
        except:
            pass
            
        time.sleep(1) # Un segundito de gracia para que el navegador dibuje todo

    try:
        with allure.step("1 a 5. Navegar a Tarifario, Paquetes y buscar"):
            # 2. Click en Tarifario
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            # 3. Click en Paquetes
            try:
                btn_paquetes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tour']")))
                driver.execute_script("arguments[0].click();", btn_paquetes)
                esperar_fin_de_carga()
            except:
                pass

            # 4 y 5. Buscar
            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].click();", btn_buscar)
            
            esperar_fin_de_carga() 
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Tarifario", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 y 7. Validar resultados y entrar al detalle del paquete (ID lnk2138)"):
            # 6. Validar estructura
            item_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item1")))
            imagenes = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-image-view")
            detalles = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-detail")
            
            assert len(imagenes) > 0 and len(detalles) > 0, "Validación fallida: No se renderizó la estructura de la card."

            # 7. Click en el paquete específico
            btn_paquete = wait.until(EC.presence_of_element_located((By.ID, "lnk2138")))
            
            # Lo centramos en pantalla para evitar que el menú flotante tape el click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_paquete)
            time.sleep(1)
            
            # Al usar 'Keys.ENTER' disparamos el evento nativo del link sin depender del mouse virtual
            btn_paquete.send_keys(Keys.ENTER)
            
            esperar_fin_de_carga() 
            allure.attach(driver.get_screenshot_as_png(), name="2_Ingreso_Detalle_Paquete", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
