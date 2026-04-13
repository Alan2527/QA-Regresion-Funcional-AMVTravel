import pytest
import allure
import time
import os
import glob
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Paquetes, validación de UI y descarga de Word")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Paquetes con validación de UI dinámica:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Búsqueda de paquetes con filtros por defecto (Argentina, Buenos Aires).
3. Validación del estado inicial del botón Ver Tarifario.
4. Apertura del panel principal, sub-acordeón de tours y validación de la tabla.
5. Cierre del panel y validación del retorno al estado inicial.
6. Descarga del paquete en formato Word (independiente del acordeón) y validación en CI/CD.
""")
def test_tarifario_paquetes(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    # Configuramos el Chrome Headless de GitHub Actions para permitir descargas locales
    descargas_dir = os.getcwd()
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': descargas_dir
    })

    # 🌟 HELPER CLAVE: Pausa absoluta antibugs
    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH, "//*[contains(translate(text(),'CARGANDO','cargando'),'cargando') or contains(@class,'loading')]"
            )))
        except:
            pass
        
        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof jQuery==='undefined') || (jQuery.active===0);"
            ))
        except:
            pass
            
        time.sleep(1)

    try:
        # =========================
        # 1-2 Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Paquetes"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']")))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            try:
                btn_paquetes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tour']")))
                driver.execute_script("arguments[0].click();", btn_paquetes)
                esperar_fin_de_carga()
            except:
                pass

        # =========================
        # 3 Búsqueda
        # =========================
        with allure.step("3. Buscar paquetes con filtros por defecto"):
            btn_buscar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_buscar)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_buscar)
            
            esperar_fin_de_carga() 
            allure.attach(driver.get_screenshot_as_png(), name="1_Busqueda_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)

        # =========================
        # HELPERS INFALIBLES JAVASCRIPT
        # =========================
        def buscar_boton_ver():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('ver tarifario')) {
                        return links[i];
                    }
                }
                return null;
            """), message="No se encontró el botón 'Ver Tarifario'.")

        def buscar_boton_cerrar():
            return wait.until(lambda d: d.execute_script("""
                var links = document.querySelectorAll('a');
                for (var i=0; i<links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || "").toLowerCase();
                    if (text.includes('cerrar tarifario')) {
                        return links[i];
                    }
                }
                return null;
            """), message="No se encontró el botón 'Cerrar Tarifario'.")
            
        def check_icono(elemento, direccion):
            return driver.execute_script(f"return arguments[0].querySelector('i[class*=\"chevron-{direccion}\"]') !== null;", elemento)

        # =========================
        # 5.1 Validar estado inicial Ver Tarifario
        # =========================
        with allure.step("5.1. Validar estado inicial del botón Ver Tarifario"):
            # Movemos la pantalla usando un elemento fresco
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", buscar_boton_ver())
            time.sleep(1.5) # Esperamos que el DOM se asiente

            # BUSCAMOS FRESCO justo antes de validar para aniquilar el StaleElement
            boton_ver_fresco = buscar_boton_ver()
            assert check_icono(boton_ver_fresco, "down"), "Falta el ícono de flecha hacia abajo en Ver Tarifario"
            allure.attach(driver.get_screenshot_as_png(), name="2_Estado_Inicial_Ver_Tarifario", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 5.2 Clickear en Ver Tarifario
        # =========================
        with allure.step("5.2. Click en Ver Tarifario para desplegar el panel principal"):
            # Buscamos de nuevo justo antes del click
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)

        # =========================
        # 5.3 Validar Cerrar, Abrir Tours y Leer Tabla
        # =========================
        with allure.step("5.3. Validar botón Cerrar Tarifario, abrir sub-grupo de tours y validar la tabla"):
            # Buscamos el botón cerrar fresco
            boton_cerrar_fresco = buscar_boton_cerrar()
            assert check_icono(boton_cerrar_fresco, "up"), "Falta el ícono de flecha hacia arriba en Cerrar Tarifario"

            # Buscamos y abrimos el sub-acordeón de tours
            sub_grupos = wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, "a.accordeon-header.tariff-detail-group-tours"
            )))
            assert len(sub_grupos) > 0, "No se encontró el sub-grupo de tours para expandir."
            
            primer_sub_grupo = sub_grupos[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", primer_sub_grupo)
            time.sleep(1)
            
            driver.execute_script("arguments[0].click();", primer_sub_grupo)
            time.sleep(2) # Pausa para que se dibuje el contenido del tour

            # Leemos la tabla
            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))

            tarifas = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(tarifas) > 0, "No hay tarifas en la tabla"

            allure.attach(driver.get_screenshot_as_png(), name="3_Tarifario_Y_Tours_Abierto_OK", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 5.4 Cierre Tarifario
        # =========================
        with allure.step("5.4. Cerrar el acordeón principal"):
            # Clickeamos buscando el botón cerrar fresco nuevamente
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2.5) # Esperamos que termine de cerrarse todo
            
        # =========================
        # 5.5 Validar estado Ver Tarifario nuevamente
        # =========================
        with allure.step("5.5. Validar que el botón retornó a Ver Tarifario"):
            # Buscamos fresco para la validación final
            boton_ver_finalisimo = buscar_boton_ver()
            assert check_icono(boton_ver_finalisimo, "down"), "Falta el ícono de flecha hacia abajo en el cierre final"

            allure.attach(driver.get_screenshot_as_png(), name="4_Cierre_Final_OK", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 6 Validar Descarga de Word (Independiente)
        # =========================
        with allure.step("6. Descargar y validar archivo Word en CI (Acordeón Cerrado)"):
            # Tomamos una "foto" de los archivos que hay antes de descargar
            archivos_previos = set(glob.glob(os.path.join(descargas_dir, "*.doc*")))
            
            btn_word = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Descargar en formato Word']")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_word)
            time.sleep(1)
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
            
            assert archivo_descargado, "Validación fallida: No se detectó la descarga del archivo Word en el entorno de pruebas."
            
            allure.attach(driver.get_screenshot_as_png(), name="5_Descarga_Word_Exitosa", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_Tarifario_Paquetes", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
