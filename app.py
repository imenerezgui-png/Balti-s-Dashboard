"""
Balti's Dashboard — Creative Planning Tracker
Black / Red / Grey gradient theme.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Balti's Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Paths & constants
# ─────────────────────────────────────────────────────────────────────────────
APP_DIR   = Path(__file__).parent
DATA_DIR  = APP_DIR / "data"
DATA_FILE = DATA_DIR / "planning.json"

# Detect cloud: filesystem is read-only on Streamlit Community Cloud
def _fs_writable() -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        test = DATA_DIR / ".write_test"
        test.write_text("x")
        test.unlink()
        return True
    except OSError:
        return False

FS_WRITABLE = _fs_writable()

EDITABLE_COLS = [
    "TEAM CREA 1", "TEAM CREA 2", "ACCOUNTS",
    "BRIEFING CRA", "DEBRIEF", "PIT STOP",
    "% D'AVANCEMENT", "DEADLINE", "PREZ CLIENT",
    "ETAT CREA", "OBSERVATIONS",
]
DATE_COLS = ["BRIEFING CRA", "DEBRIEF", "DEADLINE", "PREZ CLIENT"]
ALL_COLS  = ["id", "CLIENT", "JOB"] + EDITABLE_COLS + ["COMPLETED"]

ETAT_OPTIONS = ["EN COURS", "ATT BAT", "BAT OK", "COMPLETED", "ANNULÉ"]

# ─────────────────────────────────────────────────────────────────────────────
# Theme palette
# ─────────────────────────────────────────────────────────────────────────────
RED       = "#e63946"
RED_DARK  = "#9b1d26"
RED_MID   = "#c0303c"
GREY      = "#3a3a3a"
GREY_LT   = "#606060"
GREY_CARD = "#1c1c1c"
BG        = "#0d0d0d"
SURFACE   = "#161616"
CARD      = "#1a1a1a"
TEXT      = "#f0f0f0"
DIM       = "#888888"
GREEN     = "#27ae60"
AMBER     = "#e67e22"

# ─────────────────────────────────────────────────────────────────────────────
# CSS  (black/red/grey gradient theme)
# ─────────────────────────────────────────────────────────────────────────────
STYLE = f"""
<style>
/* ── global ─────────────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', system-ui, sans-serif;
}}

/* ── sidebar ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #110103 0%, #1a0508 60%, {BG} 100%) !important;
    border-right: 1px solid #2a2a2a;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {{
    color: {TEXT} !important;
}}

/* ── main header ─────────────────────────────────────────────────── */
.dash-header {{
    text-align: center;
    padding: 1.5rem 0 0.3rem 0;
}}
.dash-title {{
    background: linear-gradient(90deg, {GREY_LT} 0%, {RED} 40%, {RED_DARK} 70%, {GREY} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    line-height: 1.1;
}}
.dash-subtitle {{
    color: {DIM};
    font-size: 0.78rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-top: 0.2rem;
}}
.dash-divider {{
    height: 2px;
    background: linear-gradient(90deg, transparent, {RED_DARK}, {RED}, {RED_DARK}, transparent);
    margin: 0.8rem 0 1.5rem 0;
    border: none;
}}

/* ── KPI cards ──────────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.6rem;
}}
.kpi-card {{
    background: linear-gradient(135deg, {CARD} 0%, #1f0508 100%);
    border: 1px solid #2e2e2e;
    border-top: 2px solid {RED_DARK};
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}}
.kpi-card .kpi-value {{
    font-size: 2.2rem;
    font-weight: 900;
    line-height: 1;
}}
.kpi-card .kpi-label {{
    font-size: 0.68rem;
    color: {DIM};
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-top: 0.4rem;
}}

/* ── section titles ─────────────────────────────────────────────── */
.section-title {{
    font-size: 0.75rem;
    font-weight: 700;
    color: {RED};
    text-transform: uppercase;
    letter-spacing: 3px;
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 0.45rem;
    margin: 1.4rem 0 0.9rem 0;
}}

/* ── tabs ───────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {{
    background: {SURFACE};
    border-radius: 12px;
    padding: 0.35rem;
    gap: 0.4rem;
    border: 1px solid #252525;
}}
[data-testid="stTabs"] [role="tab"] {{
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    color: {DIM};
    border: none !important;
    padding: 0.5rem 2rem;
    transition: all 0.2s;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    background: linear-gradient(90deg, {RED_DARK}, {RED}) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(230,57,70,0.4);
}}
[data-testid="stTabs"] [role="tab"]:hover {{
    color: {TEXT} !important;
}}

/* ── buttons ───────────────────────────────────────────────────── */
div[data-testid="stButton"] > button {{
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    transition: all 0.2s;
    border: none;
}}
div[data-testid="stButton"] > button[kind="primary"] {{
    background: linear-gradient(90deg, {RED_DARK}, {RED}) !important;
    color: white !important;
}}
div[data-testid="stButton"] > button[kind="primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 18px rgba(230,57,70,0.45);
}}
div[data-testid="stButton"] > button[kind="secondary"] {{
    background: {GREY_CARD} !important;
    color: {TEXT} !important;
    border: 1px solid {GREY} !important;
}}

/* ── form / inputs ──────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border: 1px solid #333 !important;
}}

/* ── data editor ────────────────────────────────────────────────── */
[data-testid="stDataEditor"] {{
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    overflow: hidden;
}}

/* ── expander ───────────────────────────────────────────────────── */
[data-testid="stExpander"] details {{
    background: {CARD};
    border: 1px solid #2a2a2a !important;
    border-radius: 10px;
}}
[data-testid="stExpander"] summary {{
    color: {TEXT};
    font-weight: 600;
}}

/* ── alerts ─────────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    background: {CARD} !important;
    border-radius: 8px;
}}

/* ── hide Streamlit chrome ───────────────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_excel_date(v) -> str | None:
    """Return ISO date string or None from any Excel cell value."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, (datetime, pd.Timestamp)):
        ts = pd.Timestamp(v)
        if ts.year < 1950:   # Excel artefact date
            return None
        return ts.strftime("%Y-%m-%d")
    if isinstance(v, date):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    return None if s in ("", "nan", "NaT", "None") else s[:10]


def _parse_pct(v) -> int:
    """Convert Excel % D'AVANCEMENT cell to int 0-100."""
    if v is None:
        return 0
    try:
        if pd.isna(v):
            return 0
    except (TypeError, ValueError):
        pass
    if isinstance(v, (datetime, pd.Timestamp)):
        ts = pd.Timestamp(v)
        if ts.year < 1950:    # serial encoded as date artefact
            return 0          # cannot reliably decode — reset to 0
        return 0
    if isinstance(v, (int, float)):
        if 0 < v <= 1:
            return int(round(v * 100))
        return max(0, min(100, int(v)))
    return 0


def import_from_excel(file_obj=None) -> pd.DataFrame:
    """Parse a PLANNING Excel file and return a clean DataFrame."""
    raw = pd.read_excel(file_obj, sheet_name="PLANNING TEAM", header=None)
    # locate header row containing 'CLIENT' and 'JOB'
    hdr_row = None
    for i, row in raw.iterrows():
        vals = [str(x).strip() for x in row.values]
        if "CLIENT" in vals and "JOB" in vals:
            hdr_row = i
            break
    if hdr_row is None:
        return pd.DataFrame(columns=ALL_COLS)

    df = pd.read_excel(file_obj, sheet_name="PLANNING TEAM", header=hdr_row)
    df.columns.name = None
    # strip extra unnamed cols
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # drop completely empty rows
    df = df.dropna(how="all").reset_index(drop=True)

    # forward-fill CLIENT (merged cells)
    if "CLIENT" in df.columns:
        df["CLIENT"] = df["CLIENT"].ffill()

    rows: list[dict] = []
    for _, row in df.iterrows():
        client = str(row.get("CLIENT", "") or "").strip()
        job    = str(row.get("JOB",    "") or "").strip()
        if not client and not job:
            continue
        pct_raw = row.get("% D'AVANCEMENT")
        rec = {
            "id":              str(uuid.uuid4())[:8],
            "CLIENT":          client,
            "JOB":             job,
            "TEAM CREA 1":     str(row.get("TEAM CREA 1",  "") or "").strip(),
            "TEAM CREA 2":     str(row.get("TEAM CREA 2",  "") or "").strip(),
            "ACCOUNTS":        str(row.get("ACCOUNTS",     "") or "").strip(),
            "BRIEFING CRA":    _parse_excel_date(row.get("BRIEFING CRA")),
            "DEBRIEF":         _parse_excel_date(row.get("DEBRIEF")),
            "PIT STOP":        str(row.get("PIT STOP",     "") or "").strip(),
            "% D'AVANCEMENT":  _parse_pct(pct_raw),
            "DEADLINE":        _parse_excel_date(row.get("DEADLINE")),
            "PREZ CLIENT":     _parse_excel_date(row.get("PREZ CLIENT")),
            "ETAT CREA":       str(row.get("ETAT CREA",   "") or "EN COURS").strip() or "EN COURS",
            "OBSERVATIONS":    str(row.get("OBSERVATIONS", "") or "").strip(),
            "COMPLETED":       False,
        }
        rows.append(rec)

    return pd.DataFrame(rows, columns=ALL_COLS)


def load_data() -> pd.DataFrame:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
    if not records:
        return pd.DataFrame(columns=ALL_COLS)
    df = pd.DataFrame(records)
    for col in ALL_COLS:
        if col not in df.columns:
            df[col] = None
    return df[ALL_COLS]


def save_data(df: pd.DataFrame) -> None:
    if not FS_WRITABLE:
        return  # cloud: session state is the only store
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_json(DATA_FILE, orient="records", indent=2, force_ascii=False)


def df_to_json_bytes(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", indent=2, force_ascii=False).encode("utf-8")


def _prep_editor_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date string columns to Python date objects for st.data_editor."""
    out = df.copy()
    for col in DATE_COLS:
        if col not in out.columns:
            continue
        def to_date(v):
            if v is None or str(v).strip() in ("", "nan", "NaT", "None"):
                return None
            try:
                return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
            except ValueError:
                return None
        out[col] = out[col].apply(to_date)
    if "% D'AVANCEMENT" in out.columns:
        out["% D'AVANCEMENT"] = pd.to_numeric(out["% D'AVANCEMENT"], errors="coerce").fillna(0).astype(int)
    if "COMPLETED" in out.columns:
        out["COMPLETED"] = out["COMPLETED"].astype(bool)
    return out


def get_df() -> pd.DataFrame:
    if "df" not in st.session_state:
        if DATA_FILE.exists():
            st.session_state.df = load_data()
        else:
            st.session_state.df = pd.DataFrame(columns=ALL_COLS)
    return st.session_state.df


# ─────────────────────────────────────────────────────────────────────────────
# Chart helpers
# ─────────────────────────────────────────────────────────────────────────────

def _plotly_layout(**kwargs) -> dict:
    defaults = dict(
        paper_bgcolor=BG,
        plot_bgcolor=SURFACE,
        font=dict(color=TEXT, family="Segoe UI", size=12),
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(font=dict(color=TEXT), bgcolor="rgba(0,0,0,0)"),
    )
    defaults.update(kwargs)
    return defaults


ETAT_COLOR = {
    "COMPLETED": GREEN,
    "BAT OK":    "#2980b9",
    "EN COURS":  AMBER,
    "ATT BAT":   RED,
    "ANNULÉ":    GREY_LT,
}


# ─────────────────────────────────────────────────────────────────────────────
# ── RENDER ──────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(STYLE, unsafe_allow_html=True)

# ── Banner ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="dash-header">'
    '  <div class="dash-title">🎯 BALTI\'S DASHBOARD</div>'
    '  <div class="dash-subtitle">Creative Planning · Production Tracker</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="dash-divider">', unsafe_allow_html=True)

df = get_df()

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<span style="font-size:1.4rem;font-weight:900;'
        f'background:linear-gradient(90deg,{GREY_LT},{RED});'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        f'🎯 Balti\'s Dashboard</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    clients = ["All"] + sorted({r for r in df["CLIENT"].dropna() if r})
    sel_client = st.selectbox("Filter by Client", clients, key="sb_client")

    etats = ["All"] + ETAT_OPTIONS
    sel_etat = st.selectbox("Filter by État", etats, key="sb_etat")

    show_completed = st.checkbox("Show Completed", value=True, key="cb_completed")

    st.markdown("---")

    with st.expander("📥  Import Excel", expanded=False):
        uploaded = st.file_uploader(
            "Upload PLANNING.xlsx", type=["xlsx", "xls"], label_visibility="collapsed"
        )
        if uploaded and st.button("Import", key="btn_import"):
            st.session_state.df = import_from_excel(uploaded)
            save_data(st.session_state.df)
            st.success("Imported!")
            st.rerun()

    with st.expander("💾  Backup / Restore", expanded=False):
        cur_df = st.session_state.get("df", pd.DataFrame(columns=ALL_COLS))
        st.download_button(
            "⬇ Download JSON backup",
            data=df_to_json_bytes(cur_df),
            file_name="planning_backup.json",
            mime="application/json",
            key="btn_dl",
        )
        restore_file = st.file_uploader(
            "Upload JSON backup", type=["json"], key="restore_upload", label_visibility="collapsed"
        )
        if restore_file and st.button("Restore", key="btn_restore"):
            records = json.load(restore_file)
            st.session_state.df = pd.DataFrame(records)
            save_data(st.session_state.df)
            st.success("Restored!")
            st.rerun()

    if not FS_WRITABLE:
        st.caption("☁️ Cloud mode — use backup to persist changes")

    st.markdown("---")
    total     = len(df)
    done      = int(df["COMPLETED"].astype(bool).sum()) if "COMPLETED" in df.columns else 0
    pct_done  = round(done / total * 100) if total else 0
    st.markdown(f"**{done}/{total}** jobs completed")
    st.progress(pct_done / 100)

# ─────────────────────────────────────────────────────────────────────────────
# KPI cards
# ─────────────────────────────────────────────────────────────────────────────
today = date.today()


def _count_overdue(df_: pd.DataFrame) -> int:
    n = 0
    for _, row in df_.iterrows():
        dl = row.get("DEADLINE")
        if dl and str(dl) not in ("None", "NaT", "nan", ""):
            try:
                d = datetime.strptime(str(dl)[:10], "%Y-%m-%d").date()
                if d < today and not bool(row.get("COMPLETED", False)):
                    n += 1
            except ValueError:
                pass
    return n


total_jobs  = len(df)
completed   = int(df["COMPLETED"].astype(bool).sum()) if "COMPLETED" in df.columns else 0
in_progress = int(df["ETAT CREA"].isin(["EN COURS", "ATT BAT"]).sum()) if "ETAT CREA" in df.columns else 0
overdue     = _count_overdue(df)

st.markdown(
    f"""<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-value" style="color:{RED}">{total_jobs}</div>
    <div class="kpi-label">Total Jobs</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:{GREEN}">{completed}</div>
    <div class="kpi-label">Completed</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:{AMBER}">{in_progress}</div>
    <div class="kpi-label">In Progress</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#e74c3c">{overdue}</div>
    <div class="kpi-label">Overdue</div>
  </div>
</div>""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Filter view
# ─────────────────────────────────────────────────────────────────────────────
view = df.copy()
if sel_client != "All":
    view = view[view["CLIENT"] == sel_client]
if sel_etat != "All":
    view = view[view["ETAT CREA"] == sel_etat]
if not show_completed:
    view = view[~view["COMPLETED"].astype(bool)]

# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_plan, tab_viz = st.tabs(["📋   Planning Board", "📊   Progress & Analytics"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — PLANNING BOARD
# ═════════════════════════════════════════════════════════════════════════════
with tab_plan:

    # ── Add new job ──────────────────────────────────────────────────────────
    with st.expander("➕  Add New Job", expanded=False):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_client = c1.text_input("CLIENT *")
            new_job    = c2.text_input("JOB *")

            c3, c4, c5 = st.columns(3)
            new_tc1  = c3.text_input("TEAM CREA 1")
            new_tc2  = c4.text_input("TEAM CREA 2")
            new_acc  = c5.text_input("ACCOUNTS")

            c6, c7, c8 = st.columns(3)
            new_brief   = c6.date_input("BRIEFING CRA",  value=None)
            new_debrief = c7.date_input("DEBRIEF",        value=None)
            new_dl      = c8.date_input("DEADLINE",       value=None)

            c9, c10 = st.columns(2)
            new_prez = c9.date_input("PREZ CLIENT", value=None)
            new_pct  = c10.number_input("% D'AVANCEMENT", 0, 100, 0)

            c11, c12 = st.columns(2)
            new_etat = c11.selectbox("ETAT CREA", ETAT_OPTIONS)
            new_pit  = c12.text_input("PIT STOP")
            new_obs  = st.text_area("OBSERVATIONS")

            submitted = st.form_submit_button(
                "➕  Add Job", type="primary", width='stretch'
            )

        if submitted:
            if not new_client.strip() or not new_job.strip():
                st.error("CLIENT and JOB are required.")
            else:
                new_row = {
                    "id":              str(uuid.uuid4())[:8],
                    "CLIENT":          new_client.strip(),
                    "JOB":             new_job.strip(),
                    "TEAM CREA 1":     new_tc1.strip(),
                    "TEAM CREA 2":     new_tc2.strip(),
                    "ACCOUNTS":        new_acc.strip(),
                    "BRIEFING CRA":    str(new_brief)  if new_brief  else None,
                    "DEBRIEF":         str(new_debrief) if new_debrief else None,
                    "PIT STOP":        new_pit.strip(),
                    "% D'AVANCEMENT":  int(new_pct),
                    "DEADLINE":        str(new_dl)    if new_dl    else None,
                    "PREZ CLIENT":     str(new_prez)  if new_prez  else None,
                    "ETAT CREA":       new_etat,
                    "OBSERVATIONS":    new_obs.strip(),
                    "COMPLETED":       False,
                }
                st.session_state.df = pd.concat(
                    [df, pd.DataFrame([new_row])], ignore_index=True
                )
                save_data(st.session_state.df)
                st.success(f"✅ '{new_job.strip()}' added!")
                st.rerun()

    # ── Editable table ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Job Board</div>', unsafe_allow_html=True)

    DISPLAY_COLS = ["CLIENT", "JOB"] + EDITABLE_COLS + ["COMPLETED"]

    col_cfg = {
        "CLIENT":          st.column_config.TextColumn("CLIENT",          disabled=True, width="medium"),
        "JOB":             st.column_config.TextColumn("JOB",             width="large"),
        "TEAM CREA 1":     st.column_config.TextColumn("TEAM CREA 1",     width="medium"),
        "TEAM CREA 2":     st.column_config.TextColumn("TEAM CREA 2",     width="medium"),
        "ACCOUNTS":        st.column_config.TextColumn("ACCOUNTS",        width="small"),
        "BRIEFING CRA":    st.column_config.DateColumn("BRIEFING CRA"),
        "DEBRIEF":         st.column_config.DateColumn("DEBRIEF"),
        "PIT STOP":        st.column_config.TextColumn("PIT STOP",        width="small"),
        "% D'AVANCEMENT":  st.column_config.ProgressColumn(
                               "% D'AVANCEMENT", min_value=0, max_value=100, format="%d%%"
                           ),
        "DEADLINE":        st.column_config.DateColumn("DEADLINE"),
        "PREZ CLIENT":     st.column_config.DateColumn("PREZ CLIENT"),
        "ETAT CREA":       st.column_config.SelectboxColumn(
                               "ETAT CREA", options=ETAT_OPTIONS, width="medium"
                           ),
        "OBSERVATIONS":    st.column_config.TextColumn("OBSERVATIONS",    width="large"),
        "COMPLETED":       st.column_config.CheckboxColumn("✅ Done"),
    }

    editor_df = _prep_editor_df(view[DISPLAY_COLS].reset_index(drop=True))

    edited = st.data_editor(
        editor_df,
        column_config=col_cfg,
        width='stretch',
        num_rows="fixed",
        hide_index=True,
        key="data_editor",
    )

    # ── Action buttons ───────────────────────────────────────────────────────
    btn_cols = st.columns([1, 1.6, 1.6, 3])

    with btn_cols[0]:
        if st.button("💾  Save", type="primary", width='stretch'):
            orig_indices = view.index.tolist()
            for i, orig_idx in enumerate(orig_indices):
                for col in DISPLAY_COLS:
                    val = edited.iloc[i][col]
                    # convert date objects back to strings
                    if isinstance(val, date):
                        val = val.isoformat()
                    df.at[orig_idx, col] = val
            st.session_state.df = df
            save_data(df)
            st.success("Changes saved!")
            st.rerun()

    with btn_cols[1]:
        if st.button("✅  Mark All as Completed", width='stretch'):
            orig_indices = view.index.tolist()
            for orig_idx in orig_indices:
                df.at[orig_idx, "COMPLETED"]        = True
                df.at[orig_idx, "ETAT CREA"]        = "COMPLETED"
                df.at[orig_idx, "% D'AVANCEMENT"]   = 100
            st.session_state.df = df
            save_data(df)
            st.success("Marked as completed!")
            st.rerun()

    with btn_cols[2]:
        if st.button("↩  Unmark Selected", width='stretch'):
            orig_indices = view.index.tolist()
            for i, orig_idx in enumerate(orig_indices):
                if edited.iloc[i]["COMPLETED"]:
                    df.at[orig_idx, "COMPLETED"] = False
                    if df.at[orig_idx, "ETAT CREA"] == "COMPLETED":
                        df.at[orig_idx, "ETAT CREA"] = "EN COURS"
            st.session_state.df = df
            save_data(df)
            st.rerun()

    # ── Delete completed ──────────────────────────────────────────────────────
    with st.expander("🗑  Danger Zone", expanded=False):
        if st.button("Delete ALL completed jobs", type="secondary"):
            st.session_state.df = df[~df["COMPLETED"].astype(bool)].reset_index(drop=True)
            save_data(st.session_state.df)
            st.success("Deleted.")
            st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — PROGRESS & ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
with tab_viz:

    if len(df) == 0:
        st.info("No data yet. Add jobs in the Planning Board tab.")
        st.stop()

    # ── Row 1: Donut + Bar ───────────────────────────────────────────────────
    r1a, r1b = st.columns(2)

    with r1a:
        st.markdown('<div class="section-title">Status Distribution</div>', unsafe_allow_html=True)
        ec = df["ETAT CREA"].value_counts().reset_index()
        ec.columns = ["ETAT", "COUNT"]
        fig_donut = go.Figure(go.Pie(
            labels=ec["ETAT"],
            values=ec["COUNT"],
            hole=0.58,
            marker=dict(
                colors=[ETAT_COLOR.get(e, GREY_LT) for e in ec["ETAT"]],
                line=dict(color=BG, width=3),
            ),
            textinfo="percent+label",
            textfont=dict(color=TEXT, size=12),
            hovertemplate="<b>%{label}</b><br>%{value} jobs (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(**_plotly_layout(height=330, showlegend=False))
        st.plotly_chart(fig_donut, width='stretch')

    with r1b:
        st.markdown('<div class="section-title">Jobs per Client</div>', unsafe_allow_html=True)
        cc = df.groupby("CLIENT").size().reset_index(name="COUNT").sort_values("COUNT")
        fig_bar = go.Figure(go.Bar(
            x=cc["COUNT"],
            y=cc["CLIENT"],
            orientation="h",
            marker=dict(
                color=cc["COUNT"],
                colorscale=[[0, RED_DARK], [0.5, RED_MID], [1, RED]],
                showscale=False,
            ),
            text=cc["COUNT"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} jobs<extra></extra>",
        ))
        fig_bar.update_layout(**_plotly_layout(
            height=330,
            showlegend=False,
            xaxis=dict(showgrid=False, color=DIM),
            yaxis=dict(showgrid=False, color=TEXT),
        ))
        st.plotly_chart(fig_bar, width='stretch')

    # ── Row 2: Progress bars ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">% Avancement per Job (top 20)</div>', unsafe_allow_html=True)

    prog = df.copy()
    prog["% D'AVANCEMENT"] = pd.to_numeric(prog["% D'AVANCEMENT"], errors="coerce").fillna(0)
    prog = prog[prog["% D'AVANCEMENT"] > 0].copy()
    prog["label"] = prog["CLIENT"].fillna("?") + "  ·  " + prog["JOB"].fillna("?")
    prog = prog.sort_values("% D'AVANCEMENT").tail(20)

    if len(prog):
        bar_colors = []
        for _, row in prog.iterrows():
            p = row["% D'AVANCEMENT"]
            if bool(row.get("COMPLETED", False)) or p == 100:
                bar_colors.append(GREEN)
            elif p >= 60:
                bar_colors.append(AMBER)
            else:
                bar_colors.append(RED)

        fig_prog = go.Figure(go.Bar(
            x=prog["% D'AVANCEMENT"],
            y=prog["label"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(color=BG, width=0.5)),
            text=[f"{p:.0f}%" for p in prog["% D'AVANCEMENT"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x}%<extra></extra>",
        ))
        fig_prog.add_vline(x=50, line_color=GREY, line_dash="dot", line_width=1)
        fig_prog.update_layout(**_plotly_layout(
            height=max(280, len(prog) * 32),
            showlegend=False,
            xaxis=dict(range=[0, 115], showgrid=False, title="% Avancement", color=DIM),
            yaxis=dict(showgrid=False, color=TEXT),
        ))
        st.plotly_chart(fig_prog, width='stretch')
    else:
        st.info("Set % D'Avancement values in the Planning Board to see this chart.")

    # ── Row 3: Deadline Gantt ────────────────────────────────────────────────
    st.markdown('<div class="section-title">Deadline Timeline</div>', unsafe_allow_html=True)

    gantt_rows: list[dict] = []
    for _, row in df.iterrows():
        start = row.get("BRIEFING CRA")
        end   = row.get("DEADLINE")
        if (start and str(start) not in ("None", "NaT", "nan", "")
                and end   and str(end)   not in ("None", "NaT", "nan", "")):
            try:
                s = datetime.strptime(str(start)[:10], "%Y-%m-%d")
                e = datetime.strptime(str(end)[:10],   "%Y-%m-%d")
                if s <= e:
                    gantt_rows.append({
                        "Task":   f"{row['CLIENT']}  ·  {row['JOB']}",
                        "Start":  s,
                        "Finish": e,
                        "État":   row.get("ETAT CREA", "EN COURS") or "EN COURS",
                    })
            except ValueError:
                pass

    if gantt_rows:
        gdf = pd.DataFrame(gantt_rows)
        fig_gantt = px.timeline(
            gdf, x_start="Start", x_end="Finish", y="Task",
            color="État",
            color_discrete_map=ETAT_COLOR,
        )
        fig_gantt.update_layout(**_plotly_layout(
            height=max(350, len(gantt_rows) * 30),
            xaxis=dict(showgrid=False, color=DIM),
            yaxis=dict(showgrid=False, color=TEXT, autorange="reversed"),
        ))
        # mark today
        fig_gantt.add_vline(
            x=datetime.combine(today, datetime.min.time()).timestamp() * 1000,
            line_color=RED, line_dash="dot", line_width=1.5,
            annotation_text="Today", annotation_font_color=RED,
        )
        st.plotly_chart(fig_gantt, width='stretch')
    else:
        st.info("Set **Briefing CRA** and **Deadline** dates to see the timeline.")

    # ── Row 4: Completed vs Not over time ────────────────────────────────────
    st.markdown('<div class="section-title">Completion Rate by Client</div>', unsafe_allow_html=True)

    comp_grp = df.groupby("CLIENT").agg(
        Total   =("JOB", "count"),
        Done    =("COMPLETED", lambda x: x.astype(bool).sum()),
    ).reset_index()
    comp_grp["Pending"] = comp_grp["Total"] - comp_grp["Done"]
    comp_grp = comp_grp.sort_values("Total", ascending=False)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Completed", x=comp_grp["CLIENT"], y=comp_grp["Done"],
        marker_color=GREEN,
    ))
    fig_comp.add_trace(go.Bar(
        name="Pending", x=comp_grp["CLIENT"], y=comp_grp["Pending"],
        marker_color=RED,
    ))
    fig_comp.update_layout(**_plotly_layout(
        barmode="stack",
        height=320,
        xaxis=dict(showgrid=False, color=DIM),
        yaxis=dict(showgrid=False, color=DIM, title="Jobs"),
    ))
    st.plotly_chart(fig_comp, width='stretch')

