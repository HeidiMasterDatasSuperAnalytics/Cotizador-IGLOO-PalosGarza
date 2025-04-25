import streamlit as st
import pandas as pd
import os

st.title("# Gestión de Rutas Guardadas")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    datos_generales = cargar_datos_generales()

    # Obtener tipo de cambio y diesel
    tipo_cambio_usd = float(datos_generales.get("Tipo de cambio USD", 17.5))
    tipo_cambio_mxn = float(datos_generales.get("Tipo de cambio MXN", 1.0))
    precio_diesel = float(datos_generales.get("Costo Diesel", 24))

    # Calcular tipo de cambio aplicado por fila
    df["Tipo_Cambio"] = df["Moneda"].apply(lambda x: tipo_cambio_usd if x == "USD" else tipo_cambio_mxn)

    # Insertar columnas para visualización
    df.insert(df.columns.get_loc("Costo_Diesel"), "Precio_Diesel", precio_diesel)
    moneda_col = df.pop("Moneda")
    df.insert(df.columns.get_loc("Destino") + 1, "Moneda", moneda_col)
    tipo_cambio_col = df.pop("Tipo_Cambio")
    df.insert(df.columns.get_loc("Moneda") + 1, "Tipo_Cambio", tipo_cambio_col)

    st.dataframe(df, use_container_width=True)

    # -----------------------
    # Eliminar rutas
    # -----------------------
    st.subheader("Eliminar rutas")
    indices = st.multiselect("Índices a eliminar", df.index.tolist())
    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.rerun()

    # -----------------------
    # Editar ruta
    # -----------------------
    st.subheader("Editar una ruta existente")
    indice_editar = st.selectbox("Selecciona el índice de la ruta a editar", df.index.tolist())

    if indice_editar is not None:
        ruta = df.loc[indice_editar]

        st.markdown("### Modifica los valores y guarda los cambios:")
        tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta["Tipo"]))
        cliente = st.text_input("Cliente", value=ruta["Cliente"])
        origen = st.text_input("Origen", value=ruta["Origen"])
        destino = st.text_input("Destino", value=ruta["Destino"])
        km = st.number_input("Kilómetros", min_value=0.0, value=ruta["KM"])
        horas_termo = st.number_input("Horas Termo", min_value=0.0, value=ruta["Horas_Termo"])
        casetas = st.number_input("Casetas", min_value=0.0, value=ruta["Casetas"])
        lavado = st.number_input("Lavado Termo", min_value=0.0, value=ruta["Lavado_Termo"])
        mov_local = st.number_input("Movimiento Local", min_value=0.0, value=ruta["Movimiento_Local"])
        puntualidad = st.number_input("Puntualidad", min_value=0.0, value=ruta["Puntualidad"])
        pension = st.number_input("Pensión", min_value=0.0, value=ruta["Pension"])
        estancia = st.number_input("Estancia", min_value=0.0, value=ruta["Estancia"])
        fianza = st.number_input("Fianza Termo", min_value=0.0, value=ruta["Fianza_Termo"])
        renta = st.number_input("Renta Termo", min_value=0.0, value=ruta["Renta_Termo"])
        moneda = st.selectbox("Moneda", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda"]))
        ingreso_original = st.number_input(f"Ingreso en {moneda}", min_value=0.0, value=ruta["Ingreso_Original"])

        tipo_cambio = tipo_cambio_usd if moneda == "USD" else tipo_cambio_mxn
        ingreso_total = ingreso_original * tipo_cambio
        rendimiento = float(datos_generales.get("Rendimiento Camion", 2.5))
        costo_diesel = (km / rendimiento) * precio_diesel if rendimiento > 0 else 0
        costos_extra = sum([lavado, mov_local, puntualidad, pension, estancia, fianza, renta])
        costo_total = costo_diesel + casetas + costos_extra

        if st.button("Guardar cambios en la ruta"):
            df.at[indice_editar, :] = [
                tipo, cliente, origen, destino, km, horas_termo, casetas,
                lavado, mov_local, puntualidad, pension, estancia,
                fianza, renta, moneda, ingreso_original, ingreso_total,
                costo_diesel, costo_total
            ]
            df.to_csv(RUTA_RUTAS, index=False)
            st.success("✅ Ruta actualizada correctamente.")
            st.rerun()

    # -----------------------
    # Copias de seguridad
    # -----------------------
    st.subheader("📥 Descargar copia de seguridad")
    st.download_button("Descargar rutas_guardadas.csv", df.to_csv(index=False), file_name="rutas_guardadas.csv")

    if os.path.exists(RUTA_DATOS):
        datos_df = pd.read_csv(RUTA_DATOS)
        st.download_button("Descargar datos_generales.csv", datos_df.to_csv(index=False), file_name="datos_generales.csv")

    # -----------------------
    # Subir archivos para restaurar datos
    # -----------------------
    st.subheader("📤 Subir archivos para restaurar datos")

    rutas_file = st.file_uploader("Subir rutas_guardadas.csv", type="csv")
    if rutas_file:
        rutas_df = pd.read_csv(rutas_file)
        rutas_df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas restauradas correctamente.")
        st.rerun()

    datos_file = st.file_uploader("Subir datos_generales.csv", type="csv")
    if datos_file:
        datos_df = pd.read_csv(datos_file)
        datos_df.to_csv(RUTA_DATOS, index=False)
        st.success("✅ Datos generales restaurados correctamente.")
        st.rerun()

else:
    st.warning("No hay rutas guardadas aún.")

