import streamlit as st
import pandas as pd
import sqlite3
import json
import re

# 1. ESTÉTICA DE LUJO: GLASSMORPHISM & SOFT UI
st.set_page_config(page_title="Censo El Paraíso", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Fondo con degradado sofisticado */
    .stApp { 
        background: linear-gradient(135deg, #e9f0ec 0%, #e2e8e9 100%); 
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 35px;
        padding-top: 20px;
    }

    .titulo-censo {
        color: #1b5e20; font-weight: 900; font-size: 2.8rem; margin: 0;
        letter-spacing: -1px;
    }

    /* ETIQUETAS DE CONTEO ELEGANTES */
    .badge-total {
        background-color: #1b5e20;
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.2);
        text-transform: uppercase;
    }

    .badge-sector {
        background: rgba(255, 255, 255, 0.7);
        color: #1b5e20;
        border: 1px solid rgba(27, 94, 32, 0.3);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-left: 10px;
    }
    
    /* TARJETAS DE RUBRO: EL SALTO A LA ELEGANCIA */
    div.stButton > button {
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        color: #1b5e20 !important;
        border-radius: 24px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.04) !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        padding: 50px 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-weight: 800 !important;
    }
    
    div.stButton > button:hover {
        background: #ffffff !important;
        transform: translateY(-12px) !important;
        box-shadow: 0 20px 40px rgba(27, 94, 32, 0.08) !important;
        border: 1px solid #1b5e20 !important;
    }

    /* Tamaños ajustados */
    .modo-inicio button { font-size: 85px !important; height: 380px !important; }
    .modo-pestana button { font-size: 26px !important; height: 100px !important; border-bottom: 5px solid #1b5e20 !important; border-radius: 0 !important; padding: 10px !important; }

    /* Dataframe y Filtros */
    [data-testid="stDataFrame"] { border-radius: 20px; background: white; border: 1px solid rgba(0,0,0,0.05); overflow: hidden; }
    .stSelectbox div[data-baseweb="select"] { border-radius: 12px !important; border: 1px solid #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS Y MUNICIPIOS
conn = sqlite3.connect('productores.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS productores (dni TEXT PRIMARY KEY, nombre TEXT, municipio TEXT, rubro TEXT, riego TEXT, aldea TEXT, extra TEXT)''')
conn.commit()

MUNICIPIOS_EP = sorted(["Alauca", "Danlí", "El Paraíso", "Güinope", "Jacaleapa", "Liure", "Morocelí", "Oropolí", "Potrerillos", "San Antonio de Flores", "San Lucas", "San Matías", "Soledad", "Teupasenti", "Texiguat", "Trojes", "Vado Ancho", "Yauyupe", "Yuscarán"])

# FUNCIÓN DE SEGURIDAD GEOGRÁFICA (HONDURAS)
def validar_geoposicion_hn(extra_data):
    for k, v in extra_data.items():
        if any(x in k.upper() for x in ["SIG", "LAT", "LON", "COOR"]):
            nums = re.findall(r"[-+]?\d+\.\d+", str(v))
            if len(nums) >= 2:
                try:
                    n1, n2 = float(nums[0]), float(nums[1])
                    # Verificación de cuadrante HN (Lat: 13-16.5 | Lon: -89.5 a -83)
                    # Corregimos longitud si falta el signo menos
                    def check(lt, ln):
                        ln_corr = ln if ln < 0 else -ln
                        if 12.8 <= lt <= 17.0 and -89.5 <= ln_corr <= -82.8: return lt, ln_corr
                        return None
                    
                    res = check(n1, n2) or check(n2, n1)
                    if res: return res
                except: continue
    return None

# 3. FICHA TÉCNICA (EXPEDIENTE ELEGANTE)
@st.dialog("EXPEDIENTE TÉCNICO", width="large")
def mostrar_ficha(dni):
    p = pd.read_sql("SELECT * FROM productores WHERE dni = ?", conn, params=(dni,)).iloc[0]
    st.markdown(f"<h2 style='color:#1b5e20; border-bottom: 3px solid #1b5e20; padding-bottom:10px;'>{p['nombre']}</h2>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"**IDENTIDAD**\n\n{p['dni']}")
    c2.markdown(f"**MUNICIPIO**\n\n{p['municipio']}")
    c3.markdown(f"**ALDEA**\n\n{p['aldea']}")
    c4.markdown(f"**PROYECTO**\n\n{p['riego']}")
    
    st.divider()
    try:
        ex = json.loads(p['extra'])
        if ex:
            pos_valida = validar_geoposicion_hn(ex)
            if pos_valida:
                col_i, col_m = st.columns([1.8, 1])
                with col_i:
                    st.markdown("**INFORMACIÓN COMPLEMENTARIA:**")
                    sub_c = st.columns(2)
                    for i, (k, v) in enumerate(ex.items()): sub_c[i % 2].write(f"**{k}:** {v}")
                with col_m:
                    st.markdown("**LOCALIZACIÓN:**")
                    url_map = f"https://www.google.com/maps?q={pos_valida[0]},{pos_valida[1]}"
                    st.link_button("📍 UBICACIÓN SATELITAL", url_map, use_container_width=True)
            else:
                st.markdown("**INFORMACIÓN COMPLEMENTARIA:**")
                sub_c = st.columns(3)
                for i, (k, v) in enumerate(ex.items()): sub_c[i % 3].write(f"**{k}:** {v}")
    except: pass
    
    if st.button("Finalizar Consulta"):
        for key in list(st.session_state.keys()):
            if key.startswith("tab_"): del st.session_state[key]
        st.rerun()

# 4. CARGA DE DATOS (SIDEBAR)
with st.sidebar:
    st.header("📥 Importar Listados")
    archivo = st.file_uploader("Excel o CSV", type=["xlsx", "csv"])
    m_imp = st.selectbox("Municipio", MUNICIPIOS_EP)
    a_imp = st.text_input("Aldea")
    r_imp = st.selectbox("Rubro", ["Café", "Cacao", "Granos Básicos", "Ganadería", "Hortalizas y Legumbres"])
    v_riego = "General"
    if r_imp == "Granos Básicos" and st.checkbox("Proyecto de Riego"): v_riego = "Beneficiario Proyecto de Riego"

    if archivo and a_imp and st.button("🚀 INICIAR CARGA"):
        try:
            df_raw = pd.read_excel(archivo, header=None) if archivo.name.endswith('xlsx') else pd.read_csv(archivo, header=None)
            fila_head = next(i for i, r in df_raw.iterrows() if any(x in str(v).upper() for x in ['DNI', 'IDENTIDAD', 'NOMBRE'] for v in r))
            df = pd.read_excel(archivo, skiprows=fila_head) if archivo.name.endswith('xlsx') else pd.read_csv(archivo, skiprows=fila_head)
            df.columns = [str(col).strip() for col in df.columns]
            c_dni = next(c for c in df.columns if any(x in c.upper() for x in ['DNI', 'IDENTIDAD']))
            c_nom = next(c for c in df.columns if any(x in c.upper() for x in ['NOMBRE', 'PRODUCTOR']))
            cols_ex = [c for c in df.columns if c not in [c_dni, c_nom]]
            for _, row in df.iterrows():
                if pd.notna(row[c_dni]):
                    d_ex = {k: str(row[k]) for k in cols_ex if pd.notna(row[k])}
                    c.execute("INSERT OR REPLACE INTO productores VALUES (?,?,?,?,?,?,?)", (str(row[c_dni]), str(row[c_nom]), m_imp, r_imp, v_riego, a_imp, json.dumps(d_ex, ensure_ascii=False)))
            conn.commit()
            st.success("✅ Censo actualizado.")
        except: st.error("Error en archivo.")

# 5. PANEL PRINCIPAL
total_global = pd.read_sql("SELECT COUNT(*) as total FROM productores", conn).iloc[0]['total']

st.markdown(f"""
    <div class='header-container'>
        <h1 class='titulo-censo'>Censo Departamental - El Paraíso</h1>
        <span class='badge-total'>{total_global} productores registrados</span>
    </div>
    """, unsafe_allow_html=True)

if 'r_sel' not in st.session_state: st.session_state.r_sel = None

def set_rubro(name):
    for key in list(st.session_state.keys()):
        if key.startswith("tab_"): del st.session_state[key]
    st.session_state.r_sel = name

# Render de Rubros (Glassmorphism)
clase_v = "modo-pestana" if st.session_state.r_sel else "modo-inicio"
st.markdown(f'<div class="{clase_v}">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
if c1.button("☕\nCAFÉ"): set_rubro("Café")
if c2.button("🍫\nCACAO"): set_rubro("Cacao")
if c3.button("🚜\nGRANOS BÁSICOS"): set_rubro("Granos Básicos")
if c4.button("🥩\nGANADERÍA"): set_rubro("Ganadería")
if c5.button("🥬\nHORTALIZAS"): set_rubro("Hortalizas y Legumbres")
st.markdown('</div>', unsafe_allow_html=True)

# 6. BÚSQUEDA Y CONSULTAS
if not st.session_state.r_sel:
    st.divider()
    bg = st.text_input("🔎 BÚSQUEDA INTEGRAL (Nombre, DNI, Municipio o Aldea):", placeholder="Escriba aquí para buscar en todo el departamento...")
    if bg:
        q_gen = "SELECT dni as IDENTIDAD, nombre as NOMBRE, municipio as MUNICIPIO, aldea as ALDEA, rubro as RUBRO FROM productores WHERE NOMBRE LIKE ? OR IDENTIDAD LIKE ? OR MUNICIPIO LIKE ? OR ALDEA LIKE ?"
        df_g = pd.read_sql(q_gen, conn, params=(f'%{bg}%', f'%{bg}%', f'%{bg}%', f'%{bg}%'))
        if not df_g.empty:
            sel_g = st.dataframe(df_g, use_container_width=True, on_select="rerun", selection_mode="single-row", hide_index=True, key="tab_main")
            if len(sel_g.selection.rows) > 0: mostrar_ficha(df_g.iloc[sel_g.selection.rows[0]]['IDENTIDAD'])
else:
    # SECCIÓN DE RUBRO SELECCIONADO
    total_rubro = pd.read_sql("SELECT COUNT(*) as total FROM productores WHERE rubro=?", conn, params=(st.session_state.r_sel,)).iloc[0]['total']
    
    col_back, col_tit = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ INICIO"):
            st.session_state.r_sel = None
            st.rerun()
    with col_tit:
        st.markdown(f"### Sector: {st.session_state.r_sel.upper()} <span class='badge-sector'>{total_rubro} productores registrados</span>", unsafe_allow_html=True)

    # Filtros Sectoriales
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        ml = pd.read_sql("SELECT DISTINCT municipio FROM productores WHERE rubro=?", conn, params=(st.session_state.r_sel,))['municipio'].tolist()
        mv = st.selectbox("📍 SELECCIONE MUNICIPIO:", ["-- Seleccione --"] + ml, key="msel_rubro")
    with col_f2:
        av = "-- Todas --"
        if mv != "-- Seleccione --":
            al = pd.read_sql("SELECT DISTINCT aldea FROM productores WHERE rubro=? AND municipio=?", conn, params=(st.session_state.r_sel, mv))['aldea'].tolist()
            av = st.selectbox(f"🏡 ALDEAS EN {mv.upper()}:", ["-- Todas --"] + al, key="asel_rubro")
    with col_f3:
        bn = ""
        if mv != "-- Seleccione --" and av != "-- Todas --":
            bn = st.text_input("🔍 FILTRAR POR NOMBRE:", key="bn_rubro")
        fr = "General"
        if st.session_state.r_sel == "Granos Básicos" and st.toggle("Solo Beneficiarios de Riego"): fr = "Beneficiario Proyecto de Riego"

    if mv != "-- Seleccione --":
        q = "SELECT dni as IDENTIDAD, nombre as NOMBRE, aldea as ALDEA FROM productores WHERE rubro=? AND municipio=? AND riego=?"
        ps = [st.session_state.r_sel, mv, fr]
        if av != "-- Todas --": q += " AND aldea=?"; ps.append(av)
        
        df_f = pd.read_sql(q, conn, params=ps)
        if bn: df_f = df_f[df_f['NOMBRE'].str.contains(bn, case=False)]
        
        st.write(f"Mostrando **{len(df_f)}** productores registrados en esta zona.")
        tid = f"tab_{st.session_state.r_sel}_{mv}_{av}_{fr}"
        sel = st.dataframe(df_f, use_container_width=True, on_select="rerun", selection_mode="single-row", hide_index=True, key=tid)
        if len(sel.selection.rows) > 0: mostrar_ficha(df_f.iloc[sel.selection.rows[0]]['IDENTIDAD'])