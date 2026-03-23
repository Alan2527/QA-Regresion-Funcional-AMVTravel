import pytest
import allure
import time
import os
import glob
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@allure.feature("Tarifario")
@allure.story("Consulta de Paquetes, validación de UI y descarga de Word")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Paquetes:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Búsqueda de paquetes con filtros por defecto (Argentina, Buenos Aires).
3. Validación de estructura de resultados en pantalla.
4. Ingreso al detalle del paquete (ID lnk2138).
5. Apertura y validación del acordeón de tours.
6. Validación del modal de Proveedores y sus datos.
7. Descarga del paquete en formato Word y validación en el sistema de archivos (CI/CD).
""")
def test_tarifario_paquetes(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    # Configuramos el Chrome Headless de GitHub Actions para permitir descargas locales
    descargas_dir = os.getcwd()
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': descargas_dir
    })

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
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            try:
                btn_paquetes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tour']")))
                driver.execute_script("arguments[0].click();", btn_paquetes)
                esperar_fin_de_carga()
            except:
                pass

            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].click();", btn_buscar)
            
            esperar_fin_de_carga() 
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Tarifario", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 y 7. Validar resultados y entrar al detalle del paquete (ID lnk2138)"):
            item_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item1")))
            imagenes = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-image-view")
            detalles = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-detail")
            
            assert len(imagenes) > 0 and len(detalles) > 0, "Validación fallida: No se renderizó la estructura de la card."

            btn_paquete = wait.until(EC.presence_of_element_located((By.ID, "lnk2138")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_paquete)
            time.sleep(1)
            btn_paquete.send_keys(Keys.ENTER)
            
            esperar_fin_de_carga() 
            allure.attach(driver.get_screenshot_as_png(), name="2_Ingreso_Detalle_Paquete", attachment_type=allure.attachment_type.PNG)

        with allure.step("8 a 10. Validar renderizado y apertura del acordeón de tours"):
            # Omitimos la clase toggle-asigned porque se pone dinámicamente
            acc_header = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.accordeon-header.tariff-detail-group-tours")))
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", acc_header)
            time.sleep(1) 
            
            acc_header.send_keys(Keys.ENTER) # Replicamos la técnica que nos funcionó antes
            
            acc_content = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.col-md-12.accordeon-content")))
            assert acc_content.is_displayed(), "Validación fallida: El acordeón no se desplegó."
            
            time.sleep(1) 
            allure.attach(driver.get_screenshot_as_png(), name="3_Acordeon_Abierto", attachment_type=allure.attachment_type.PNG)

        with allure.step("11 a 13. Validar modal de Proveedores"):
            btn_proveedores = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Ver Proveedores']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_proveedores)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))
            tds = driver.find_elements(By.CSS_SELECTOR, "table.suppliers-table td")
            
            texto_encontrado = any(td.text.strip() != "" for td in tds)
            assert texto_encontrado, "Validación fallida: La tabla cargó vacía."
            
            time.sleep(1) 
            allure.attach(driver.get_screenshot_as_png(), name="4_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            
            btn_cerrar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-close-suppliers")))
            driver.execute_script("arguments[0].click();", btn_cerrar)
            
            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))
            time.sleep(1) # Pausa para que el modal termine de desvanecerse

        with allure.step("14 y 15. Descargar y validar archivo Word en CI"):
            # Tomamos una "foto" de los archivos que hay antes de descargar
            archivos_previos = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
            
            btn_word = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Descargar en formato Word']")))
            driver.execute_script("arguments[0].click();", btn_word)
            
            archivo_descargado = False
            # Intentamos hasta 20 veces (10 segundos total) revisar la carpeta
            for _ in range(20): 
                time.sleep(0.5)
                archivos_actuales = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
                nuevos_archivos = archivos_actuales - archivos_previos
                
                if nuevos_archivos:
                    archivo_descargado = True
                    break
            
            assert archivo_descargado, "Validación fallida: No se detectó la descarga del archivo Word."
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Descarga_Exitosa", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
