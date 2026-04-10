import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Cena Show Completa (Tooltips, Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Cena Show:
1. Login y navegación a la solapa Cena Show.
2. Búsqueda con destino Cachi.
3. Validación de Tooltip de Duración.
4. Validación de Tooltip de Idiomas.
5. Validación de Tooltip de Operatividad (Días y meses específicos).
6. Validación del modal "Ver Proveedores" desde el listado.
7. Validación del modal "Ver Detalle".
8. Ingreso al detalle de la cena show y validación de la tabla de tarifas.
""")
def test_tarifario(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
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
        # Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Cena Show"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            # Acceso específico a Cena Show mediante href="#show"
            btn_cenashow = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#show"]')))
            driver.execute_script("arguments[0].click();", btn_cenashow)
            esperar_fin_de_carga()

        # =========================
        # Filtro y búsqueda
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
                name="1_Busqueda_CenaShow_Cachi",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Tooltip 1: Duración
        # =========================
        with allure.step("4. Validar tooltip de icono Duración"):
            icono_duracion = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-clock")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icono_duracion)
            time.sleep(0.5)
            
            actions.move_to_element(icono_duracion).pause(1).perform()

            tooltip_duracion = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//span[contains(@class, 'tariff-op-tooltip') and contains(., 'Duración estimada del servicio')]"
            )))
            
            assert tooltip_duracion.is_displayed(), "El tooltip de duración no es visible."
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Tooltip_Duracion",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Tooltip 2: Idiomas
        # =========================
        with allure.step("5. Validar tooltip de icono Idiomas"):
            icono_idiomas = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-translate")))
            actions.move_to_element(icono_idiomas).pause(1).perform()

            tooltip_idiomas = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//span[contains(@class, 'tariff-op-tooltip') and .//strong[contains(text(), 'Idiomas')]]"
            )))
            
            texto_idiomas = tooltip_idiomas.text
            assert "Español" in texto_idiomas, "Falta idioma Español"
            assert "English" in texto_idiomas, "Falta idioma English"
            assert "Portuguese" in texto_idiomas, "Falta idioma Portuguese"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Tooltip_Idiomas",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Tooltip 3: Operatividad
        # =========================
        with allure.step("6. Validar tooltip de icono Operatividad"):
            icono_operatividad = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.ph-calendar-dots")))
            actions.move_to_element(icono_operatividad).pause(1).perform()

            tooltip_operatividad = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//span[contains(@class, 'tariff-op-tooltip') and .//strong[contains(text(), 'Operatividad')]]"
            )))
            
            # Nuevas validaciones para Cena Show
            texto_operatividad = tooltip_operatividad.text
            assert "lunes a martes, jueves a viernes, domingo" in texto_operatividad, "Faltan días en el tooltip de operatividad"
            assert "enero, marzo, mayo, julio, septiembre, noviembre" in texto_operatividad, "Falta temporada en el tooltip de operatividad"

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Tooltip_Operatividad",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Validación Modal "Ver Proveedores"
        # =========================
        with allure.step("7. Abrir modal de Proveedores y validar"):
            actions.move_by_offset(0, -100).perform() 
            time.sleep(0.5)

            btn_proveedores = wait.until(EC.element_to_be_clickable((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))
            
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            modal_prov = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal"
            )))
            time.sleep(3)

            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores está vacía."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Modal_Proveedores",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()

        # =========================
        # Validación Modal "Ver Detalle"
        # =========================
        with allure.step("8. Click en botón Ver Detalle y validar modal"):
            btn_detalle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tariff-op-detail-btn")))
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))
            
            assert modal_detalle.is_displayed()
            time.sleep(1)

            allure.attach(
                driver.get_screenshot_as_png(),
                name="6_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # =========================
        # Detalle Cena Show (Tarifario)
        # =========================
        with allure.step("9. Ingresar al detalle de la cena show y validar tarifas"):
            btn_cenashow = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_cenashow)
            time.sleep(1)
            
            # --- INICIO NUEVA VALIDACIÓN: TOGGLE BOTÓN VER/CERRAR TARIFARIO ---
            texto_inicial = btn_cenashow.text.strip().lower()
            assert "ver" in texto_inicial, f"Error: El botón inicialmente dice '{texto_inicial}' en vez de 'Ver...'"

            driver.execute_script("arguments[0].click();", btn_cenashow)
            esperar_fin_de_carga()
            time.sleep(1)

            texto_abierto = btn_cenashow.text.strip().lower()
            assert "cerrar" in texto_abierto, f"Error: El botón no cambió a 'Cerrar...', dice '{texto_abierto}'"

            driver.execute_script("arguments[0].click();", btn_cenashow)
            time.sleep(1)

            texto_cerrado = btn_cenashow.text.strip().lower()
            assert "ver" in texto_cerrado, f"Error: El botón no volvió a 'Ver...', quedó en '{texto_cerrado}'"

            driver.execute_script("arguments[0].click();", btn_cenashow)
            esperar_fin_de_carga()
            time.sleep(1)
            # --- FIN NUEVA VALIDACIÓN ---

            tabla_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(p_tariffs) > 0, "No se encontró ningún elemento pTariff."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="7_Detalle_CenaShow_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_CenaShow",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
