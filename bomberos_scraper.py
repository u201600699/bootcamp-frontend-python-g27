# -*- coding: utf-8 -*-
"""
Scraper Bomberos Perú (Últimas 24 horas) - Solo Selenium
- Extrae la tabla renderizada por JS
- Construye histórico en CSV con deduplicación por nro_parte (10 dígitos)
- Sin BeautifulSoup

Requisitos:
  py -m pip install selenium webdriver-manager pandas python-dateutil
"""

import re
import time
import pandas as pd
from pathlib import Path
from dateutil import parser as dparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://sgonorte.bomberosperu.gob.pe/24horas"
OUT = Path("bomberos_historico.csv")

# ---------- Utilidades ----------
def norm_txt(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def norm_header(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    return norm_txt(s)

def find_idx(headers_norm, candidates):
    """Devuelve el índice de la cabecera cuyo nombre contenga alguno de los candidatos."""
    for i, h in enumerate(headers_norm):
        for c in candidates:
            if c in h:
                return i
    return None

def parse_datetime(texto: str):
    """Parsea 'dd/mm/yyyy hh:mm:ss a.m./p.m.' (u otras variantes) a timestamp."""
    t = norm_txt(texto)
    if not t:
        return pd.NaT
    try:
        return pd.to_datetime(dparser.parse(t, dayfirst=True, fuzzy=True))
    except Exception:
        return pd.NaT

def limpiar_maquinas(s: str) -> str:
    """Reduce la lista a tokens tipo ABC-123, RES-14, AMB-60, etc."""
    if not s:
        return ""
    toks = [t.strip() for t in re.split(r"[,\s/;]+", s) if t.strip()]
    toks = [t for t in toks if re.match(r"^[A-ZÁÉÍÓÚ-]+\d*(?:-\d+)?$", t)]
    # quitar duplicados manteniendo orden
    return ", ".join(dict.fromkeys(toks).keys())

# ---------- Core Selenium ----------
def scrap_24h_selenium(headless: bool = True) -> pd.DataFrame:
    """
    Abre el sitio, espera la tabla renderizada y extrae filas.
    Devuelve DataFrame con columnas:
      nro_parte, fecha_hora, tipo, estado, distrito, direccion, maquinas
    """
    chrome_opts = webdriver.ChromeOptions()
    if headless:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)
    try:
        driver.get(URL)

        # Espera a que aparezca una tabla y que tenga filas
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table")))
        # un colchón para que terminen de inyectarse filas
        time.sleep(1.5)

        # Selecciona la primera tabla visible
        table = driver.find_element(By.XPATH, "(//table)[1]")

        # -------- Cabeceras --------
        th_elems = table.find_elements(By.XPATH, ".//thead//th")
        if not th_elems:
            # fallback si no hay thead
            th_elems = table.find_elements(By.XPATH, ".//tr[1]/*")
        headers = [norm_txt(th.text) for th in th_elems]
        headers_norm = [norm_header(h) for h in headers]

        idx_nro      = find_idx(headers_norm, ["n° parte", "nro parte", "nro.", "parte"])
        idx_fecha    = find_idx(headers_norm, ["fecha y hora", "fecha", "hora"])
        idx_tipo     = find_idx(headers_norm, ["tipo de emergencia", "tipo", "emergencia"])
        idx_estado   = find_idx(headers_norm, ["estado"])
        idx_distrito = find_idx(headers_norm, ["distrito"])
        idx_dir      = find_idx(headers_norm, ["direccion", "dirección"])
        idx_maq      = find_idx(headers_norm, ["maquinas", "máquinas", "unidad", "unidades"])

        # -------- Filas --------
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        if not rows:
            # fallback: todas menos la primera (cabecera)
            rows = table.find_elements(By.XPATH, ".//tr[position()>1]")

        registros = []
        for tr in rows:
            tds = tr.find_elements(By.XPATH, "./td")
            if not tds:
                continue

            sg = lambda i: norm_txt(tds[i].text) if i is not None and i < len(tds) else ""

            nro_parte = re.sub(r"\D", "", sg(idx_nro))
            if not re.fullmatch(r"\d{10}", nro_parte or ""):
                # si no hay 10 dígitos, saltamos (evita filas vacías o de totales)
                continue

            fecha_hora = parse_datetime(sg(idx_fecha))
            tipo       = sg(idx_tipo)
            estado_raw = sg(idx_estado).upper()
            estado     = "CERRADO" if "CERRADO" in estado_raw else ("ATENDIENDO" if "ATEND" in estado_raw else estado_raw)
            distrito   = sg(idx_distrito)
            direccion  = sg(idx_dir)
            maquinas   = limpiar_maquinas(sg(idx_maq))

            # Evita que "tipo" sea una fecha mal capturada
            if tipo and re.search(r"\d{2}/\d{2}/\d{4}", tipo):
                tipo = ""

            registros.append({
                "nro_parte": nro_parte,
                "fecha_hora": fecha_hora,
                "tipo": tipo,
                "estado": estado,
                "distrito": distrito,
                "direccion": direccion,
                "maquinas": maquinas
            })

        df = pd.DataFrame(registros)
        if df.empty:
            # Guarda HTML para depuración si no se obtuvo nada
            Path("page_source_empty.html").write_text(driver.page_source, encoding="utf-8")
            return df

        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
        df = df.drop_duplicates(subset=["nro_parte"]).sort_values("fecha_hora", ascending=False)
        return df

    finally:
        driver.quit()

# ---------- Persistencia del histórico ----------
def guardar_historico(df_new: pd.DataFrame, out_path: Path = OUT):
    if df_new is None or df_new.empty:
        print("⚠️ No se recuperaron filas nuevas (DF vacío).")
        return

    if out_path.exists():
        df_old = pd.read_csv(out_path, parse_dates=["fecha_hora"])
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        df_all = df_all.drop_duplicates(subset=["nro_parte"]).sort_values("fecha_hora")
    else:
        df_all = df_new.sort_values("fecha_hora")

    df_all.to_csv(out_path, index=False, encoding="utf-8")
    print(f"✅ Registros nuevos: {len(df_new)} | Total histórico: {len(df_all)}")
    print(f"📄 Archivo actualizado: {out_path.resolve()}")

# ---------- Main ----------
if __name__ == "__main__":
    df = scrap_24h_selenium(headless=True)
    print("Filas recuperadas en esta corrida:", 0 if df is None else len(df))
    if df is not None and not df.empty:
        print(df.head(5).to_string(index=False))
    guardar_historico(df)
