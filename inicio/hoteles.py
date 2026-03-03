import pytest
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

@allure.feature("Motor de Reservas - Hoteles")
@allure.story("Búsqueda, filtrado y reserva de hotel en Bariloche")
def test_reserva_hotel_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)

    with allure.step("1 a 3. Seleccionar pestaña Hoteles, ingresar destino y fechas"):
        # 1.5 Click en la pestaña de Hoteles
        tab_hoteles = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabHotels']")))
        tab_hoteles.click()
        
        # Damos un segundito para que la animación de la pestaña termine y muestre el formulario
        time.sleep(1) 

        # 2. Destino
        input_destino = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_ctrlHotelSearchControl_searchDestination")))
        input_destino.clear()
        input_destino.send_keys("Bariloche, Argentina")

        # 3. Calendario
        input_calendario = driver.find_element(By.ID, "txtCalendar")
        input_calendario.clear()
        input_calendario.send_keys("03/03/2026 - 10/03/2026")
        
        allure.attach(driver.get_screenshot_as_png(), name="Tab_Destino_y_Fechas", attachment_type=allure.attachment_type.PNG)

    with allure.step("4 a 9. Configurar habitaciones y pasajeros"):
        # 4. Hover para abrir el dropdown de pasajeros
        btn_pasajeros = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'pink-btn') and contains(@class, 'passengerQuantity-botton')]")))
        actions.move_to_element(btn_pasajeros).perform()
        time.sleep(1) # Pequeña espera para que la animación del ul termine

        # 5. Sumar 2 habitaciones (doble click)
        btn_rooms = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"QuantityModify(+1,'rooms')\"]")))
        actions.double_click(btn_rooms).perform()

        # 6. Sumar 2 adultos (doble click)
        btn_adults = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"QuantityModify(1,'adults')\"]")))
        actions.double_click(btn_adults).perform()

        # 7. Sumar 2 menores (doble click)
        btn_children = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@onclick=\"ChildrenModify(true)\"]")))
        actions.double_click(btn_children).perform()
        time.sleep(1) # Espera para que aparezcan los selects de edades

        # 8. Edad menor 1
        select_edad1 = Select(driver.find_element(By.ID, "childrenAge1"))
        select_edad1.select_by_visible_text("9")

        # 9. Volver a hacer hover por si se cerró, y seleccionar Edad menor 2
        actions.move_to_element(btn_pasajeros).perform()
        time.sleep(0.5)
        select_edad2 = Select(driver.find_element(By.ID, "childrenAge2"))
        select_edad2.select_by_visible_text("11")
        
        allure.attach(driver.get_screenshot_as_png(), name="Configuracion_Pasajeros", attachment_type=allure.attachment_type.PNG)

    with allure.step("10. Ejecutar Búsqueda"):
        wait.until(EC.element_to_be_clickable((By.ID, "btnSearch"))).click()
        # Esperamos a que la página de resultados cargue parcialmente
        time.sleep(5) 

    with allure.step("11 a 15. Aplicar Filtros laterales"):
        # 11 al 14. Checkboxes
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphSideMain_ctrlDispAndFamilyPlanFilter_repHotelInfo_ctl00_CheckBox1"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "ctl02_cphSideMain_ctrlDistrictFilter_repHotelInfo_ctl01_CheckBox1"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "ctl04_cphSideMain_ctrlCategoryFilter_repHotelInfo_ctl02_CheckBox1"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphSideMain_ctrlAmenityFilter_repHotelInfo_ctl02_CheckBox1"))).click()

        # 15. Click en aplicar filtros
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphSideMain_lnkFilter"))).click()
        time.sleep(4) # Esperamos la recarga de los resultados filtrados
        
        allure.attach(driver.get_screenshot_as_png(), name="Filtros_Aplicados", attachment_type=allure.attachment_type.PNG)

    with allure.step("16. Validar panel de resultados"):
        panel_resultados = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphMain_updMainPanel")))
        assert panel_resultados is not None, "El div de resultados no apareció."

    with allure.step("17. Validar componentes de la Card del Hotel y Ver Más"):
        # a. Imagen
        assert driver.find_elements(By.CSS_SELECTOR, "img[style*='height: 200px']"), "Falta la imagen de la card"
        # b. Nombre del hotel
        assert driver.find_elements(By.CSS_SELECTOR, "div[style*='font-size: 20px'] span"), "Falta el nombre del hotel"
        # c. Rating
        assert driver.find_elements(By.CSS_SELECTOR, "div.single-car-rating"), "Falta el rating en la card"
        # d. Zona
        assert driver.find_elements(By.CSS_SELECTOR, "div[style*='color: #6B72F2'] i"), "Falta la zona del hotel"
        # e. Descripción
        assert driver.find_elements(By.CSS_SELECTOR, "div[style*='margin-top: 2px'] p"), "Falta la descripción del hotel"
        # f. Disponibilidad
        assert driver.find_elements(By.CSS_SELECTOR, "div#True.available-hotel"), "Falta indicador de disponibilidad"
        # g. Precio
        caja_precio = driver.find_element(By.CSS_SELECTOR, "div[style*='background-color: #444444']")
        assert "Desde" in caja_precio.text, "Falta el texto 'Desde' en la caja de precio"
        
        # h. Click en Ver Más
        btn_ver_mas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#verMasbtn.btn.pink-btn.apreload")))
        btn_ver_mas.click()
        time.sleep(3)

    with allure.step("18. Validar información en el detalle del hotel"):
        # Validamos todos los elementos de la vista de detalle
        assert wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.h2name"))), "Falta el nombre (h2name)"
        assert driver.find_elements(By.CSS_SELECTOR, "div.rating.clearfix"), "Falta el rating"
        assert driver.find_elements(By.CSS_SELECTOR, "img.newSlide"), "Faltan las imágenes (newSlide)"
        assert driver.find_elements(By.XPATH, '//*[@id="aspnetForm"]/article/div[1]/div[2]/div[2]/div[4]'), "Falta la descripción principal"
        assert driver.find_elements(By.ID, "ctl00_cphMain_amenitiesList"), "Falta la lista de amenities"
        assert driver.find_elements(By.CSS_SELECTOR, "ul.nav.nav-tabs"), "Faltan los nav-tabs"
        assert driver.find_elements(By.CSS_SELECTOR, "h2.smallh2"), "Falta el nombre de la oferta (smallh2)"
        assert driver.find_elements(By.CSS_SELECTOR, "table.table.table-bordered.table-striped"), "Falta la tabla de precios/habitaciones"
        assert driver.find_elements(By.CSS_SELECTOR, "div.fleft"), "Faltan las políticas de cancelación"

        allure.attach(driver.get_screenshot_as_png(), name="Detalle_Hotel_Validado", attachment_type=allure.attachment_type.PNG)

    with allure.step("19 a 22. Sumar habitación, validar input y confirmar reserva"):
        # 19. Click en sumar
        btn_suma = wait.until(EC.element_to_be_clickable((By.ID, "72260-185813-105-1-2-Integration-26611-suma")))
        btn_suma.click()
        
        # 20. Validar que el input cambió (no es 0)
        input_cantidad = driver.find_element(By.ID, "185813")
        valor_input = input_cantidad.get_attribute("value")
        assert valor_input != "0", f"El input de cantidad sigue siendo 0. Valor actual: {valor_input}"

        # 21. Click en Guardar (usamos XPATH para buscar el input por una porción de su onclick)
        btn_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@onclick, 'Guardar(185813')]")))
        btn_guardar.click()

        # 22. Validar Alert
        try:
            alert = wait.until(EC.alert_is_present())
            texto_alert = alert.text.lower()
            allure.attach(texto_alert, name="Texto_del_Alert", attachment_type=allure.attachment_type.TEXT)
            
            assert "error" not in texto_alert, f"La reserva falló. El alert contiene un error: {alert.text}"
            
            alert.accept()
        except Exception as e:
            pytest.fail(f"No apareció el alert esperado o hubo un problema al validarlo: {e}")
