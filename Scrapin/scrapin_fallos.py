import os
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

# Crear carpeta para guardar fallos
folder_fallos = "fallos"
if not os.path.exists(folder_fallos):
    os.makedirs(folder_fallos)

service = Service(GeckoDriverManager().install())
options = webdriver.FirefoxOptions()
options.add_argument("window-size=1200,800")
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get("https://juris.pjud.cl/busqueda?Laborales")
    cards = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "capa_elemento_lista_resultado_busqueda")
            )
        )
    print(f"Se encontraron {len(cards)} sentencias")

    div_xpath = "//div[starts-with(@id, 'capa_texto_sentencia_')]"
    div_sentencia = driver.find_element(By.XPATH, div_xpath)
    for i, card in enumerate(cards, start=1):
        boton_ver = card.find_element(By.XPATH, ".//button[contains(text(), 'Ver sentencia')]")
        driver.execute_script("arguments[0].click();", boton_ver)

        old_text = div_sentencia.text

        # Esperar a que el div cambie su contenido
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element(By.XPATH, div_xpath).text != old_text
        )

        # Reasignar el div con el nuevo texto
        div_sentencia = driver.find_element(By.XPATH, div_xpath)
        
        # Guardar el fallo
        nombre_txt = f"sentencia_{i}.txt"
        ruta_txt = os.path.join(folder_fallos, nombre_txt)
        with open(ruta_txt, "w", encoding="utf-8") as f_txt:
            f_txt.write(div_sentencia.text)
        print(f"Sentencia {i} guardada en {ruta_txt}")
except Exception as e:
    print(f"❌ Error general: {e}")

finally:
    driver.quit()

