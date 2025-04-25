import streamlit as st
import pandas as pd
import os

st.title("Gestión de Rutas Guardadas")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

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

    # Insertar precio diesel si no existe
    if "Precio_Diesel" not in df.columns:
        df.insert(df.columns.get_loc("Costo_Diesel"), "Precio_Diesel", precio_diesel)

    # Asegurarse de tener las columnas bien organizadas
    columnas_ordenadas = [
        "Tipo", "Cliente", "Origen", "Destino", "KM",
        "Moneda", "Ingreso_Original", "Ingreso_Total",
        "Moneda_Cruce", "Cruce_Original", "Cruce_Total",
        "Casetas", "Horas_Termo", "Lavado_Termo", "Movimiento_Local",
        "Puntualidad", "Pension", "Estancia", "Fianza_Termo", "Renta_Termo",
        "Precio_Diesel", "Costo_Diesel", "Costo_Total"
    ]
    df = df[columnas_ordenadas]

    # Mostrar tabla ordenada
    st.dataframe(df, use_container_width=True)

    # 🔴 Eliminar rutas
    st.subheader("Eliminar rutas")
    indices = st.multiselect("Índices a eliminar", df.index.tolist())
    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.rerun()

    # 🟡 Editar ruta
    st.subheader("Editar una ruta existente")
    indice_editar = st.selectbox("Selecciona el índice de la ruta a editar", df.index.tolist())

    if indice_editar is not None:
        ruta = df.loc[indice_editar]

        st.markdown("### Modifica los valores y guarda los cambios:")

        tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta["Tipo"]))
        cliente = st.text_input("Cliente", value=ruta["Cliente"])
        origen = st.text_input("Origen", value=ruta["Origen"])
        destino = st.text_input("Destino", value=ruta["Destino"])
        km = st.number_input("Kilómetros recorridos", min_value=0.0, value=ruta["KM"])

        # Ingreso Flete
        moneda = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda"]))
        ingreso_original = st.number_input(f"Ingreso Flete en {moneda}", min_value=0.0, value=ruta["Ingreso_Original"])
        tipo_cambio_ing = tipo_cambio_usd if moneda == "USD" else tipo_cambio_mxn
        ingreso_total = ingreso_original * tipo_cambio_ing

        # Ingreso Cruce
        moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"], index=["MXN", "USD"].index(ruta["Moneda_Cruce"]))
        cruce_original = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0, value=ruta["Cruce_Original"])
        tipo_cambio_cruce = tipo_cambio_usd if moneda_cruce == "USD" else tipo_cambio_mxn
        cruce_total = cruce_original * tipo_cambio_cruce

        casetas = st.number_input("Costo de Casetas", min_value=0.0, value=ruta["Casetas"])
        horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0, value=ruta["Horas_Termo"])
        lavado_termo = st.number_input("Lavado de Termo", min_value=0.0, value=ruta["Lavado_Termo"])
        mov_local = st.number_input("Movimiento Local", min_value=0.0, value=ruta["Movimiento_Local"])
        puntualidad = st.number_input("Puntualidad", min_value=0.0, value=ruta["Puntualidad"])
        pension = st.number_input("Pensión", min_value=0.0, value=ruta["Pension"])
        estancia = st.number_input("Estancia", min_value=0.0, value=ruta["Estancia"])
        fianza = st.number_input("Fianza Termo Rentado/Externo", min_value=0.0, value=ruta["Fianza_Termo"])
        renta_termo = st.number_input("Renta de Termo", min_value=0.0, value=ruta["Renta_Termo"])

        rendimiento = float(datos_generales.get("Rendimiento Camion", 2.5))
        costo_diesel = (km / rendimiento) * precio_diesel if rendimiento > 0 else 0
        costos_extra = sum([lavado_termo, mov_local, puntualidad, pension, estancia, fianza, renta_termo])
        costo_total = costo_diesel + casetas + costos_extra + cruce_total

        if st.button("Guardar cambios en la ruta"):
            df.loc[indice_editar, "Tipo"] = tipo
            df.loc[indice_editar, "Cliente"] = cliente
            df.loc[indice_editar, "Origen"] = origen
            df.loc[indice_editar, "Destino"] = destino
            df.loc[indice_editar, "KM"] = km
            df.loc[indice_editar, "Moneda"] = moneda
            df.loc[indice_editar, "Ingreso_Original"] = ingreso_original
            df.loc[indice_editar, "Ingreso_Total"] = ingreso_total
            df.loc[indice_editar, "Moneda_Cruce"] = moneda_cruce
            df.loc[indice_editar, "Cruce_Original"] = cruce_original
            df.loc[indice_editar, "Cruce_Total"] = cruce_total
            df.loc[indice_editar, "Casetas"] = casetas
            df.loc[indice_editar, "Horas_Termo"] = horas_termo
            df.loc[indice_editar, "Lavado_Termo"] = lavado_termo
            df.loc[indice_editar, "Movimiento_Local"] = mov_local
            df.loc[indice_editar, "Puntualidad"] = puntualidad
            df.loc[indice_editar, "Pension"] = pension
            df.loc[indice_editar, "Estancia"] = estancia
            df.loc[indice_editar, "Fianza_Termo"] = fianza
            df.loc[indice_editar, "Renta_Termo"] = renta_termo
            df.loc[indice_editar, "Costo_Diesel"] = costo_diesel
            df.loc[indice_editar, "Costo_Total"] = costo_total

            df.to_csv(RUTA_RUTAS, index=False)
            st.success("✅ Ruta actualizada correctamente.")
            st.rerun()

    # 🟢 Backup
    st.subheader("📥 Descargar copia de seguridad")
    st.download_button("Descargar rutas_guardadas.csv", df.to_csv(index=False), file_name="rutas_guardadas.csv")

    if os.path.exists(RUTA_DATOS):
        datos_df = pd.read_csv(RUTA_DATOS)
        st.download_button("Descargar datos_generales.csv", datos_df.to_csv(index=False), file_name="datos_generales.csv")

    # 🔄 Restaurar desde archivo
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
