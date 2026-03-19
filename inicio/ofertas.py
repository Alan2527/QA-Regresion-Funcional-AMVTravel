import pytest
import allure
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@allure.feature("Ofertas / Oportunidades")
@allure.story("Búsqueda y configuración de Oportunidad a 7 días")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre la configuración de una oferta:
1. Navegación a la pestaña de Oportunidades.
2. Búsqueda con fecha dinámica (hoy + 7 días) y cierre del calendario.
3. Configuración de noches, pasajeros, habitaciones y categoría mediante selectores custom.
4. Avance de pantalla y selección de un servicio específico (checkbox 163).
""")
def test_ofertas_flujo_completo(logged_in_driver):
    # Inyectamos el driver que ya viene con el login resuelto desde conftest.py
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)

    # Helper interno para manejar los selectores custom de la UI
    def seleccionar_dropdown(xpath_div, valor):
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_div))).click()
        time.sleep(0.5) # Pausa breve para que la animación del combo despliegue las opciones
        xpath_opcion = f"//li[text()='{valor}'] | //div[contains(@class, 'option') and text()='{valor}'] | //a[text()='{valor}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion))).click()

    try:
        with allure.step("1. Navegar a Oportunidades y buscar por fecha dinámica"):
            # 2. Click en la pestaña Oportunidad
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_lblOpportunity"))).click()
            
            # 3. Calcular fecha (hoy + 7 días) y tipear
            fecha_oferta = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
            input_fecha = wait.until(EC.element_to_be_clickable((By.ID, "txtOpportunityCalendar")))
            input_fecha.clear()
            input_fecha.send_keys(fecha_oferta)
            
            # Cerrar el calendario superpuesto apretando ESCAPE para liberar el botón Buscar
            input_fecha.send_keys(Keys.ESCAPE)
            time.sleep(0.5) 
            
            # 4. Click en buscar
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and contains(@class, 'btnSearchOpportunity')]"))).click()

        with allure.step("2. Configurar Destino (Noches, Pasajeros, Habitaciones y Categoría)"):
            # 5 y 6. Click en div destino/noches y seleccionar 8
            seleccionar_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[1]/div[2]/div[1]/div[2]/div", "8")
            
            # 7 y 8. Click en div pasajeros y seleccionar 1
            seleccionar_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[3]/div/div[1]", "1")
            
            # 9 y 10. Click en div habitaciones y seleccionar 1
            seleccionar_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[2]/div/div[1]", "1")
            
            # 11 y 12. Click en div categoría y seleccionar 3
            seleccionar_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[1]/div/div[1]", "3")

        with allure.step("3. Avanzar y agregar servicio adicional"):
            # 13. Siguiente
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lnkNext"))).click()
            
            # 14. Click en Añadir Servicio
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lvDestinations_ctrl0_lnkAddService"))).click()
            
            # 15. Marcar checkbox con data-id="163" si no está marcado
            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @data-id='163']")))
            if not checkbox.is_selected():
                checkbox.click()
            
            # 16. Click en el modal para agregar el servicio
            wait.until(EC.element_to_be_clickable((By.ID, "lnkAddServiceModal"))).click()
            
            # Captura de éxito para el reporte de Allure
            allure.attach(driver.get_screenshot_as_png(), name="Oferta_Configurada_Exitosamente", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        # Captura de error para el reporte de Allure
        allure.attach(driver.get_screenshot_as_png(), name="Fallo_en_Ofertas", attachment_type=allure.attachment_type.PNG)
        pytest.fail(f"El test falló durante la ejecución de los pasos: {e}")
