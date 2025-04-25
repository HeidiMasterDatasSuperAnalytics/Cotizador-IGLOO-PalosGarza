import streamlit as st
import pandas as pd
import os

st.title("# Simulador de Vuelta Redonda")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

def load_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

def calcular_costos(ruta, datos):
    tipo = ruta["Tipo"]
    km = ruta["KM"]
    diesel = float(datos.get("Costo Diesel", 24))
    rendimiento = float(datos.get("Rendimiento Camion", 2.5))

    # Costo Diesel
    costo_diesel = (km / rendimiento) * diesel if rendimiento > 0 else 0

    # Sueldo operador
    if tipo == "IMPO":
        sueldo = km * float(datos.get("Pago x km IMPO", 2.1))
    elif tipo == "EXPO":
        sueldo = km * float(datos.get("Pago x km EXPO", 2.5))
    else:  # VACIO
        sueldo = float(datos.get("Pago fijo VACIO", 200))

    return costo_diesel, sueldo

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    datos = load_datos_generales()

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]
    vacio_rutas = df[df["Tipo"] == "VACIO"]

    st.subheader("Selecciona rutas para simular")

    impo_sel = st.selectbox("Ruta de Importación", impo_rutas.index.tolist(), format_func=lambda x: f"{impo_rutas.loc[x, 'Origen']} → {impo_rutas.loc[x, 'Destino']}")
    expo_sel = st.selectbox("Ruta de Exportación", expo_rutas.index.tolist(), format_func=lambda x: f"{expo_rutas.loc[x, 'Origen']} → {expo_rutas.loc[x, 'Destino']}")
    usar_vacio = st.checkbox("¿Agregar ruta VACÍA entre IMPO y EXPO?")

    if usar_vacio and not vacio_rutas.empty:
        vacio_sel = st.selectbox("Ruta VACÍA (opcional)", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
    else:
        vacio_sel = None

    if st.button("Simular Vuelta Redonda"):
        rutas = [impo_rutas.loc[impo_sel]]
        if vacio_sel is not None:
            rutas.append(vacio_rutas.loc[vacio_sel])
        rutas.append(expo_rutas.loc[expo_sel])

        ingreso_total = 0
        diesel_total = 0
        sueldo_total = 0

        st.subheader("🧾 Detalle por Ruta")

        for ruta in rutas:
            costo_diesel, sueldo = calcular_costos(ruta, datos)
            total = costo_diesel + sueldo
            ingreso_total += ruta["Ingreso_Total"]
            diesel_total += costo_diesel
            sueldo_total += sueldo

            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Origen']} → {ruta['Destino']}**
            - Ingreso: ${ruta['Ingreso_Total']:,.2f}
            - Diesel: ${costo_diesel:,.2f}
            - Sueldo operador: ${sueldo:,.2f}
            - **Costo Total Ruta:** ${total:,.2f}
            """)

        costo_total = diesel_total + sueldo_total
        utilidad = ingreso_total - costo_total
        rentabilidad = (utilidad / ingreso_total * 100) if ingreso_total > 0 else 0

        st.subheader("📊 Resultado General")
        st.success(f"Utilidad total: ${utilidad:,.2f}")
        st.info(f"Rentabilidad total: {rentabilidad:.2f}%")

else:
    st.warning("No hay rutas guardadas todavía para simular.")
