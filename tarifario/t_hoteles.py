import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Tarifario")
@allure.story("Consulta de Hoteles Completa (Tags, Modales y Tarifas)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo completo de Tarifario - Hoteles:
1. Login y navegación a la solapa Hoteles.
2. Búsqueda con destino Cachi.
3. Validación de existencia del tag "Hotel Recomendado" (featured-tag).
4. Validación del modal "Ver Proveedores" desde el listado.
5. Validación del modal "Ver Detalle" (link con estilo primario).
6. Ingreso al detalle del hotel.
7. Apertura del acordeón de habitación y validación de la tabla de tarifas.
""")
def test_tarifario_hoteles_completo(logged_in_driver):
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
        with allure.step("1 a 2. Navegar a Tarifario y solapa Hoteles"):
            btn_tarifario = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[href*='defaulttariff.aspx']"
            )))
            driver.execute_script("arguments[0].click();", btn_tarifario)
            esperar_fin_de_carga()

            try:
                btn_hoteles = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#hotel"], #a-hotels')))
                driver.execute_script("arguments[0].click();", btn_hoteles)
                esperar_fin_de_carga()
            except:
                pass 

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
                name="1_Busqueda_Hoteles_Cachi",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Validación Tag "Recomendado"
        # =========================
        with allure.step("4. Validar existencia del tag de Hotel Recomendado"):
            tag_recomendado = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.featured-tag"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tag_recomendado)
            time.sleep(0.5)

            assert tag_recomendado.is_displayed(), "No se visualiza el tag de Hotel Recomendado (featured-tag)."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="2_Tag_Recomendado",
                attachment_type=allure.attachment_type.PNG
            )

        # =========================
        # Validación Modal "Ver Proveedores"
        # =========================
        with allure.step("5. Abrir modal de Proveedores y validar"):
            btn_proveedores = wait.until(EC.element_to_be_clickable((
                By.XPATH, "(//button[contains(text(), 'Ver Proveedores') or contains(@onclick, 'openSuppliersModal')])[1]"
            )))
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_proveedores)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn_proveedores)
            
            modal_prov = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".modal.show, .modal.in, #suppliersModal"
            )))
            time.sleep(3)

            tds = modal_prov.find_elements(By.TAG_NAME, "td")
            assert any(td.text.strip() != "" for td in tds), "La tabla de proveedores está vacía."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="3_Modal_Proveedores",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            esperar_fin_de_carga()

        # =========================
        # Validación Modal "Ver Detalle"
        # =========================
        with allure.step("6. Click en botón Ver Detalle y validar modal"):
            btn_detalle = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@style, 'var(--amv-primary)') and contains(., 'Ver detalle')]"
            )))
            driver.execute_script("arguments[0].click();", btn_detalle)

            modal_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "div.modal-content"
            )))
            
            assert modal_detalle.is_displayed(), "El modal de detalle del hotel no se renderizó."
            time.sleep(1)

            allure.attach(
                driver.get_screenshot_as_png(),
                name="4_Modal_VerDetalle",
                attachment_type=allure.attachment_type.PNG
            )

            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        # =========================
        # Detalle Hotel y Acordeón (Tarifario)
        # =========================
        with allure.step("7. Ingresar al detalle del hotel, abrir acordeón y validar tarifas"):
            # 1. Entramos al detalle general del hotel
            btn_hotel = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.item1 a[id^='lnk']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_hotel)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_hotel)
            esperar_fin_de_carga()

            # 2. Buscamos y abrimos la primera opción del acordeón (dinámico)
            btn_habitacion = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "a[id^='accordeon-header-']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_habitacion)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_habitacion)
            
            # Esperamos a que la animación de Bootstrap despliegue el acordeón
            time.sleep(2)

            # 3. Validamos la tabla de tarifas ahora que es visible
            tabla_detalle = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, "table.table.table-bordered.table-striped.table-rounded"
            )))
            p_tariffs = tabla_detalle.find_elements(By.CSS_SELECTOR, "p.pTariff")

            assert len(p_tariffs) > 0, "No se encontró ningún elemento pTariff en la tabla del hotel."

            allure.attach(
                driver.get_screenshot_as_png(),
                name="5_Detalle_Hotel_Tarifas",
                attachment_type=allure.attachment_type.PNG
            )

    except Exception as e:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Fallo_Tarifario_Hoteles",
            attachment_type=allure.attachment_type.PNG
        )
        pytest.fail(f"El test falló durante la ejecución: {str(e)}")
