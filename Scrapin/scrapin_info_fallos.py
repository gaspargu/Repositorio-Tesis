import os
import json
import re
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def pop_start_word(texto):
    """
    Retorna el string sin la primera palabra (todo después del primer espacio).
    Si no hay espacios, retorna una cadena vacía.
    """
    partes = texto.split(' ', 1)
    return partes[1] if len(partes) > 1 else ''


# Crear carpeta para guardar metadatos proporcionados por Portal Unificado
folder_pu = "metadata-PortalUnificado"
if not os.path.exists(folder_pu):
    os.makedirs(folder_pu)

service = Service(GeckoDriverManager().install())
options = webdriver.FirefoxOptions()
options.add_argument("window-size=1200,800")
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get("https://juris.pjud.cl/busqueda?Laborales")
    
    # Esperar las cards
    cards = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "capa_elemento_lista_resultado_busqueda"))
    )
    print(f"Se encontraron {len(cards)} sentencias")
    
    for i, card in enumerate(cards, 1):
        try:
            print(f"\n=== Procesando sentencia {i} ===")
            
            # Esperar que los spans estén visibles en esta card
            titulos = WebDriverWait(card, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, './/span[@class="estilo_resultado_titulo"]'))
            )

            subtitulos = WebDriverWait(card, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, './/span[@class="estilo_resultado_subtitulo"]'))
            )

            materias = WebDriverWait(card, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, './/div[@class="estilo_resultado_listas"]'))
            )
            
            if len(titulos) >= 5 and len(subtitulos) >= 1:
                datos = {
                    'ROL': pop_start_word(titulos[0].text),
                    'Caratulado': pop_start_word(titulos[1].text),
                    'Fecha': pop_start_word(titulos[2].text),
                    'Materia': [materia.text for materia in materias],
                    'Tribunal': pop_start_word(titulos[4].text),
                    'Juez(a)': pop_start_word(subtitulos[0].text)
                }
                
                for clave, valor in datos.items():
                    print(f"{clave}: {valor}")
                
                # Guardar en archivo JSON
                nombre_archivo = f"sentencia_{i}.json"
                ruta_archivo = os.path.join(folder_pu, nombre_archivo)
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump(datos, f, ensure_ascii=False, indent=4)

                print(f"Archivo guardado: {ruta_archivo}")
                print("-" * 50)
            
            else:
                print(f"⚠️  Card {i} incompleta")
                
        except Exception as e:
            print(f"❌ Error en card {i}: {e}")
            continue
            
except Exception as e:
    print(f"❌ Error general: {e}")
    
finally:
    driver.quit()


