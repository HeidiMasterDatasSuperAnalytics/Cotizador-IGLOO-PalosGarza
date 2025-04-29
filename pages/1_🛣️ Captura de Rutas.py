import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Ruta de archivos
RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

# Valores por defecto
valores_por_defecto = {
    "Rendimiento Camion": 2.5,
    "Costo Diesel": 24.0,
    "Rendimiento Termo": 3.0,
    "Bono ISR IMSS": 462.66,
    "Pago x km IMPO": 2.10,
    "Pago x km EXPO": 2.50,
    "Pago fijo VACIO": 200.00,
    "Tipo de cambio USD": 17.5,
    "Tipo de cambio MXN": 1.0
}

def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    else:
        return valores_por_defecto.copy()

def guardar_datos_generales(valores):
    df = pd.DataFrame(valores.items(), columns=["Parametro", "Valor"])
    df.to_csv(RUTA_DATOS, index=False)

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

valores = cargar_datos_generales()

st.title("🚛 Captura de Rutas + Datos Generales")

with st.expander("⚙️ Configurar Datos Generales"):
    for key in valores_por_defecto:
        valores[key] = st.number_input(key, value=float(valores.get(key, valores_por_defecto[key])), step=0.1)
    if st.button("Guardar Datos Generales"):
        guardar_datos_generales(valores)
        st.success("✅ Datos Generales guardados correctamente.")

st.markdown("---")

if os.path.exists(RUTA_RUTAS):
    df_rutas = pd.read_csv(RUTA_RUTAS)
else:
    df_rutas = pd.DataFrame()

st.subheader("🛣️ Nueva Ruta")
with st.form("captura_ruta"):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", value=datetime.today())
        tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
        cliente = st.text_input("Nombre Cliente")
        origen = st.text_input("Origen")
        destino = st.text_input("Destino")
        km = st.number_input("Kilómetros", min_value=0.0)
        moneda_ingreso = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"])
        ingreso_flete = st.number_input(f"Ingreso Flete en {moneda_ingreso}", min_value=0.0, key="ingreso_flete_input")
        moneda_cruce = st.selectbox("Moneda Ingreso Cruce", ["MXN", "USD"])
        ingreso_cruce = st.number_input(f"Ingreso Cruce en {moneda_cruce}", min_value=0.0, key="ingreso_cruce_input")
    with col2:
        horas_termo = st.number_input("Horas Termo", min_value=0.0)
        lavado_termo = st.number_input("Lavado Termo", min_value=0.0)
        movimiento_local = st.number_input("Movimiento Local", min_value=0.0)
        puntualidad = st.number_input("Puntualidad", min_value=0.0)
        pension = st.number_input("Pensión", min_value=0.0)
        estancia = st.number_input("Estancia", min_value=0.0)
        fianza_termo = st.number_input("Fianza Termo", min_value=0.0)
        renta_termo = st.number_input("Renta Termo", min_value=0.0)
        casetas = st.number_input("Casetas", min_value=0.0)

    submitted = st.form_submit_button("💾 Guardar Ruta")

    if submitted:
        tipo_cambio_flete = valores["Tipo de cambio USD"] if moneda_ingreso == "USD" else valores["Tipo de cambio MXN"]
        tipo_cambio_cruce = valores["Tipo de cambio USD"] if moneda_cruce == "USD" else valores["Tipo de cambio MXN"]

        ingreso_flete_convertido = ingreso_flete * tipo_cambio_flete
        ingreso_cruce_convertido = ingreso_cruce * tipo_cambio_cruce
        ingreso_total = ingreso_flete_convertido + ingreso_cruce_convertido

        diesel = valores["Costo Diesel"]
        rendimiento_camion = valores["Rendimiento Camion"]
        rendimiento_termo = valores["Rendimiento Termo"]

        costo_diesel_camion = (km / rendimiento_camion) * diesel if rendimiento_camion > 0 else 0
        costo_diesel_termo = horas_termo * rendimiento_termo * diesel if rendimiento_termo > 0 else 0

        if tipo == "IMPO":
            pago_km = valores["Pago x km IMPO"]
            sueldo = km * pago_km
            bono = valores["Bono ISR IMSS"]
        elif tipo == "EXPO":
            pago_km = valores["Pago x km EXPO"]
            sueldo = km * pago_km
            bono = valores["Bono ISR IMSS"]
        else:
            pago_km = 0.0
            sueldo = valores["Pago fijo VACIO"]
            bono = 0.0

        extras = sum([
            safe_number(lavado_termo), safe_number(movimiento_local), safe_number(puntualidad),
            safe_number(pension), safe_number(estancia), safe_number(fianza_termo), safe_number(renta_termo)
        ])

        costo_total = costo_diesel_camion + costo_diesel_termo + sueldo + bono + casetas + extras + ingreso_cruce_convertido

        nueva_ruta = {
            "Fecha": fecha, "Tipo": tipo, "Cliente": cliente, "Origen": origen, "Destino": destino, "KM": km,
            "Moneda": moneda_ingreso, "Ingreso_Original": ingreso_flete, "Tipo de cambio": tipo_cambio_flete,
            "Ingreso Flete": ingreso_flete_convertido, "Moneda_Cruce": moneda_cruce, "Cruce_Original": ingreso_cruce,
            "Tipo cambio Cruce": tipo_cambio_cruce, "Ingreso Cruce": ingreso_cruce_convertido,
            "Ingreso Total": ingreso_total,
            "Pago por KM": pago_km, "Sueldo_Operador": sueldo, "Bono": bono,
            "Casetas": casetas, "Horas_Termo": horas_termo, "Lavado_Termo": lavado_termo,
            "Movimiento_Local": movimiento_local, "Puntualidad": puntualidad, "Pension": pension,
            "Estancia": estancia, "Fianza_Termo": fianza_termo, "Renta_Termo": renta_termo,
            "Costo_Diesel_Camion": costo_diesel_camion, "Costo_Diesel_Termo": costo_diesel_termo,
            "Costo_Extras": extras, "Costo_Total_Ruta": costo_total
        }

        df_rutas = pd.concat([df_rutas, pd.DataFrame([nueva_ruta])], ignore_index=True)
        df_rutas.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Ruta guardada exitosamente.")
        st.experimental_rerun()
