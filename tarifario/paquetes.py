import pytest
import allure
import time
import os
import glob
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Paquetes, validación de UI y descarga de Word")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Paquetes:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Búsqueda de paquetes con filtros por defecto (Argentina, Buenos Aires).
3. Validación de estructura de resultados en pantalla.
4. Ingreso al detalle del paquete (ID 2138) y validación del acordeón desplegable.
5. Apertura del modal de Proveedores y validación de datos cargados.
6. Descarga del paquete en formato Word y validación en el sistema de archivos (CI/CD).
""")
def test_tarifario_paquetes(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    descargas_dir = os.getcwd()
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': descargas_dir
    })

    # 🌟 HELPER CLAVE: Pausa el test si detecta el overlay de "Cargando..."
    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loading') or contains(@class, 'spinner')]")))
            time.sleep(1) # Buffer extra de 1 segundo para que el DOM se dibuje bien
        except:
            pass

    try:
        with allure.step("1 a 5. Navegar a Tarifario, Paquetes y buscar"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            btn_tarifario.click()
            esperar_fin_de_carga()

            try:
                btn_paquetes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tour']")))
                btn_paquetes.click()
            except:
                pass

            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            btn_buscar.click()
            
            esperar_fin_de_carga() # Espera a que carguen los resultados
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Tarifario", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 y 7. Validar resultados y entrar al detalle del paquete (ID 2138)"):
            item_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item1")))
            imagenes = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-image-view")
            detalles = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-detail")
            
            assert len(imagenes) > 0 and len(detalles) > 0, "Validación fallida: No se renderizó la estructura."

            btn_paquete = wait.until(EC.element_to_be_clickable((By.ID, "lnk2138")))
            driver.execute_script("arguments[0].click();", btn_paquete)
            
            esperar_fin_de_carga() # Espera a que cargue la vista de detalle del paquete
            allure.attach(driver.get_screenshot_as_png(), name="2_Ingreso_Detalle_Paquete", attachment_type=allure.attachment_type.PNG)

        with allure.step("8 a 10. Validar renderizado y apertura del acordeón de tours"):
            # Aumentamos la espera específica para este bloque a 30 segundos
            wait_long = WebDriverWait(driver, 30)
            
            # Usamos CSS Selector apuntando directamente a las clases estáticas del elemento
            acc_header = wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.accordeon-header.tariff-detail-group-tours")))
            
            # 🌟 SCROLL FORZADO: Movemos la pantalla hasta el elemento antes de interactuar
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", acc_header)
            time.sleep(1) # Pausa obligatoria post-scroll
            
            # Forzamos click por JS
            driver.execute_script("arguments[0].click();", acc_header)
            
            acc_content = wait_long.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.col-md-12.accordeon-content")))
            assert acc_content.is_displayed(), "Validación fallida: El acordeón no se desplegó."
            
            time.sleep(1) # Pequeña pausa para capturar la animación del acordeón abierto
            allure.attach(driver.get_screenshot_as_png(), name="3_Acordeon_Abierto", attachment_type=allure.attachment_type.PNG)

        with allure.step("11 a 13. Validar modal de Proveedores"):
            btn_proveedores = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Ver Proveedores']")))
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))
            tds = driver.find_elements(By.CSS_SELECTOR, "table.suppliers-table td")
            
            texto_encontrado = any(td.text.strip() != "" for td in tds)
            assert texto_encontrado, "Validación fallida: La tabla cargó vacía."
            
            time.sleep(1) # Pausa para foto
            allure.attach(driver.get_screenshot_as_png(), name="4_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            
            btn_cerrar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-close-suppliers")))
            driver.execute_script("arguments[0].click();", btn_cerrar)
            
            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))

        with allure.step("14 y 15. Descargar y validar archivo Word en CI"):
            archivos_previos = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
            
            btn_word = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Descargar en formato Word']")))
            driver.execute_script("arguments[0].click();", btn_word)
            
            archivo_descargado = False
            for _ in range(20): 
                time.sleep(0.5)
                archivos_actuales = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
                nuevos_archivos = archivos_actuales - archivos_previos
                
                if nuevos_archivos:
                    archivo_descargado = True
                    break
            
            assert archivo_descargado, "Validación fallida: No se detectó la descarga del archivo."
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Descarga_Exitosa", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
