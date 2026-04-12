import time
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.feature("Tarifario")
@allure.story("Consulta de Ofertas Completa (Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
def test_tarifario_ofertas(logged_in_driver):

    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(),'CARGANDO','cargando'),'cargando') or contains(@class,'loading')]"
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
        with allure.step("1 a 2. Navegar a Tarifario y solapa Ofertas"):

            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_ofertas = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'a[href="#opportunity"]'
            )))
            driver.execute_script("arguments[0].click();", btn_ofertas)
            esperar_fin_de_carga()

        # =========================
        # 3 Búsqueda
        # =========================
        with allure.step("3. Buscar ofertas en Buenos Aires"):

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_buscar)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", btn_buscar)
            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Ofertas_BUE",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 4 Modal
        # =========================
        with allure.step("4. Click en botón Ver Detalle y validar modal"):

            XPATH_DETALLE = "//a[@href='javascript:void(0);' and contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')]"

            def get_btn_detalle():
                return wait.until(EC.presence_of_element_located((By.XPATH, XPATH_DETALLE)))

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", get_btn_detalle())
            time.sleep(1)

            driver.execute_script("arguments[0].click();", get_btn_detalle())

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))

            time.sleep(1)

            assert modal_detalle.is_displayed(), "El modal de detalle de la oferta no se renderizó."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            wait.until(EC.invisibility_of_element(modal_detalle))
            time.sleep(1)

        # =========================
        # HELPERS DE BÚSQUEDA INDEPENDIENTE
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
        with allure.step("5.1. Validar que el botón tenga el texto Ver Tarifario y el icono chevron-down"):

            boton_ver_inicial = buscar_boton_ver()
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton_ver_inicial)
            time.sleep(1)

            assert check_icono(boton_ver_inicial, "down"), "Falta el ícono de flecha hacia abajo en Ver Tarifario"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Paso1_Ver_Tarifario_Inicial",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 5.2 Clickear en Ver Tarifario
        # =========================
        with allure.step("5.2. Clickear en el botón Ver Tarifario"):
            driver.execute_script("arguments[0].click();", boton_ver_inicial)
            time.sleep(2.5) 

        # =========================
        # 5.3 Validar estado Cerrar Tarifario
        # =========================
        with allure.step("5.3. Buscar el nuevo botón y validar que diga Cerrar Tarifario con icono chevron-up"):
            
            boton_cerrar = buscar_boton_cerrar()
            assert check_icono(boton_cerrar, "up"), "Falta el ícono de flecha hacia arriba en Cerrar Tarifario"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Paso3_Cerrar_Tarifario",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 5.4 Clickear en Cerrar Tarifario
        # =========================
        with allure.step("5.4. Clickear en el botón Cerrar Tarifario"):
            driver.execute_script("arguments[0].click();", boton_cerrar)
            time.sleep(2.5)

        # =========================
        # 5.5 Validar estado Ver Tarifario nuevamente
        # =========================
        with allure.step("5.5. Buscar nuevamente el botón y validar que diga Ver Tarifario"):

            boton_ver_final = buscar_boton_ver()
            assert check_icono(boton_ver_final, "down"), "Falta el ícono de flecha hacia abajo al volver"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Paso5_Vuelve_Ver_Tarifario",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 6 Acordeón y Tabla
        # =========================
        with allure.step("6. Validar apertura final y tabla de tarifas"):
            
            boton_para_abrir = buscar_boton_ver()
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton_para_abrir)
            time.sleep(1)
            
            driver.execute_script("arguments[0].click();", boton_para_abrir)
            
            # Garantía: Esperamos a que aparezca "Cerrar Tarifario" para confirmar que se abrió
            buscar_boton_cerrar()
            time.sleep(1) 

            tabla = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))

            tarifas = tabla.find_elements(By.CSS_SELECTOR, "p.pTariff")
            assert len(tarifas) > 0, "No hay tarifas en la tabla"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="6_Detalle_Oferta_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # 7 Cerrar Tarifario Final
        # =========================
        with allure.step("7. Cerrar el acordeón tras leer la tabla y validar estado final"):
            
            # 1. Ya sabemos que está abierto, así que buscamos el botón "Cerrar" fresco
            boton_para_cerrar_final = buscar_boton_cerrar()
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton_para_cerrar_final)
            time.sleep(1)
            
            # 2. Le hacemos clic
            driver.execute_script("arguments[0].click();", boton_para_cerrar_final)
            time.sleep(2.5) # Esperamos que termine de cerrarse
            
            # 3. Buscamos el botón de "Ver" para confirmar que volvió a la normalidad
            boton_ver_finalisimo = buscar_boton_ver()
            assert check_icono(boton_ver_finalisimo, "down"), "Falta el ícono de flecha hacia abajo en el cierre final"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="7_Cierre_Final_OK",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Ofertas",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
