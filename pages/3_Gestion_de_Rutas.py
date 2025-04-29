import streamlit as st
import pandas as pd
import os

# Ruta del archivo
RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🗂️ Gestión de Rutas Guardadas")

# Cargar rutas guardadas
if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    st.subheader("📋 Rutas Registradas")
    st.dataframe(df, use_container_width=True)

    st.markdown(f"**Total de rutas registradas:** {len(df)}")

    st.markdown("---")

    # Eliminar rutas
    st.subheader("🗑️ Eliminar rutas")
    indices = st.multiselect("Selecciona los índices a eliminar", df.index.tolist())

    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.experimental_rerun()

    st.markdown("---")

    # Editar rutas
    st.subheader("✏️ Editar Ruta Existente")
    indice_editar = st.selectbox("Selecciona el índice a editar", df.index.tolist())

    if indice_editar is not None:
        ruta = df.loc[indice_editar]

        st.markdown("### Modifica los valores principales:")
        
        fecha = st.date_input("Fecha", pd.to_datetime(ruta.get("Fecha", pd.Timestamp.now())))
        tipo = st.selectbox("Tipo", ["IMPO", "EXPO", "VACIO"], index=["IMPO", "EXPO", "VACIO"].index(ruta.get("Tipo", "IMPO")))
        cliente = st.text_input("Cliente", value=ruta.get("Cliente", ""))
        origen = st.text_input("Origen", value=ruta.get("Origen", ""))
        destino = st.text_input("Destino", value=ruta.get("Destino", ""))
        km = st.number_input("Kilómetros", min_value=0.0, value=float(ruta.get("KM", 0.0)))
        ingreso_original = st.number_input("Ingreso Flete Original", min_value=0.0, value=float(ruta.get("Ingreso_Original", 0.0)))

        if st.button("Guardar cambios"):
            df.at[indice_editar, "Fecha"] = fecha
            df.at[indice_editar, "Tipo"] = tipo
            df.at[indice_editar, "Cliente"] = cliente
            df.at[indice_editar, "Origen"] = origen
            df.at[indice_editar, "Destino"] = destino
            df.at[indice_editar, "KM"] = km
            df.at[indice_editar, "Ingreso_Original"] = ingreso_original

            df.to_csv(RUTA_RUTAS, index=False)
            st.success("✅ Ruta actualizada exitosamente.")
            st.experimental_rerun()
else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
