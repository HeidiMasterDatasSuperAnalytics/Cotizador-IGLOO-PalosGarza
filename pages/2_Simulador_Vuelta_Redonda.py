import streamlit as st
import pandas as pd
import os

st.title("Simulador de Vuelta Redonda")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

def load_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

def calcular_costos(ruta, datos):
    tipo = ruta["Tipo"]
    km = ruta["KM"]
    horas_termo = ruta.get("Horas_Termo", 0)
    diesel = float(datos.get("Costo Diesel", 24))
    rendimiento_camion = float(datos.get("Rendimiento Camion", 2.5))

    # Costo Diesel Camión
    costo_diesel_camion = (km / rendimiento_camion) * diesel if rendimiento_camion > 0 else 0

    # Costo Diesel Termo
    costo_diesel_termo = horas_termo * diesel

    # Sueldo operador
    if tipo == "IMPO":
        sueldo = km * float(datos.get("Pago x km IMPO", 2.1))
    elif tipo == "EXPO":
        sueldo = km * float(datos.get("Pago x km EXPO", 2.5))
    else:
        sueldo = float(datos.get("Pago fijo VACIO", 200))

    # Bono ISR IMSS (solo para IMPO y EXPO)
    if tipo in ["IMPO", "EXPO"]:
        bono_isr_imss = float(datos.get("Bono ISR IMSS", 0))
    else:
        bono_isr_imss = 0

    # Costos adicionales
    casetas = ruta.get("Casetas", 0)
    extras = sum([
        ruta.get("Lavado_Termo", 0),
        ruta.get("Movimiento_Local", 0),
        ruta.get("Puntualidad", 0),
        ruta.get("Pension", 0),
        ruta.get("Estancia", 0),
        ruta.get("Fianza_Termo", 0),
        ruta.get("Renta_Termo", 0)
    ])

    cruce = ruta.get("Cruce_Total", 0)

    costo_total = costo_diesel_camion + costo_diesel_termo + sueldo + bono_isr_imss + casetas + extras + cruce

    return costo_diesel_camion, costo_diesel_termo, sueldo, bono_isr_imss, casetas, extras, cruce, costo_total

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

        km_total = 0
        ingreso_total = 0
        diesel_camion_total = 0
        diesel_termo_total = 0
        sueldo_total = 0
        bono_total = 0
        casetas_total = 0
        extras_total = 0
        cruce_total = 0
        costo_total_general = 0

        st.subheader("🧾 Detalle por Ruta")

        for ruta in rutas:
            costo_diesel_camion, costo_diesel_termo, sueldo, bono_isr_imss, casetas, extras, cruce, total_ruta = calcular_costos(ruta, datos)
            km_total += ruta["KM"]
            ingreso_total += ruta["Ingreso_Total"]
            diesel_camion_total += costo_diesel_camion
            diesel_termo_total += costo_diesel_termo
            sueldo_total += sueldo
            bono_total += bono_isr_imss
            casetas_total += casetas
            extras_total += extras
            cruce_total += cruce
            costo_total_general += total_ruta

            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Origen']} → {ruta['Destino']}**
            - Moneda: {ruta.get('Moneda', 'MXN')}
            - Ingreso Original: ${ruta.get('Ingreso_Original', 0):,.2f}
            - Ingreso Convertido: ${ruta['Ingreso_Total']:,.2f}
            - Diesel Camión: ${costo_diesel_camion:,.2f}
            - Diesel Termo: ${costo_diesel_termo:,.2f}
            - Sueldo operador: ${sueldo:,.2f}
            - Bono ISR/IMSS: ${bono_isr_imss:,.2f}
            - Casetas: ${casetas:,.2f}
            - Extras: ${extras:,.2f}
            - Cruce: ${cruce:,.2f}
            - **Costo Total Ruta:** ${total_ruta:,.2f}
            """)

        utilidad_bruta = ingreso_total - costo_total_general
        estimado_costo_indirecto = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - estimado_costo_indirecto
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.subheader("📊 Resultado General")
        st.success(f"Ingreso Total Vuelta Redonda: ${ingreso_total:,.2f}")
        st.info(f"Costo Total Vuelta Redonda: ${costo_total_general:,.2f}")
        st.success(f"Utilidad Bruta: ${utilidad_bruta:,.2f}")
        st.info(f"Estimado Costo Indirecto (35%): ${estimado_costo_indirecto:,.2f}")
        st.success(f"Utilidad Neta Estimada: ${utilidad_neta:,.2f}")
        st.info(f"% Utilidad Neta: {porcentaje_utilidad_neta:.2f}%")

        st.subheader("📋 Resumen de Gastos")
        st.write(f"**Total Kilómetros Recorridos:** {km_total:,.2f} km")
        st.write(f"**Total Diesel Camión:** ${diesel_camion_total:,.2f}")
        st.write(f"**Total Diesel Termo:** ${diesel_termo_total:,.2f}")
        st.write(f"**Total Sueldos Operador:** ${sueldo_total:,.2f}")
        st.write(f"**Total Bono ISR/IMSS:** ${bono_total:,.2f}")
        st.write(f"**Total Casetas:** ${casetas_total:,.2f}")
        st.write(f"**Total Extras:** ${extras_total:,.2f}")
        st.write(f"**Total Cruces:** ${cruce_total:,.2f}")

else:
    st.warning("No hay rutas guardadas todavía para simular.")

