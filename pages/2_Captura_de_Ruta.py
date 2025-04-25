if st.button("Guardar Ruta"):
    nueva_ruta = pd.DataFrame([{
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "KM": km,
        "Horas_Termo": horas_termo,
        "Casetas": casetas,
        "Lavado_Termo": lavado_termo,
        "Movimiento_Local": mov_local,
        "Puntualidad": puntualidad,
        "Pension": pension,
        "Estancia": estancia,
        "Fianza_Termo": fianza,
        "Renta_Termo": renta_termo,
        "Moneda": moneda,
        "Ingreso_Original": ingreso_original,
        "Ingreso_Total": ingreso_total,
        "Costo_Diesel": costo_diesel,
        "Costo_Total": costo_total
    }])
    df = pd.concat([df, nueva_ruta], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("✅ La ruta se guardó exitosamente.")
    st.rerun()

