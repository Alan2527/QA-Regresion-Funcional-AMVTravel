import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Excursiones")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Este caso de prueba cubre el flujo de Tarifario - Excursiones:
1. Login silencioso y navegación a la pestaña Tarifario.
2. Cambio a la solapa Excursiones.
3. Ejecución de la búsqueda con filtros por defecto.
4. Apertura y validación del modal de Proveedores desde la vista de listado.
5. Cierre de modal y navegación al detalle de la excursión.
6. Validación de la tabla de tarifas.
""")
def test_tarifario_excursiones(logged_in_driver):
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

    try:
        # =========================
        # Navegación
        # =========================
        with allure.step("1 a 2. Navegar a Tarifario y solapa Excursiones"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            btn_excursiones = wait.until(EC.element_to_be_clickable((By.ID, "a-excursions")))
            driver.execute_script("arguments[0].click();", btn_excursiones)
            esperar_fin_de_carga()

        # =========================
        # Filtro y búsqueda (SIN TOCAR DESTINO)
        # =========================
        with allure.step("3. Ejecutar búsqueda con destino por defecto"):
            btn_buscar = wait.until(EC.presence_of_element_located((
                By.ID, "ctl00_cphMainSlider_ctrlTariffFilterControl_lnkView"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_buscar)
            time.sleep(1)
            btn_buscar.send_keys(Keys.ENTER)

            esperar_fin_de_carga()

            allure.attach(
                driver.get_screenshot_as_png(),
                name="1_Busqueda_Excursiones",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Modal proveedores desde el listado
        # =========================
        with allure.step("4. Abrir modal de Proveedores desde el listado y validar"):
            btn_proveedores = wait.until(EC.element_to_be_clickable((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_proveedores)
            time.sleep(1)

            # UN SOLO CLICK LIMPIO para no encender y apagar el modal por error
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            # Esperamos que el contenedor del modal en sí aparezca (cualquiera sea su ID o clase de Bootstrap)
            modal = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal"
            )))
            
            # Esperamos 3 segundos a que el Ajax termine de rellenar el modal
            time.sleep(3)

            # Buscamos de forma genérica CUALQUIER tabla dentro de ese modal
            tds = modal.find_elements(By.TAG_NAME, "td")
            texto_encontrado = any(td.text.strip() != "" for td in tds)

            assert texto_encontrado, "Validación fallida: La tabla de proveedores en el modal cargó vacía o no se encontró."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Modal_Proveedores_Abierto",
                attachment_type=allure.attachment_type.PNG
            )

            # CERRAR EL MODAL con la tecla ESCAPE y esperar a que desaparezca
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()

        # =========================
        # Detalle excursión
        # =========================
        with allure.step("5 y 6. Ingresar al detalle de la excursión y validar tabla de tarifas"):
            btn_excursion = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_excursion)
            time.sleep(1)
            
            # Navegamos al detalle de la excursión
            driver.execute_script("arguments[0].click();", btn_excursion)

            esperar_fin_de_carga()

            tabla_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(p_tariffs) > 0, "Validación fallida: No se encontró ningún elemento <p> con clase 'pTariff'."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Detalle_Excursion_Validado",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Excursiones",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
