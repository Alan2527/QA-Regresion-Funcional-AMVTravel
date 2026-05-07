import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Hoteles Completa (Tags, Tarifas y Modales)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Hoteles:
1. Login y navegación a la solapa Hoteles.
2. Búsqueda con destino Cachi.
3. Validación estática del Tag "Hotel Recomendado" (Antes de alterar el scroll).
4. Validación del estado inicial del botón Ver Tarifario.
5. Apertura del panel principal, sub-acordeón de habitaciones y validación de la tabla de tarifas.
6. Cierre del panel y validación del retorno al estado inicial.
7. Validación Independiente del modal "Ver Proveedores".
8. Validación Independiente del modal "Ver Detalle".
""")
def test_tarifario_hoteles(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    def esperar_fin_de_carga():
        try:
            wait.until(EC.invisibility_of_element_located((
                By.XPATH,
                "//*[contains(translate(text(), 'CARGANDO', 'cargando'), 'cargando') or contains(@class, 'loading') or contains(@class, 'spinner')]"
            )))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof Sys === 'undefined') || "
                "(typeof Sys.WebForms === 'undefined') || "
                "(Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack() === false);"
            ))
        except:
            pass
        try:
            wait.until(lambda d: d.execute_script(
                "return (typeof jQuery === 'undefined') || (jQuery.active === 0);"
            ))
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
        # =========================
        # 1-2 Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Hoteles"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_hoteles = wait.until(EC.element_to_be_clickable((By.ID, "a-hotels")))
            driver.execute_script("arguments[0].click();", btn_hoteles)
            esperar_fin_de_carga()

        # =========================
        # 3 Filtro y búsqueda
        # =========================
        with allure.step("3. Cambiar destino a Cachi y buscar"):
            cambiar_destino("Buenos Aires", "Cachi")

            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Cachi_Hoteles",
                attachment_type=allure.attachment_type.PNG
            )

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


        # ==========================================
        # BLOQUE 1: ELEMENTOS ESTÁTICOS DE LA TARJETA
        # ==========================================

        # =========================
        # 4 Tag Hotel Recomendado
        # =========================
        with allure.step("4. Validar existencia del tag 'Hotel Recomendado' antes de alterar el layout"):
            tag_recomendado = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.featured-tag"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tag_recomendado)
            time.sleep(0.5)
            
            assert tag_recomendado.is_displayed(), "El tag de Hotel Recomendado no está visible."
            allure.attach(driver.get_screenshot_as_png(), name="2_Tag_Recomendado", attachment_type=allure.attachment_type.PNG)


        # ==========================================
        # BLOQUE 2: VALIDACIÓN CICLO DE VIDA DEL PANEL
        # ==========================================

        # =========================
        # 5 Validar estado inicial Ver Tarifario
        # =========================
        with allure.step("5. Validar estado inicial del botón Ver Tarifario"):
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", buscar_boton_ver())
            time.sleep(1.5) 

            boton_ver_fresco = buscar_boton_ver()
            assert check_icono(boton_ver_fresco, "down"), "Falta el ícono de flecha hacia abajo en Ver Tarifario"
            allure.attach(driver.get_screenshot_as_png(), name="3_Estado_Inicial_Ver_Tarifario", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 6 Clickear en Ver Tarifario
        # =========================
        with allure.step("6. Click en Ver Tarifario para desplegar el panel principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_ver())
            time.sleep(2.5)

        # =========================
        # 7 Validar Cerrar, Abrir Sub-Grupo y Leer Tabla
        # =========================
        with allure.step("7. Validar botón Cerrar Tarifario, desplegar habitación y validar la tabla"):
            boton_cerrar_fresco = buscar_boton_cerrar()
            assert check_icono(boton_cerrar_fresco, "up"), "Falta el ícono de flecha hacia arriba en Cerrar Tarifario"

            btn_habitacion = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "a[id^='accordeon-header-']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_habitacion)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_habitacion)
            time.sleep(2) 

            tabla_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(p_tariffs) > 0, "No se encontró ningún elemento pTariff en la tabla del hotel."
            allure.attach(driver.get_screenshot_as_png(), name="4_Tarifario_Y_Tabla_Abiertos", attachment_type=allure.attachment_type.PNG)

        # =========================
        # 8 Cierre Tarifario
        # =========================
        with allure.step("8. Cerrar el acordeón principal"):
            driver.execute_script("arguments[0].click();", buscar_boton_cerrar())
            time.sleep(2.5) 
            
        # =========================
        # 9 Validar estado Ver Tarifario nuevamente
        # =========================
        with allure.step("9. Validar que el botón retornó a Ver Tarifario"):
            boton_ver_finalisimo = buscar_boton_ver()
            assert check_icono(boton_ver_finalisimo, "down"), "Falta el ícono de flecha hacia abajo en el cierre final"
            allure.attach(driver.get_screenshot_as_png(), name="5_Cierre_Final_OK", attachment_type=allure.attachment_type.PNG)


        # ==========================================
        # BLOQUE 3: VALIDACIÓN DE MODALES (INDEPENDIENTES)
        # ==========================================

        # =========================
        # 10 Modal Proveedores
        # =========================
        with allure.step("10. Abrir modal de Proveedores desde el listado y validar datos"):
            btn_proveedores = wait.until(EC.presence_of_element_located((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_proveedores)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            modal_prov = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal"
            )))
            time.sleep(3) 

            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores cargó vacía."

            allure.attach(driver.get_screenshot_as_png(), name="6_Modal_Proveedores", attachment_type=allure.attachment_type.PNG)

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1.5)
            esperar_fin_de_carga()

        # =========================
        # 11 Modal Ver Detalle (FIXED)
        # =========================
        with allure.step("11. Click en botón Ver Detalle y validar apertura de modal de detalle"):
            # Usamos un selector robusto por texto para encontrar el botón correcto
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(translate(text(), 'VER DETALLE', 'ver detalle'), 'ver detalle')]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_detalle)
            time.sleep(1) 
            # Forzamos el clic por JS para disparar el evento onclick del modal
            driver.execute_script("arguments[0].click();", btn_detalle)

            # Esperamos a que el contenido del modal sea visible
            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal.show div.modal-content, div.modal.in div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle no se renderizó."
            time.sleep(1)

            allure.attach(driver.get_screenshot_as_png(), name="7_Modal_VerDetalle", attachment_type=allure.attachment_type.PNG)

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Hoteles",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
