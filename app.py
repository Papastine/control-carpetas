import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control TOP", layout="wide")
st.title("Sistema de Control de Carpetas TOP")

# 1. MATRIZ DE SUBSISTEMAS ESTANDARIZADA
ss_ide = [
    "7114-A01-000", "7114-A01-001", "7114-A01-002", "7114-A01-003", "7114-A01-005", "7114-A01-006", "7114-A01-007", "7114-A01-008", 
    "7210-B01-001", "7210-B01-002", "7210-B01-003", "7210-B01-004", "7210-B01-005", "7210-B01-006", "7210-B01-007", "7210-B01-008", 
    "7210-B01-009", "7210-B01-010", "7210-B01-011", "7210-B01-012", "7212-B01-013", "7212-B01-014", "7212-B01-015", "7212-B01-018", 
    "7212-B01-019", "7212-B01-020", "7212-B01-021", "7212-B01-022", "7212-B01-023", "7212-B01-024", "7213-B01-025", "7213-B01-026", 
    "7213-B01-027", "7213-B01-028", "7213-B01-029", "7213-B01-030", "7213-B01-031", "7213-B01-032", "7213-B01-033", "7213-B01-034", 
    "7213-B01-035", "7213-B01-036", "7213-B01-038", "7213-B01-039", "7213-B01-040", "7213-B01-041", "7213-B01-042", "7221-C01-001", 
    "7221-C01-002", "7221-C01-003", "7221-C01-004", "7221-C01-005", "7221-C01-006", "7221-C01-007", "7221-D01-006", "7221-D01-008", 
    "7221-D02-001", "7221-D02-002", "7221-D02-003", "7221-D02-004", "7221-D02-006", "7221-D02-007", "7221-D02-008", "7221-D02-009", 
    "7221-D02-010", "7221-D02-011", "7230-F01-001", "7230-F01-002", "7240-G01-001", "7240-G01-002", "7240-G02-001", "7240-G03-001", 
    "7240-G03-002", "7240-G04-001", "7240-G04-002", "7240-G04-003", "7240-G04-004", "7240-G04-005", "7240-G04-010", "7240-G04-011", 
    "7240-G04-013", "7240-G04-014", "7240-G05-001", "7240-G05-003", "7240-G05-004", "7240-G05-005", "7240-G05-006", "7240-G05-007", 
    "7240-G05-008", "7240-G05-010", "7240-G05-011", "7240-G05-014", "7240-G05-015", "7240-G05-018", "7240-G06-001", "7250-I01-001", 
    "7250-I01-002", "7250-I01-003", "7260-W01-001", "7261-B01-037", "7264-Z01-001", "7270-E01-001", "7270-E02-001", "7270-E02-002", 
    "7270-E02-003", "7270-E02-004", "7270-E02-005", "7270-E02-006", "7270-E02-007", "7270-E02-008", "7270-E02-009", "7270-E02-010", 
    "7270-E02-011", "7270-E02-012", "7270-S01-001", "7270-S01-002", "7270-S01-003", "7270-S01-004", "7270-S01-005", "7270-S01-006", 
    "7270-S01-007", "7270-S01-008", "7270-S01-009", "7270-S01-010", "7270-S01-011", "7270-S01-012", "7270-S01-013", "7200-FTS-09", 
    "7200-FTS-12", "7200-FTS-02", "7200-FTS-08", "7200-FTS-01", "7200-FTS-03", "7200-FTS-04", "7200-FTS-05", "7200-FTS-06", 
    "7200-FTS-07", "7200-FTS-10", "7200-FTS-11", "7200-FTS-13", "7200-FTS-14", "7200-FTS-15", "7200-FTS-16", "7200-FTS-17", 
    "7200-FTS-20", "7200-FTS-21", "7200-FTS-22", "7200-FTS-18", "7200-FTS-19"
]

ss_techint_belfi = [
    "7111-F01-001", "7113-F01-001-A1", "7113-F01-001-B2", "7114-F01-001", "7121-F01-001", "7122-F01-001", "7123-F01-001", 
    "7130-F01-001", "7130-F01-002"
]

ss_master = sorted(list(set(ss_ide + ss_techint_belfi))) + ["OTRO (Ingreso Manual)"]
estados_oficiales = ["OK", "Falta firma", "En revision", "Faltan PRT", "Falta escanear"]

# 2. CONEXIÓN Y EXTRACCIÓN DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# 3. CONTROLADOR DE INTERFAZ
with st.sidebar:
    st.header("Panel de Operaciones")
    modo = st.radio("Fase de trabajo:", ["1. Ingreso Documental", "2. Panel de Auditoría y Edición"])
    st.markdown("---")
    if st.button("🔄 Sincronizar Nube"):
        st.rerun()

# ==========================================
# MÓDULO 1: INGRESO NUEVO
# ==========================================
if modo == "1. Ingreso Documental":
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Ingreso de Trazabilidad")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema_sel = st.selectbox("ID Subsistema", ss_master)
            subsistema_manual = st.text_input("Ingreso Manual (Solo si es 'OTRO')")
            tipo = st.selectbox("Categoría", ["CRP", "PRECOM"])
            tomo = st.text_input("Tomo N° / Rango")
            
        with col2:
            subcontrato = st.selectbox("Emisor", ["TECHINT", "IDE", "BELFI", "Syncore"])
            responsable = st.text_input("Responsable")
            estado = st.selectbox("Estado", estados_oficiales)
            
        with col3:
            comentario = st.text_area("Comentarios")
            
        submit = st.form_submit_button("Registrar")

    if submit:
        subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (Ingreso Manual)" else subsistema_sel
        if not subsistema_final or not responsable or not tomo:
            st.error("Campos obligatorios faltantes.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema_final,
                "Tipo": tipo,
                "Tomo": str(tomo).strip(),
                "Subcontrato": subcontrato,
                "Responsable": str(responsable).strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": str(comentario).strip()
            }])
            df_base = data.dropna(how="all") if data is not None else pd.DataFrame()
            df_actualizado = pd.concat([df_base, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)
            st.success("Registrado.")
            st.rerun()

# ==========================================
# MÓDULO 2: PANEL MAESTRO (Visualización y Edición)
# ==========================================
else:
    st.subheader("Auditoría y Edición")
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.warning("Sin datos.")
    else:
        df_limpio = df_limpio.fillna("").astype(str).replace(["nan", "None"], "")
        
        c1, c2, c3, c_down = st.columns([1,1,1,1.5])
        c1.metric("Total", len(df_limpio))
        c2.metric("OK", len(df_limpio[df_limpio["Estado"] == "OK"]))
        c3.metric("En revisión", len(df_limpio[df_limpio["Estado"] == "En revision"]))
        
        with c_down:
            csv_data = df_limpio.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button("📥 Descargar Excel", csv_data, f"Control_TOP_{datetime.now().strftime('%d-%m-%Y')}.csv", "text/csv", use_container_width=True)

        st.markdown("---")
        
        # FILTRO REACTIVO OPTIMIZADO PARA MÓVIL (No requiere Enter)
        # Extraemos solo los SS que existen actualmente en la base de datos para no saturar el filtro
        ss_registrados = sorted(df_limpio["Subsistema"].unique().tolist())
        opciones_filtro = ["📋 MOSTRAR TODOS LOS REGISTROS"] + ss_registrados
        
        buscador = st.selectbox("🔍 Búsqueda Rápida: Toca aquí y escribe el SS para filtrar al instante", opciones_filtro)
        
        if buscador != "📋 MOSTRAR TODOS LOS REGISTROS":
            df_vis = df_limpio[df_limpio["Subsistema"] == buscador].copy()
        else:
            df_vis = df_limpio.copy()

        if not df_vis.empty:
            df_editado = st.data_editor(
                df_vis,
                use_container_width=True,
                num_rows="fixed",
                hide_index=True,
                column_config={
                    "Subsistema": st.column_config.SelectboxColumn("Subsistema", options=ss_master, required=True),
                    "Tipo": st.column_config.SelectboxColumn("Tipo", options=["CRP", "PRECOM"], required=True),
                    "Tomo": st.column_config.TextColumn("Tomo", required=True),
                    "Subcontrato": st.column_config.SelectboxColumn("Emisor", options=["TECHINT", "IDE", "BELFI", "Syncore"], required=True),
                    "Responsable": st.column_config.TextColumn("Responsable", required=True),
                    "Estado": st.column_config.SelectboxColumn("Estado", options=estados_oficiales, required=True),
                    "Fecha_Registro": st.column_config.TextColumn("Fecha", disabled=True),
                    "Comentarios": st.column_config.TextColumn("Comentarios")
                }
            )

            if st.button("💾 Guardar Cambios", type="primary"):
                df_editado = df_editado.fillna("").astype(str).replace(["nan", "None"], "")
                hubo_cambios = False
                
                for idx in df_editado.index:
                    if idx in df_limpio.index:
                        if not df_limpio.loc[idx].equals(df_editado.loc[idx]):
                            df_limpio.loc[idx] = df_editado.loc[idx]
                            df_limpio.loc[idx, "Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M") + " (Editado)"
                            hubo_cambios = True

                if hubo_cambios:
                    conn.update(data=df_limpio)
                    st.success("Sincronizado.")
                    st.rerun()
