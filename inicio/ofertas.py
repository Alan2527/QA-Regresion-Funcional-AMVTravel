from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

# Inicialización del driver y esperas
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

try:
    # 1. Login
    # (Reemplazar con la URL exacta y los pasos de login que ya usas en servicios.py)
    driver.get("https://qa.amv.travel/login")
    # wait.until(EC.presence_of_element_located((By.ID, "txtUsername"))).send_keys("usuario")
    # wait.until(EC.presence_of_element_located((By.ID, "txtPassword"))).send_keys("clave")
    # wait.until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()

    # 2. Click en la pestaña de Oportunidades
    wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_lblOpportunity"))).click()

    # 3. Calcular fecha (hoy + 7 días) y escribirla en el input
    fecha_oferta = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    input_fecha = wait.until(EC.element_to_be_clickable((By.ID, "txtOpportunityCalendar")))
    input_fecha.clear()
    input_fecha.send_keys(fecha_oferta)

    # 4. Click en el botón de búsqueda
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and contains(@class, 'btnSearchOpportunity pink-btn')]"))).click()

    # Función auxiliar para manejar los selectores custom (Dropdowns)
    # Hace clic en el DIV principal y luego busca la opción por su texto visible.
    def seleccionar_en_dropdown(xpath_div, valor):
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_div))).click()
        time.sleep(0.5) # Pequeña pausa para permitir que la animación del dropdown lo haga visible
        # Se asume que las opciones se renderizan como <li> o elementos clickeables que contienen el número
        xpath_opcion = f"//li[text()='{valor}'] | //div[contains(@class, 'option') and text()='{valor}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion))).click()

    # 5 y 6. Click en div destino/noches y seleccionar 8
    seleccionar_en_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[1]/div[2]/div[1]/div[2]/div", "8")

    # 7 y 8. Click en div pasajeros y seleccionar 1
    seleccionar_en_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[3]/div/div[1]", "1")

    # 9 y 10. Click en div habitaciones y seleccionar 1
    seleccionar_en_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[2]/div/div[1]", "1")

    # 11 y 12. Click en div categoría/otro y seleccionar 3
    seleccionar_en_dropdown("//*[@id='updCustomTourDestination']/div[1]/div[2]/div[2]/div[1]/div/div[1]", "3")

    # 13. Click en el botón Siguiente
    wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lnkNext"))).click()

    # 14. Click en Añadir Servicio
    wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMain_lvDestinations_ctrl0_lnkAddService"))).click()

    # 15. Marcar checkbox con data-id="163"
    checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @data-id='163']")))
    if not checkbox.is_selected():
        checkbox.click()

    # 16. Click en el modal para agregar el servicio
    wait.until(EC.element_to_be_clickable((By.ID, "lnkAddServiceModal"))).click()

    print("Script completado exitosamente.")

except Exception as e:
    print(f"Ocurrió un error durante la ejecución: {e}")

finally:
    # driver.quit() # Descomentar para que cierre el navegador al finalizar
    pass
