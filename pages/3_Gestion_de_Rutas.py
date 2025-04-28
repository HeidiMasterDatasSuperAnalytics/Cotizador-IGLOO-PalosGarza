import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO

# Función para convertir imagen a base64
def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Cargar logos
logo_claro = Image.open("Igloo Original.png")
logo_oscuro = Image.open("Igloo White.png")
logo_claro_b64 = image_to_base64(logo_claro)
logo_oscuro_b64 = image_to_base64(logo_oscuro)

# Mostrar logos
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

# Título
st.title("Gestión de Rutas Guardadas")

# Rutas de los archivos
RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

# Cargar datos generales
def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    datos_generales = cargar_datos_generales()

    tipo_cambio_usd = float(datos_generales.get("Tipo de cambio USD", 17.5))
    tipo_cambio_mxn = float(datos_generales.get("Tipo de cambio MXN", 1.0))
    precio_diesel = float(datos_generales.get("Costo Diesel", 24))

    # Calcular tipos de cambio
    df["Tipo_Cambio"] = df["Moneda"].apply(lambda x: tipo_cambio_usd if x == "USD" else tipo_cambio_mxn)
    df["Tipo_Cambio_Cruce"] = df["Moneda_Cruce"].apply(lambda x: tipo_cambio_usd if x == "USD" else tipo_cambio_mxn)

    # Insertar columna de Precio Diesel SOLO si existe 'Costo_Diesel'
    if "Costo_Diesel" in df.columns:
        if "Precio_Diesel" not in df.columns:
            df.insert(df.columns.get_loc("Costo_Diesel"), "Precio_Diesel", precio_diesel)

    # Reubicar columnas Moneda y Tipo Cambio
    moneda = df.pop("Moneda")
    tipo_cambio = df.pop("Tipo_Cambio")
    df.insert(df.columns.get_loc("Destino") + 1, "Moneda", moneda)
    df.insert(df.columns.get_loc("Moneda") + 1, "Tipo_Cambio", tipo_cambio)

    # Reubicar columnas de Cruce
    moneda_cruce = df.pop("Moneda_Cruce")
    tipo_cambio_cruce = df.pop("Tipo_Cambio_Cruce")
    cruce_original = df.pop("Cruce_Original")
    cruce_total = df.pop("Cruce_Total")
    df.insert(df.columns.get_loc("Ingreso_Total") + 1, "Moneda_Cruce", moneda_cruce)
    df.insert(df.columns.get_loc("Moneda_Cruce") + 1, "Tipo_Cambio_Cruce", tipo_cambio_cruce)
    df.insert(df.columns.get_loc("Tipo_Cambio_Cruce") + 1, "Cruce_Original", cruce_original)
    df.insert(df.columns.get_loc("Cruce_Original") + 1, "Cruce_Total", cruce_total)

    # Mostrar tabla
    st.dataframe(df, use_container_width=True)

    # Opciones para eliminar rutas
    st.subheader("Eliminar rutas")
    indices = st.multiselect("Selecciona índices a eliminar", df.index.tolist())
    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.rerun()

    # Opciones para editar rutas
    st.subheader("Editar ruta existente")
    indice_editar = st.selectbox("Selecciona el índice para editar", df.index.tolist())

    if indice_editar is not None:
        ruta = df.loc[indice_editar]

        st.markdown("### Edita los valores:")

        # Capturar valores
        tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta["Tipo"]))
        cliente = st.text_input("Cliente", value=ruta["Cliente"])
        origen = st.text_input("Origen", value=ruta["Origen"])
        destino = st.text_input("Destino", value=ruta["Destino"])
        km = st.number_input("Kilómetros", min_value=0.0, value=float(ruta["KM"]))

        moneda = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda"]))
        ingreso_original = st.number_input(f"Ingreso Flete en {moneda}", min_value=0.0, value=float(ruta["Ingreso_Original"]))
        tipo_cambio_ing = tipo_cambio_usd if moneda == "USD" else tipo_cambio_mxn
        ingreso_total = ingreso_original * tipo_cambio_ing

        moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda_Cruce"]))
        cruce_original = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0, value=float(ruta["Cruce_Original"]))
        tipo_cambio_cru = tipo_cambio_usd if moneda_cruce == "USD" else tipo_cambio_mxn
        cruce_total = cruce_original * tipo_cambio_cru

        casetas = st.number_input("Casetas", min_value=0.0, value=float(ruta["Casetas"]))
        horas_termo = st.number_input("Horas Termo", min_value=0.0, value=float(ruta["Horas_Termo"]))

        lavado_termo = st.number_input("Lavado Termo", min_value=0.0, value=float(ruta["Lavado_Termo"]))
        movimiento_local = st.number_input("Movimiento Local", min_value=0.0, value=float(ruta["Movimiento_Local"]))
        puntualidad = st.number_input("Puntualidad", min_value=0.0, value=float(ruta["Puntualidad"]))
        pension = st.number_input("Pensión", min_value=0.0, value=float(ruta["Pension"]))
        estancia = st.number_input("Estancia", min_value=0.0, value=float(ruta["Estancia"]))
        fianza_termo = st.number_input("Fianza Termo", min_value=0.0, value=float(ruta["Fianza_Termo"]))
        renta_termo = st.number_input("Renta Termo", min_value=0.0, value=float(ruta["Renta_Termo"]))

        if st.button("Guardar cambios en ruta"):
            df.loc[indice_editar] = [
                ruta["Fecha"], tipo, cliente, origen, destino, km,
                moneda, ingreso_original, tipo_cambio_ing, ingreso_total,
                moneda_cruce, tipo_cambio_cru, cruce_original, cruce_total,
                casetas, horas_termo,
                lavado_termo, movimiento_local, puntualidad, pension, estancia, fianza_termo, renta_termo
            ]
            df.to_csv(RUTA_RUTAS, index=False)
            st.success("✅ Ruta actualizada correctamente.")
            st.rerun()

else:
    st.warning("No hay rutas capturadas todavía.")
