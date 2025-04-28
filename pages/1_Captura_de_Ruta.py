import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO

# Función para convertir imagen en base64
def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Cargar imágenes
logo_claro = Image.open("Igloo Original.png")
logo_oscuro = Image.open("Igloo White.png")

# Convertir a base64
logo_claro_b64 = image_to_base64(logo_claro)
logo_oscuro_b64 = image_to_base64(logo_oscuro)

# Mostrar logo en esquina superior izquierda
st.markdown(f"""
    <div style='position: absolute; top: 10px; left: 10px;'>
        <img src="data:image/png;base64,{logo_claro_b64}" class="logo-light" style="height:50px;">
        <img src="data:image/png;base64,{logo_oscuro_b64}" class="logo-dark" style="height:50px;">
    </div>
    <style>
    @media (prefers-color-scheme: dark) {{
        .logo-light {{ display: none; }}
        .logo-dark {{ display: inline; }}
    }}
    @media (prefers-color-scheme: light) {{
        .logo-light {{ display: inline; }}
        .logo-dark {{ display: none; }}
    }}
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("Captura de Ruta")

# Ruta donde guardamos
RUTA_RUTAS = "rutas_guardadas.csv"

# Si ya existe cargamos, si no creamos vacío
if os.path.exists(RUTA_RUTAS):
    df_rutas = pd.read_csv(RUTA_RUTAS)
else:
    df_rutas = pd.DataFrame()

# Formulario
with st.form("captura_ruta"):
    fecha = st.date_input("Fecha de captura")
    tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
    cliente = st.text_input("Nombre del Cliente")
    origen = st.text_input("Origen")
    destino = st.text_input("Destino")
    km = st.number_input("Kilómetros recorridos", min_value=0.0)

    moneda_ingreso = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"])
    ingreso_flete = st.number_input(f"Ingreso Flete en {moneda_ingreso}", min_value=0.0)

    moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"])
    ingreso_cruce = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0)

    casetas = st.number_input("Costo de Casetas", min_value=0.0)
    horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0)

    lavado_termo = st.number_input("Lavado Termo", min_value=0.0)
    movimiento_local = st.number_input("Movimiento Local", min_value=0.0)
    puntualidad = st.number_input("Puntualidad", min_value=0.0)
    pension = st.number_input("Pensión", min_value=0.0)
    estancia = st.number_input("Estancia", min_value=0.0)
    fianza_termo = st.number_input("Fianza Termo Rentado/Externo", min_value=0.0)
    renta_termo = st.number_input("Renta de Termo", min_value=0.0)

    submitted = st.form_submit_button("Guardar Ruta")

# Acción al guardar
if submitted:
    nueva_ruta = {
        "Fecha": fecha,
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "KM": km,
        "Moneda": moneda_ingreso,
        "Ingreso_Original": ingreso_flete,
        "Moneda_Cruce": moneda_cruce,
        "Cruce_Original": ingreso_cruce,
        "Casetas": casetas,
        "Horas_Termo": horas_termo,
        "Lavado_Termo": lavado_termo,
        "Movimiento_Local": movimiento_local,
        "Puntualidad": puntualidad,
        "Pension": pension,
        "Estancia": estancia,
        "Fianza_Termo": fianza_termo,
        "Renta_Termo": renta_termo
    }

    df_rutas = pd.concat([df_rutas, pd.DataFrame([nueva_ruta])], ignore_index=True)
    df_rutas.to_csv(RUTA_RUTAS, index=False)
    st.success("✅ La ruta se guardó exitosamente.")
    st.rerun()  # <-- ahora corregido
