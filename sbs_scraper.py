# pip install selenium webdriver-manager requests

import os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

URL = "https://www.sbs.gob.pe/supervisados-y-registros/registros/registros-del-sistema-de-seguros/intermediario-y-auxiliares-de-seguros/directorios-de-intermediarios-y-axuliares-de-seguros/corredores-de-seguros-personas-naturales-habiles-a-la-fecha"
SAVE_AS = "corredores_habilitados_sbs.xlsx"

# Inicia navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(URL)

# 1) Selecciona "Habilitados" en el combo Estado
select = Select(driver.find_element(By.ID, "ctl00_cphContent_dbEstado_DropDown"))  # ⚠️ revisa el id real, puede ser distinto
select.select_by_visible_text("Habilitados")
time.sleep(2)  # espera a que recargue la tabla

# 2) Encuentra el botón/enlace "Generar Listado"
link = driver.find_element(By.XPATH, "//a[contains(., 'Generar Listado')]")
href = link.get_attribute("href")

# 3) Descarga el archivo directamente con requests
driver.quit()
r = requests.get(href, timeout=60)
r.raise_for_status()
with open(SAVE_AS, "wb") as f:
    f.write(r.content)

print("✅ Descargado:", SAVE_AS)
