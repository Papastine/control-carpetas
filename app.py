import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Documental", layout="wide")
st.title("📦 Sistema Estricto de Control de Carpetas")

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

# Consolidar, ordenar y agregar compuerta lógica de contingencia
ss_master = sorted(list(set(ss_ide + ss_techint_belfi))) + ["OTRO (Ingreso Manual)"]

# 2. CONEXIÓN Y EXTRACCIÓN DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla de conexión de lectura: {e}")
    st.stop()

# 3. CONTROLADOR DE INTERFAZ
with st.sidebar:
    st.header("Panel de Control")
    modo = st.radio("Acción requerida:", ["1. Ingresar Nuevo Registro", "2. Editar Registro Existente", "3. Panel de Visualización"])
    if st.button("🔄 Forzar Sincronización Nube"):
        st.rerun()

# ==========================================
# MÓDULO 1: INGRESO NUEVO
# ==========================================
if modo == "1. Ingresar Nuevo Registro":
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Ingreso de Trazabilidad Documental")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema_sel = st.selectbox("ID Subsistema (Matriz Oficial)", ss_master)
            subsistema_manual = st.text_input("Ingreso Manual (Solo si elegiste 'OTRO')")
            tipo = st.selectbox("Categoría de Carpeta", ["CRP", "PRECOM"])
            tomo = st.text_input("Tomo N° / Rango (ej: 1 al 4, 5, 6-7)")
            
        with col2:
            subcontrato = st.selectbox("Empresa Subcontrato (Emisor)", ["TECHINT", "IDE", "BELFI", "Syncore"])
            responsable = st.text_input("Responsable (Receptor/Revisor)")
            estado = st.selectbox("Estado Operativo", ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"])
            
        with col3:
            comentario = st.text_area("Registro de Modificaciones / Faltantes")
            
        submit = st.form_submit_button("Registrar en Base de Datos")

    if submit:
        # Resolución de la compuerta lógica del Subsistema
        subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (Ingreso Manual)" else subsistema_sel
        
        if not subsistema_final or not responsable or not tomo:
            st.error("⚠️ Error Crítico: Los campos Subsistema, Tomo(s) y Responsable son obligatorios.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema_final,
                "Tipo": tipo,
                "Tomo": tomo.strip(),
                "Subcontrato": subcontrato,
                "Responsable": responsable.strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": comentario.strip()
            }])
            
            df_base = data.dropna(how="all") if data is not None else pd.DataFrame()
            df_actualizado = pd.concat([df_base, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)
            st.success("✅ Protocolo registrado con éxito.")
            st.balloons()

# ==========================================
# MÓDULO 2: EDICIÓN EXISTENTE
# ==========================================
elif modo == "2. Editar Registro Existente":
    st.subheader("Auditoría y Corrección de Registros")
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.warning("La base de datos está vacía. No hay variables para auditar.")
    else:
        # Crear un selector legible para ubicar el registro exacto
        opciones_idx = df_limpio.index.tolist()
        def formato_selector(i):
            return f"[{df_limpio.loc[i, 'Estado']}] {df_limpio.loc[i, 'Subsistema']} | {df_limpio.loc[i, 'Tipo']} | Tomo: {df_limpio.loc[i, 'Tomo']}"
        
        idx_editar = st.selectbox("Selecciona el registro específico que requiere modificación:", opciones_idx, format_func=formato_selector)
        
        # Extraer variables actuales para pre-llenar el formulario
        fila_actual = df_limpio.loc[idx_editar]
        
        # Determinar índice del selectbox para el subsistema actual
        try:
            ss_index_actual = ss_master.index(fila_actual["Subsistema"])
        except ValueError:
            ss_index_actual = len(ss_master) - 1 # Cae en "OTRO"

        with st.form("edit_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                edit_sub_sel = st.selectbox("ID Subsistema", ss_master, index=ss_index_actual)
                edit_sub_man = st.text_input("Ingreso Manual", value=fila_actual["Subsistema"] if ss_index_actual == len(ss_master)-1 else "")
                
                tipo_options = ["CRP", "PRECOM"]
                edit_tipo = st.selectbox("Categoría", tipo_options, index=tipo_options.index(fila_actual["Tipo"]) if fila_actual["Tipo"] in tipo_options else 0)
                edit_tomo = st.text_input("Tomo N° / Rango", value=str(fila_actual["Tomo"]))
                
            with col2:
                subc_options = ["TECHINT", "IDE", "BELFI", "Syncore"]
                edit_subc = st.selectbox("Subcontrato", subc_options, index=subc_options.index(fila_actual["Subcontrato"]) if fila_actual["Subcontrato"] in subc_options else 0)
                edit_resp = st.text_input("Responsable", value=str(fila_actual["Responsable"]))
                
                estado_options = ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"]
                edit_est = st.selectbox("Estado Operativo", estado_options, index=estado_options.index(fila_actual["Estado"]) if fila_actual["Estado"] in estado_options else 0)
                
            with col3:
                edit_coment = st.text_area("Comentarios", value=str(fila_actual["Comentarios"] if pd.notna(fila_actual["Comentarios"]) else ""))
                
            submit_edit = st.form_submit_button("Sobrescribir Registro")
            
        if submit_edit:
            sub_final_edit = edit_sub_man.strip().upper() if edit_sub_sel == "OTRO (Ingreso Manual)" else edit_sub_sel
            
            # Clonar el dataframe para inyectar la modificación en la fila exacta
            df_actualizado = df_limpio.copy()
            df_actualizado.loc[idx_editar, "Subsistema"] = sub_final_edit
            df_actualizado.loc[idx_editar, "Tipo"] = edit_tipo
            df_actualizado.loc[idx_editar, "Tomo"] = edit_tomo.strip()
            df_actualizado.loc[idx_editar, "Subcontrato"] = edit_subc
            df_actualizado.loc[idx_editar, "Responsable"] = edit_resp.strip().upper()
            df_actualizado.loc[idx_editar, "Estado"] = edit_est
            df_actualizado.loc[idx_editar, "Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M") + " (Editado)"
            df_actualizado.loc[idx_editar, "Comentarios"] = edit_coment.strip()
            
            conn.update(data=df_actualizado)
            st.success("✅ Modificación estructural aplicada a la base de datos.")
            st.rerun()

# ==========================================
# MÓDULO 3: VISUALIZACIÓN Y AUDITORÍA
# ==========================================
else:
    st.subheader("Auditoría de Subsistemas Pendientes y OK")
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.warning("Base de datos limpia o sin formato correcto detectado.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Movimientos", len(df_limpio))
        c2.metric("Lotes OK", len(df_limpio[df_limpio["Estado"] == "OK"]))
        c3.metric("Lotes en QA", len(df_limpio[df_limpio["Estado"] == "En Revisión QA"]))
        c4.metric("Lotes sin Escanear", len(df_limpio[df_limpio["Estado"] == "Falta Escanear"]))

        st.markdown("---")
        filtro_sub = st.text_input("🔍 Búsqueda rigurosa por TAG:")
        if filtro_sub:
            df_vis = df_limpio[df_limpio["Subsistema"].astype(str).str.contains(filtro_sub.upper(), na=False)]
        else:
            df_vis = df_limpio

        st.dataframe(df_vis, use_container_width=True, hide_index=True)
