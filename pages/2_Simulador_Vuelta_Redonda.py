import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO
import math

# Función para convertir imagen en base64
def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Función para manejar NaN como 0
def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and math.isnan(x))) else x

# Función para aplicar color azul o verde/rojo dependiendo del valor
def color_value(value, tipo="resultado"):
    if tipo == "resultado":
        color = "green" if value >= 0 else "red"
    else:  # para ingresos y costos
        color = "blue"
    return f"<span style='color:{color}; font-weight:bold;'>${value:,.2f}</span>"

# Cargar logos
logo_claro = Image.open("Igloo Original.png")
logo_oscuro = Image.open("Igloo White.png")
logo_claro_b64 = image_to_base64(logo_claro)
logo_oscuro_b64 = image_to_base64(logo_oscuro)

# Mostrar logo
st.markdown(f"""
    <div style='text-align: left; margin-bottom: 10px;'>
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

st.title("Simulador de Vuelta Redonda")

# (código intermedio no modificado para mantener flujo)

        st.subheader("📊 Resultado General")
        st.markdown(f"Ingreso Total Vuelta Redonda: {color_value(ingreso_total, tipo='ingreso')}", unsafe_allow_html=True)
        st.markdown(f"Costo Total Vuelta Redonda: {color_value(costo_total_general, tipo='ingreso')}", unsafe_allow_html=True)
        st.markdown(f"Utilidad Bruta: {color_value(utilidad_bruta)}", unsafe_allow_html=True)
        st.markdown(f"Estimado Costo Indirecto (35%): {color_value(estimado_costo_indirecto)}", unsafe_allow_html=True)
        st.markdown(f"Utilidad Neta Estimada: {color_value(utilidad_neta)}", unsafe_allow_html=True)
        st.info(f"% Utilidad Neta: {porcentaje_utilidad_neta:.2f}%")

# (código posterior no modificado para mantener flujo)
