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

st.title("Gestión de Rutas Guardadas")

# Archivos
RUTA_RUTAS = "rutas_guardadas.csv"

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    # Ordenar columnas si existen
    columnas_ordenadas = [
        "Fecha", "Tipo", "Cliente", "Origen", "Destino", "KM",
        "Moneda", "Ingreso_Original", "Moneda_Cruce", "Cruce_Original", "Costo_Cruce",
        "Casetas", "Horas_Termo", "Lavado_Termo", "Movimiento_Local",
        "Puntualidad", "Pension", "Estancia", "Fianza_Termo", "Renta_Termo"
    ]
    columnas_disponibles = [col for col in columnas_ordenadas if col in df.columns]
    df = df[columnas_disponibles]

    st.subheader("📋 Rutas capturadas:")
    st.dataframe(df, use_container_width=True)

    # 🔴 Eliminar rutas
    st.subheader("Eliminar rutas")
    indices = st.multiselect("Selecciona los índices a eliminar", df.index.tolist())

    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.rerun()

    # 🟡 Editar rutas
    st.subheader("Editar ruta existente")
    indice_editar = st.selectbox("Selecciona el índice a editar", df.index.tolist())

    if indice_editar is not None:
        ruta = df.loc[indice_editar]

        st.markdown("### Modifica los valores:")

        fecha = st.date_input("Fecha de captura", pd.to_datetime(ruta["Fecha"]))
        tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta["Tipo"]))
        cliente = st.text_input("Cliente", value=ruta["Cliente"])
        origen = st.text_input("Origen", value=ruta["Origen"])
        destino = st.text_input("Destino", value=ruta["Destino"])
        km = st.number_input("Kilómetros recorridos", min_value=0.0, value=float(ruta["KM"]))
        moneda = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda"]))
        ingreso_original = st.number_input(f"Ingreso Flete en {moneda}", min_value=0.0, value=float(ruta["Ingreso_Original"]))
        moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda_Cruce"]))
        ingreso_cruce = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0, value=float(ruta["Cruce_Original"]))
        costo_cruce = st.number_input("Costo de Cruce", min_value=0.0, value=float(ruta["Costo_Cruce"]))
        casetas = st.number_input("Casetas", min_value=0.0, value=float(ruta["Casetas"]))
        horas_termo = st.number_input("Horas Termo", min_value=0.0, value=float(ruta["Horas_Termo"]))
        lavado_termo = st.number_input("Lavado Termo", min_value=0.0, value=float(ruta["Lavado_Termo"]))
        movimiento_local = st.number_input("Movimiento Local", min_value=0.0, value=float(ruta["Movimiento_Local"]))
        puntualidad = st.number_input("Puntualidad", min_value=0.0, value=float(ruta["Puntualidad"]))
        pension = st.number_input("Pensión", min_value=0.0, value=float(ruta["Pension"]))
        estancia = st.number_input("Estancia", min_value=0.0, value=float(ruta["Estancia"]))
        fianza_termo = st.number_input("Fianza Termo Rentado/Externo", min_value=0.0, value=float(ruta["Fianza_Termo"]))
        renta_termo = st.number_input("Renta Termo", min_value=0.0, value=float(ruta["Renta_Termo"]))

        if st.button("Guardar cambios en la ruta"):
            df.loc[indice_editar, columnas_disponibles] = [
                fecha, tipo, cliente, origen, destino, km,
                moneda, ingreso_original, moneda_cruce, ingreso_cruce, costo_cruce,
                casetas, horas_termo, lavado_termo, movimiento_local,
                puntualidad, pension, estancia, fianza_termo, renta_termo
            ]
            df.to_csv(RUTA_RUTAS, index=False)
            st.success("✅ Ruta actualizada correctamente.")
            st.rerun()

else:
    st.warning("No hay rutas capturadas todavía.")
