import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Documental", layout="wide")
st.title("📦 Sistema Estricto de Control de Carpetas")

# Conexión estandarizada a la base de datos
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    data = conn.read()
except Exception as e:
    st.error(f"Falla de conexión de lectura a la base de datos: {e}")
    st.stop()

with st.sidebar:
    st.header("Panel de Control")
    modo = st.radio("Acción requerida:", ["Panel de Visualización", "Ingresar/Auditar Carpeta"])

if modo == "Ingresar/Auditar Carpeta":
    with st.form("registro_form"):
        st.subheader("Ingreso de Trazabilidad Documental")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema = st.text_input("ID Subsistema")
            tipo = st.selectbox("Categoría de Carpeta", ["CRP", "PRECOM"])
            # Campo de texto para soportar rangos dinámicos de tomos
            tomo = st.text_input("Tomo N° / Rango (ej: 1 al 4, 5, 6-7)")
            
        with col2:
            subcontrato = st.selectbox("Empresa Subcontrato (Emisor)", ["TECHINT", "IDE", "Syncore"])
            responsable = st.text_input("Responsable (Receptor/Revisor)")
            estado = st.selectbox("Estado Operativo", ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"])
            
        with col3:
            comentario = st.text_area("Registro de Modificaciones / Faltantes")
            
        submit = st.form_submit_button("Registrar en Base de Datos")

    if submit:
        # Validación crítica de campos obligatorios
        if not subsistema or not responsable or not tomo:
            st.error("⚠️ Error Crítico: Los campos Subsistema, Tomo(s) y Responsable son obligatorios para la trazabilidad.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema.strip().upper(),
                "Tipo": tipo,
                "Tomo": tomo.strip(),
                "Subcontrato": subcontrato,
                "Responsable": responsable.strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": comentario.strip()
            }])
            
            # Se añade el nuevo evento al historial y se sincroniza
            df_actualizado = pd.concat([data, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)
            
            st.success("✅ Protocolo registrado correctamente. Sincronización exitosa.")
            st.rerun()

else:
    st.subheader("Auditoría de Subsistemas Pendientes y OK")
    
    if data is None or data.empty:
        st.warning("Base de datos vacía. No hay variables para analizar.")
    else:
        # Métricas de control estricto
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Movimientos", len(data))
        c2.metric("Lotes OK", len(data[data["Estado"] == "OK"]))
        c3.metric("Lotes en QA", len(data[data["Estado"] == "En Revisión QA"]))
        c4.metric("Lotes sin Escanear", len(data[data["Estado"] == "Falta Escanear"]))

        st.markdown("---")
        st.write("**Matriz de Trazabilidad Histórica**")
        
        # Filtro analítico por TAG
        filtro_sub = st.text_input("Filtrar por ID de Subsistema (Presiona Enter):")
        if filtro_sub:
            df_filtrado = data[data["Subsistema"].str.contains(filtro_sub.upper(), na=False)]
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(data, use_container_width=True, hide_index=True)
