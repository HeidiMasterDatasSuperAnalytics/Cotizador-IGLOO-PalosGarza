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

# Función para aplicar color a valores
def color_value(value, tipo="resultado"):
    if tipo == "resultado":
        color = "green" if value >= 0 else "red"
    else:
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

# Archivos
RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

# Función para cargar datos generales
def load_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

# Función para calcular costos
def calcular_costos(ruta, datos):
    tipo = ruta["Tipo"]
    km = safe_number(ruta.get("KM", 0))
    horas_termo = safe_number(ruta.get("Horas_Termo", 0))

    diesel = float(datos.get("Costo Diesel", 24))
    rendimiento_camion = float(datos.get("Rendimiento Camion", 2.5))
    rendimiento_termo = float(datos.get("Rendimiento Termo", 3.0))
    bono_isr_imss = float(datos.get("Bono ISR IMSS", 0))

    costo_diesel_camion = (km / rendimiento_camion) * diesel if rendimiento_camion > 0 else 0
    costo_diesel_termo = horas_termo * rendimiento_termo * diesel if rendimiento_termo > 0 else 0

    if tipo == "IMPO":
        sueldo = km * float(datos.get("Pago x km IMPO", 2.1))
        bono = bono_isr_imss
    elif tipo == "EXPO":
        sueldo = km * float(datos.get("Pago x km EXPO", 2.5))
        bono = bono_isr_imss
    else:
        sueldo = float(datos.get("Pago fijo VACIO", 200))
        bono = 0

    casetas = safe_number(ruta.get("Casetas", 0))
    extras = sum([
        safe_number(ruta.get("Lavado_Termo", 0)),
        safe_number(ruta.get("Movimiento_Local", 0)),
        safe_number(ruta.get("Puntualidad", 0)),
        safe_number(ruta.get("Pension", 0)),
        safe_number(ruta.get("Estancia", 0)),
        safe_number(ruta.get("Fianza_Termo", 0)),
        safe_number(ruta.get("Renta_Termo", 0))
    ])

    ingreso_cruce = safe_number(ruta.get("Cruce_Original", 0))
    moneda_cruce = ruta.get("Moneda_Cruce", "MXN")
    tipo_cambio_usd = float(datos.get("Tipo de cambio USD", 17.5))
    tipo_cambio_mxn = float(datos.get("Tipo de cambio MXN", 1.0))

    if moneda_cruce == "USD":
        costo_cruce = ingreso_cruce * tipo_cambio_usd
    else:
        costo_cruce = ingreso_cruce * tipo_cambio_mxn

    costo_total = costo_diesel_camion + costo_diesel_termo + sueldo + bono + casetas + extras + costo_cruce

    return costo_diesel_camion, costo_diesel_termo, sueldo, bono, casetas, extras, costo_cruce, costo_total

# Simulación principal
if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    datos = load_datos_generales()

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]
    vacio_rutas = df[df["Tipo"] == "VACIO"]

    st.subheader("Selecciona rutas para simular")

    clientes_impo = impo_rutas["Cliente"].dropna().unique()
    clientes_expo = expo_rutas["Cliente"].dropna().unique()

    col1, col2 = st.columns(2)

    with col1:
        cliente_impo = st.selectbox("Cliente Importación", clientes_impo)
        rutas_impo_filtradas = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
        impo_sel = st.selectbox("Ruta Importación", rutas_impo_filtradas.index.tolist(), format_func=lambda x: f"{rutas_impo_filtradas.loc[x, 'Cliente']} ➔ {rutas_impo_filtradas.loc[x, 'Origen']} → {rutas_impo_filtradas.loc[x, 'Destino']}")

    with col2:
        cliente_expo = st.selectbox("Cliente Exportación", clientes_expo)
        rutas_expo_filtradas = expo_rutas[expo_rutas["Cliente"] == cliente_expo]
        expo_sel = st.selectbox("Ruta Exportación", rutas_expo_filtradas.index.tolist(), format_func=lambda x: f"{rutas_expo_filtradas.loc[x, 'Cliente']} ➔ {rutas_expo_filtradas.loc[x, 'Origen']} → {rutas_expo_filtradas.loc[x, 'Destino']}")

    usar_vacio = st.checkbox("¿Agregar ruta VACÍA entre IMPO y EXPO?")

    if usar_vacio and not vacio_rutas.empty:
        vacio_sel = st.selectbox("Ruta VACÍA (opcional)", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
    else:
        vacio_sel = None

    if st.button("🚛 Simular Vuelta Redonda"):
        tipo_cambio_usd = float(datos.get("Tipo de cambio USD", 17.5))
        tipo_cambio_mxn = float(datos.get("Tipo de cambio MXN", 1.0))

        rutas = []
        rutas.append(rutas_impo_filtradas.loc[[impo_sel]].squeeze())
        if vacio_sel is not None:
            rutas.append(vacio_rutas.loc[[vacio_sel]].squeeze())
        rutas.append(rutas_expo_filtradas.loc[[expo_sel]].squeeze())

        km_total = ingreso_total = diesel_camion_total = diesel_termo_total = sueldo_total = bono_total = casetas_total = extras_total = cruce_total = costo_total_general = 0

        st.subheader("🧾 Detalle por Ruta")

        for ruta in rutas:
            costo_diesel_camion, costo_diesel_termo, sueldo, bono, casetas, extras, costo_cruce, total_ruta = calcular_costos(ruta, datos)
            km_total += safe_number(ruta.get("KM", 0))

            ingreso_original = safe_number(ruta.get("Ingreso_Original", 0))
            moneda_ingreso = ruta.get("Moneda", "MXN")

            if moneda_ingreso == "USD":
                ingreso_ruta = ingreso_original * tipo_cambio_usd
            else:
                ingreso_ruta = ingreso_original * tipo_cambio_mxn

            ingreso_total += ingreso_ruta
            diesel_camion_total += costo_diesel_camion
            diesel_termo_total += costo_diesel_termo
            sueldo_total += sueldo
            bono_total += bono
            casetas_total += casetas
            extras_total += extras
            cruce_total += costo_cruce
            costo_total_general += total_ruta

            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Cliente']} ➔ {ruta['Origen']} → {ruta['Destino']}**
            - Moneda: {moneda_ingreso}
            - Ingreso Original: ${ingreso_original:,.2f}
            - Ingreso Convertido: ${ingreso_ruta:,.2f}
            - Diesel Camión: ${costo_diesel_camion:,.2f}
            - Diesel Termo: ${costo_diesel_termo:,.2f}
            - Sueldo Operador: ${sueldo:,.2f}
            - Bono ISR/IMSS: ${bono:,.2f}
            - Casetas: ${casetas:,.2f}
            - Extras: ${extras:,.2f}
            - Costo Cruce: ${costo_cruce:,.2f}
            - **Costo Total Ruta:** ${total_ruta:,.2f}
            """, unsafe_allow_html=True)

        utilidad_bruta = ingreso_total - costo_total_general
        estimado_costo_indirecto = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - estimado_costo_indirecto
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.subheader("📊 Resultado General")
        st.markdown(f"Ingreso Total Vuelta Redonda: {color_value(ingreso_total, tipo='ingreso')}", unsafe_allow_html=True)
        st.markdown(f"Costo Total Vuelta Redonda: {color_value(costo_total_general, tipo='ingreso')}", unsafe_allow_html=True)
        st.markdown(f"Utilidad Bruta: {color_value(utilidad_bruta)}", unsafe_allow_html=True)
        st.markdown(f"Estimado Costo Indirecto (35%): {color_value(estimado_costo_indirecto)}", unsafe_allow_html=True)
        st.markdown(f"Utilidad Neta Estimada: {color_value(utilidad_neta)}", unsafe_allow_html=True)

        color_utilidad = "green" if porcentaje_utilidad_neta >= 0 else "red"
        fondo_utilidad = "#e6f9e6" if porcentaje_utilidad_neta >= 0 else "#f9e6e6"
        st.markdown(f"""
        <div style='background-color: {fondo_utilidad}; padding: 10px; border-radius: 10px;'>
            <span style='color:{color_utilidad}; font-weight:bold;'>% Utilidad Neta: {porcentaje_utilidad_neta:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)

        # 🔵 Resumen de Gastos
        st.subheader("📋 Resumen de Gastos")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Total Kilómetros Recorridos:** {safe_number(km_total):,.2f} km")
            st.write(f"**Total Diesel Camión:** ${safe_number(diesel_camion_total):,.2f}")
            st.write(f"**Total Diesel Termo:** ${safe_number(diesel_termo_total):,.2f}")
            st.write(f"**Total Sueldos Operador:** ${safe_number(sueldo_total):,.2f}")

        with col2:
            st.write(f"**Total Bono ISR/IMSS:** ${safe_number(bono_total):,.2f}")
            st.write(f"**Total Casetas:** ${safe_number(casetas_total):,.2f}")
            st.write(f"**Total Extras:** ${safe_number(extras_total):,.2f}")
            st.write(f"**Total Costo Cruces:** ${safe_number(cruce_total):,.2f}")

else:
    st.warning("No hay rutas guardadas todavía para simular.")
