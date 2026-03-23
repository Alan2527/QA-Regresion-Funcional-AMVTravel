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

    # Configuramos el Chrome Headless de GitHub Actions para permitir descargas locales
    descargas_dir = os.getcwd()
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': descargas_dir
    })

    try:
        with allure.step("1 a 5. Navegar a Tarifario, Paquetes y buscar"):
            # 2. Click en la pestaña Tarifario 
            # (Usamos un *= para que coincida aunque las fechas de los parámetros en el href cambien mañana)
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            btn_tarifario.click()
            
            # 3. Click en Paquetes (href="#tour")
            try:
                # Puede que la solapa ya esté activa por defecto, lo metemos en try-except para que no falle si no se puede clickear
                btn_paquetes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tour']")))
                btn_paquetes.click()
            except:
                pass
            
            # 4 y 5. Buscar con filtros por defecto
            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            btn_buscar.click()
            
            # CAPTURA PASO 1
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Tarifario", attachment_type=allure.attachment_type.PNG)

        with allure.step("6 y 7. Validar resultados y entrar al detalle del paquete (ID 2138)"):
            # 6. Validar que exista al menos un div class="item1" con su imagen y detalle interno
            item_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item1")))
            imagenes = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-image-view")
            detalles = item_container.find_elements(By.CSS_SELECTOR, "div.tariff-detail")
            
            assert len(imagenes) > 0 and len(detalles) > 0, "Validación fallida: No se renderizó la estructura de la tarjeta del paquete (imagen o detalle ausente)."
            
            # 7. Click en el paquete específico lnk2138
            btn_paquete = wait.until(EC.element_to_be_clickable((By.ID, "lnk2138")))
            btn_paquete.click()
            
            # CAPTURA PASO 2
            allure.attach(driver.get_screenshot_as_png(), name="2_Ingreso_Detalle_Paquete", attachment_type=allure.attachment_type.PNG)

        with allure.step("8 a 10. Validar renderizado y apertura del acordeón de tours"):
            # 8 y 9. Click en el encabezado del acordeón
            acc_header = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.col-md-12 a.accordeon-header.tariff-detail-group-name.tariff-detail-group-tours.toggle-asigned")))
            acc_header.click()
            
            # 10. Validar que se renderiza y hace visible el contenido interno
            acc_content = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.col-md-12.accordeon-content")))
            assert acc_content.is_displayed(), "Validación fallida: El acordeón no se desplegó."
            
            # Espera mínima para que termine la animación css de apertura antes de la foto
            time.sleep(1) 
            # CAPTURA PASO 3
            allure.attach(driver.get_screenshot_as_png(), name="3_Acordeon_Abierto", attachment_type=allure.attachment_type.PNG)

        with allure.step("11 a 13. Validar modal de Proveedores"):
            # 11. Click en Ver Proveedores
            btn_proveedores = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Ver Proveedores']")))
            btn_proveedores.click()
            
            # 12. Validar que se abre la tabla y tiene al menos un 'td' con texto renderizado
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))
            tds = driver.find_elements(By.CSS_SELECTOR, "table.suppliers-table td")
            
            # Verificamos si algún TD contiene texto real (no vacío)
            texto_encontrado = any(td.text.strip() != "" for td in tds)
            assert texto_encontrado, "Validación fallida: La tabla de proveedores cargó vacía."
            
            # CAPTURA PASO 4 (Modal abierto)
            allure.attach(driver.get_screenshot_as_png(), name="4_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)
            
            # 13. Cerrar Modal
            btn_cerrar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-close-suppliers")))
            btn_cerrar.click()
            
            # Validamos que desaparezca de la vista
            wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.suppliers-table")))

        with allure.step("14 y 15. Descargar y validar archivo Word en CI"):
            # Escaneamos cuántos archivos .doc o .docx hay ANTES de dar click
            archivos_previos = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
            
            # 14. Click en descargar Word
            btn_word = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Descargar en formato Word']")))
            btn_word.click()
            
            # 15. Wait polling (Esperamos un máximo de 10 segundos buscando si aparece un archivo nuevo)
            archivo_descargado = False
            for _ in range(20): 
                time.sleep(0.5)
                archivos_actuales = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
                nuevos_archivos = archivos_actuales - archivos_previos
                
                if nuevos_archivos:  # Si la diferencia no está vacía, se descargó!
                    archivo_descargado = True
                    break
            
            assert archivo_descargado, "Validación fallida: No se detectó la descarga del archivo Word."
            
            # CAPTURA FINAL
            allure.attach(driver.get_screenshot_as_png(), name="5_Descarga_Exitosa", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
