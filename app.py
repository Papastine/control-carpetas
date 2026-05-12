import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from st_keyup import st_keyup

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Control TOP QA", layout="wide")

st.title("Sistema de Control de Carpetas TOP")
st.markdown("Plataforma de Auditoría y Trazabilidad Documental")
st.divider()

# -----------------------------------------------------------------------------
# MATRIZ DE SUBSISTEMAS ESTANDARIZADA
# -----------------------------------------------------------------------------
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

ss_master = sorted(list(set(ss_ide + ss_techint_belfi))) + ["OTRO (INGRESO MANUAL)"]
estados_oficiales = ["OK", "Falta firma", "En revision", "Faltan PRT", "Falta escanear"]
empresas_oficiales = ["TECHINT", "IDE", "BELFI", "Syncore"]
tipos_oficiales = ["CRP", "PRECOM"]

# -----------------------------------------------------------------------------
# CONEXIÓN A BASE DE DATOS
# -----------------------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla de conexión a la base de datos: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# NAVEGACIÓN LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Menú Principal")
    modo = st.radio("Módulos:", ["1. Ingreso Documental", "2. Auditoría y Edición"])
    st.divider()
    if st.button("Sincronizar Datos", use_container_width=True):
        st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 1: INGRESO DOCUMENTAL
# -----------------------------------------------------------------------------
if modo == "1. Ingreso Documental":
    
    st.subheader("Registro de Lote")
    st.caption("Complete los campos obligatorios para el ingreso. El sistema bloquea duplicados exactos automáticamente.")
    
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            subsistema_sel = st.selectbox("ID Subsistema", ss_master)
            subsistema_manual = st.text_input("Ingreso Manual (Solo si seleccionó 'OTRO')")
            tipo = st.selectbox("Categoría Documental", tipos_oficiales)
            tomo = st.text_input("Tomo N° / Rango")
            
        with col2:
            subcontrato = st.selectbox("Empresa Emisora", empresas_oficiales)
            responsable = st.text_input("Responsable QA")
            estado = st.selectbox("Estado Operativo", estados_oficiales)
            
        comentario = st.text_area("Observaciones", height=100)
            
        submit = st.form_submit_button("Guardar Registro", type="primary")

    if submit:
        subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (INGRESO MANUAL)" else subsistema_sel
        
        if not subsistema_final or not responsable or not tomo:
            st.error("Campos obligatorios faltantes. Verifique los datos.")
        else:
            df_base = data.dropna(subset=["Subsistema"]).fillna("").astype(str) if data is not None else pd.DataFrame()
            
            # CONTROL DE DUPLICADOS ESTRICTO
            if not df_base.empty:
                duplicado = df_base[
                    (df_base["Subsistema"] == subsistema_final) & 
                    (df_base["Tipo"] == tipo) & 
                    (df_base["Tomo"] == str(tomo).strip())
                ]
            else:
                duplicado = pd.DataFrame()

            if not duplicado.empty:
                st.error("Bloqueo de seguridad: El lote ingresado (Subsistema + Tipo + Tomo) ya se encuentra en la base de datos.")
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
                df_actualizado = pd.concat([data.dropna(how="all"), nuevo_registro], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success("Lote registrado correctamente.")
                st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 2: AUDITORÍA Y EDICIÓN
# -----------------------------------------------------------------------------
else:
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.info("La base de datos no contiene registros.")
    else:
        df_limpio = df_limpio.fillna("").astype(str).replace(["nan", "None"], "")
        
        # --- BUSCADOR PRINCIPAL (Tiempo Real) ---
        st.subheader("Búsqueda Inmediata de Subsistema")
        buscador_txt = st_keyup("Escriba el TAG para filtrar la tabla al instante:", key="buscador_ss")
        st.divider()
        
        # --- MÉTRICAS DE CONTROL ---
        total_reg = len(df_limpio)
        total_ok = len(df_limpio[df_limpio["Estado"] == "OK"])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Registros", total_reg)
        c2.metric("Carpetas OK", total_ok)
        c3.metric("En Revisión QA", len(df_limpio[df_limpio["Estado"] == "En revision"]))
        c4.metric("Falta Escanear", len(df_limpio[df_limpio["Estado"] == "Falta escanear"]))
        st.write("")

        # --- FILTROS SECUNDARIOS ---
        with st.expander("Filtros Adicionales (Estado, Empresa, Tipo)"):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                filtro_estado = st.selectbox("Estado", ["TODOS"] + estados_oficiales)
            with f_col2:
                filtro_empresa = st.selectbox("Empresa", ["TODOS"] + empresas_oficiales)
            with f_col3:
                filtro_tipo = st.selectbox("Tipo", ["TODOS"] + tipos_oficiales)

        # ORDENAMIENTO Y APLICACIÓN DE FILTROS
        df_limpio = df_limpio.sort_values(by=["Subsistema", "Tipo", "Tomo"], ascending=[True, True, True]).reset_index(drop=True)
        df_vis = df_limpio.copy()
        
        if buscador_txt:
            df_vis = df_vis[df_vis["Subsistema"].str.contains(buscador_txt.upper(), na=False)]
        if filtro_estado != "TODOS":
            df_vis = df_vis[df_vis["Estado"] == filtro_estado]
        if filtro_empresa != "TODOS":
            df_vis = df_vis[df_vis["Subcontrato"] == filtro_empresa]
        if filtro_tipo != "TODOS":
            df_vis = df_vis[df_vis["Tipo"] == filtro_tipo]

        # --- PANEL DE EDICIÓN ---
        st.subheader("Panel de Datos")
        st.caption("Seleccione la casilla a la izquierda de la fila para resaltarla. Doble clic en una celda para editar.")
        
        if not df_vis.empty:
            df_editado = st.data_editor(
                df_vis,
                use_container_width=True,
                num_rows="fixed",
                hide_index=False, # ESTA VARIABLE PERMITE SELECCIONAR Y RESALTAR LA FILA COMPLETA
                column_config={
                    "Subsistema": st.column_config.SelectboxColumn("Subsistema", options=ss_master, required=True),
                    "Tipo": st.column_config.SelectboxColumn("Tipo", options=tipos_oficiales, required=True),
                    "Tomo": st.column_config.TextColumn("Tomo", required=True),
                    "Subcontrato": st.column_config.SelectboxColumn("Subcontrato", options=empresas_oficiales, required=True),
                    "Responsable": st.column_config.TextColumn("Responsable", required=True),
                    "Estado": st.column_config.SelectboxColumn("Estado", options=estados_oficiales, required=True),
                    "Fecha_Registro": st.column_config.TextColumn("Fecha Modificación", disabled=True),
                    "Comentarios": st.column_config.TextColumn("Comentarios")
                }
            )

            st.write("")
            col_save, col_empty, col_export = st.columns([2, 2, 1])
            
            with col_save:
                if st.button("Guardar Cambios Editados", type="primary", use_container_width=True):
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
                        st.success("Cambios sincronizados en la base de datos.")
                        st.rerun()
                    else:
                        st.info("No se detectaron modificaciones para guardar.")
                        
            with col_export:
                csv_data = df_vis.to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button("Exportar Vista (CSV)", csv_data, f"Reporte_TOP_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
                
        else:
            st.warning("No se encontraron coincidencias para la búsqueda.")
