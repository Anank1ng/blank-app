import streamlit as st
import json
import os
from datetime import datetime, date
import uuid

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaskBoard Pro",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* Root Variables */
:root {
    --bg: #0f0f13;
    --surface: #17171f;
    --surface2: #1e1e28;
    --surface3: #252533;
    --border: #2e2e3e;
    --accent: #7c6af7;
    --accent2: #f7c56a;
    --accent3: #6af7c5;
    --accent4: #f76a8f;
    --text: #e8e8f0;
    --text2: #9090a8;
    --text3: #5a5a70;
    --red: #f76a6a;
    --green: #6af7a0;
    --yellow: #f7e06a;
}

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide Streamlit Branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Main Container */
.main .block-container {
    padding: 1.5rem 2rem;
    max-width: 100%;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }

/* App Title */
.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.app-subtitle {
    font-size: 0.75rem;
    color: var(--text3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.logo-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--accent);
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 12px var(--accent);
}

/* Nav Items */
.nav-section {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text3);
    margin: 1.5rem 0 0.5rem 0.3rem;
    font-weight: 600;
}

/* Cards */
.board-column {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem;
    min-height: 400px;
}
.column-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.col-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.task-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.task-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--accent);
    border-radius: 3px 0 0 3px;
}
.task-card.urgent::before { background: var(--accent4); }
.task-card.done::before { background: var(--accent3); }
.task-card.hold::before { background: var(--accent2); }

.task-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.task-meta {
    font-size: 0.72rem;
    color: var(--text3);
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.tag-todo { background: rgba(124,106,247,0.15); color: var(--accent); border: 1px solid rgba(124,106,247,0.3); }
.tag-inprogress { background: rgba(247,197,106,0.15); color: var(--accent2); border: 1px solid rgba(247,197,106,0.3); }
.tag-done { background: rgba(106,247,197,0.15); color: var(--accent3); border: 1px solid rgba(106,247,197,0.3); }
.tag-urgent { background: rgba(247,106,143,0.15); color: var(--accent4); border: 1px solid rgba(247,106,143,0.3); }

/* Progress Bar */
.progress-wrap {
    background: var(--surface3);
    border-radius: 20px;
    height: 6px;
    margin: 0.5rem 0;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.5s ease;
}

/* Stats */
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.stat-number {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.stat-label {
    font-size: 0.7rem;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Memo Card */
.memo-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid var(--accent2);
}
.memo-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.memo-body {
    font-size: 0.82rem;
    color: var(--text2);
    line-height: 1.6;
}
.memo-date {
    font-size: 0.68rem;
    color: var(--text3);
    margin-top: 0.5rem;
}

/* Reminder */
.reminder-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.reminder-overdue { border-left: 3px solid var(--red); }
.reminder-today { border-left: 3px solid var(--yellow); }
.reminder-upcoming { border-left: 3px solid var(--accent3); }

/* Checklist */
.checklist-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.4rem 0;
    font-size: 0.84rem;
    color: var(--text2);
}
.checklist-item.done {
    text-decoration: line-through;
    color: var(--text3);
}

/* Section Divider */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}
.section-sub {
    font-size: 0.78rem;
    color: var(--text3);
    margin-bottom: 1.5rem;
}

/* Buttons Override */
.stButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--surface3) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: white !important;
    border-color: var(--accent) !important;
}

/* Form inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.2) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    gap: 4px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text3) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface3) !important;
    color: var(--text) !important;
}

/* Checkbox */
.stCheckbox > label > span { color: var(--text2) !important; font-size: 0.84rem !important; }

/* Metric */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* Alert boxes */
.stAlert {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--border); }
</style>
""", unsafe_allow_html=True)

# ─── Data Persistence ──────────────────────────────────────────────────────────
DATA_FILE = "taskboard_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "tasks": [],
        "memos": [],
        "reminders": [],
        "checklists": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ─── Init Session State ────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "page" not in st.session_state:
    st.session_state.page = "Board"

data = st.session_state.data

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="app-title"><span class="logo-dot"></span>TaskBoard</div>
    <div class="app-subtitle">Pro Workspace</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="nav-section">Menu</div>', unsafe_allow_html=True)
    
    pages = {
        "Board": "🗂️",
        "Memo & Catatan": "📝",
        "Reminder": "🔔",
        "Checklist": "✅",
    }
    
    for page_name, icon in pages.items():
        is_active = st.session_state.page == page_name
        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    
    # Quick stats
    tasks = data.get("tasks", [])
    total = len(tasks)
    done_count = len([t for t in tasks if t["status"] == "Done"])
    inprog = len([t for t in tasks if t["status"] == "In Progress"])
    
    st.markdown('<div class="nav-section">Statistik Cepat</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Task", total)
        st.metric("Selesai", done_count)
    with col2:
        st.metric("Progres", inprog)
        overdue_rem = len([r for r in data.get("reminders", []) 
                          if r.get("date") and datetime.strptime(r["date"], "%Y-%m-%d").date() < date.today() 
                          and not r.get("done")])
        st.metric("⚠️ Terlambat", overdue_rem)

# ─── Helper ────────────────────────────────────────────────────────────────────
def priority_color(p):
    return {"Tinggi": "urgent", "Sedang": "", "Rendah": "done"}.get(p, "")

def status_tag(s):
    m = {"Todo": "tag-todo", "In Progress": "tag-inprogress", "Done": "tag-done", "On Hold": "tag-urgent"}
    return m.get(s, "tag-todo")

def calc_progress(task):
    items = task.get("checklist", [])
    if not items:
        return 0
    done = sum(1 for i in items if i.get("done"))
    return int((done / len(items)) * 100)

def progress_color(pct):
    if pct == 100: return "#6af7a0"
    if pct >= 60: return "#7c6af7"
    if pct >= 30: return "#f7c56a"
    return "#f76a8f"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Board":
    st.markdown('<div class="section-title">Papan Tugas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Kelola semua tugas kamu dalam satu tampilan — seperti Trello</div>', unsafe_allow_html=True)

    # Add Task Form
    with st.expander("➕ Tambah Tugas Baru", expanded=False):
        with st.form("add_task_form"):
            c1, c2 = st.columns(2)
            with c1:
                task_title = st.text_input("Judul Tugas *", placeholder="Contoh: Desain Landing Page")
                task_status = st.selectbox("Status", ["Todo", "In Progress", "Done", "On Hold"])
                task_priority = st.selectbox("Prioritas", ["Tinggi", "Sedang", "Rendah"])
            with c2:
                task_desc = st.text_area("Deskripsi", placeholder="Detail tugas...", height=100)
                task_due = st.date_input("Deadline", value=None)
                task_tags = st.text_input("Tag (pisahkan dengan koma)", placeholder="design, frontend, ui")
            
            # Inline checklist
            st.markdown("**Checklist Item** (opsional, satu per baris)")
            checklist_text = st.text_area("", placeholder="Buat wireframe\nImplement layout\nReview dengan klien", height=80, label_visibility="collapsed")
            
            submitted = st.form_submit_button("✦ Tambah Tugas", use_container_width=True, type="primary")
            if submitted and task_title:
                checklist_items = []
                if checklist_text.strip():
                    for item in checklist_text.strip().split("\n"):
                        if item.strip():
                            checklist_items.append({"id": str(uuid.uuid4())[:8], "text": item.strip(), "done": False})
                
                new_task = {
                    "id": str(uuid.uuid4())[:8],
                    "title": task_title,
                    "description": task_desc,
                    "status": task_status,
                    "priority": task_priority,
                    "due": str(task_due) if task_due else None,
                    "tags": [t.strip() for t in task_tags.split(",") if t.strip()],
                    "checklist": checklist_items,
                    "created": str(date.today())
                }
                data["tasks"].append(new_task)
                save_data(data)
                st.success("✦ Tugas berhasil ditambahkan!")
                st.rerun()

    st.markdown("---")

    # Overall progress bar
    tasks = data.get("tasks", [])
    if tasks:
        done_pct = int((len([t for t in tasks if t["status"] == "Done"]) / len(tasks)) * 100)
        st.markdown(f"""
        <div style="margin-bottom:1.5rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.85rem;">Progress Keseluruhan</span>
                <span style="font-size:0.85rem;color:var(--accent);font-weight:700;">{done_pct}%</span>
            </div>
            <div class="progress-wrap">
                <div class="progress-fill" style="width:{done_pct}%;background:{progress_color(done_pct)};"></div>
            </div>
            <div style="font-size:0.72rem;color:var(--text3);margin-top:4px;">{len([t for t in tasks if t['status']=='Done'])} dari {len(tasks)} tugas selesai</div>
        </div>
        """, unsafe_allow_html=True)

    # Columns
    statuses = ["Todo", "In Progress", "Done", "On Hold"]
    col_colors = {"Todo": "#7c6af7", "In Progress": "#f7c56a", "Done": "#6af7c5", "On Hold": "#f76a8f"}
    col_icons = {"Todo": "○", "In Progress": "◑", "Done": "●", "On Hold": "⊘"}
    
    cols = st.columns(4)
    for i, status in enumerate(statuses):
        with cols[i]:
            status_tasks = [t for t in tasks if t["status"] == status]
            color = col_colors[status]
            st.markdown(f"""
            <div class="column-header" style="color:{color};">
                <span class="col-dot" style="background:{color};box-shadow:0 0 8px {color}60;"></span>
                {status}
                <span style="margin-left:auto;background:rgba(255,255,255,0.05);border-radius:20px;padding:2px 8px;font-size:0.7rem;color:var(--text3);">{len(status_tasks)}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if not status_tasks:
                st.markdown(f'<div style="text-align:center;padding:2rem;color:var(--text3);font-size:0.8rem;">Tidak ada tugas</div>', unsafe_allow_html=True)
            
            for task in status_tasks:
                pct = calc_progress(task)
                p_color = progress_color(pct)
                card_class = priority_color(task["priority"])
                due_str = ""
                if task.get("due"):
                    due_date = datetime.strptime(task["due"], "%Y-%m-%d").date()
                    if due_date < date.today() and status != "Done":
                        due_str = f'<span style="color:var(--red);">⚠ {task["due"]}</span>'
                    elif due_date == date.today():
                        due_str = f'<span style="color:var(--yellow);">🔔 Hari ini</span>'
                    else:
                        due_str = f'<span>📅 {task["due"]}</span>'
                
                tags_html = " ".join([f'<span class="tag tag-todo">{t}</span>' for t in task.get("tags", [])[:2]])
                
                checklist_html = ""
                if task.get("checklist"):
                    done_c = sum(1 for c in task["checklist"] if c["done"])
                    total_c = len(task["checklist"])
                    checklist_html = f"""
                    <div style="margin-top:8px;">
                        <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text3);margin-bottom:4px;">
                            <span>✓ {done_c}/{total_c}</span>
                            <span style="color:{p_color};">{pct}%</span>
                        </div>
                        <div class="progress-wrap">
                            <div class="progress-fill" style="width:{pct}%;background:{p_color};"></div>
                        </div>
                    </div>
                    """
                
                st.markdown(f"""
                <div class="task-card {card_class}">
                    <div class="task-title">{task['title']}</div>
                    {f'<div style="font-size:0.75rem;color:var(--text3);margin-top:2px;">{task["description"][:60]}{"..." if len(task.get("description",""))>60 else ""}</div>' if task.get("description") else ""}
                    {checklist_html}
                    <div class="task-meta">
                        {due_str}
                        {tags_html}
                        <span style="margin-left:auto;"><span class="tag tag-{'todo' if task['priority']=='Tinggi' else 'done' if task['priority']=='Rendah' else 'inprogress'}">{task['priority']}</span></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"⚙ Edit • {task['title'][:20]}"):
                    with st.form(f"edit_{task['id']}"):
                        new_status = st.selectbox("Status", ["Todo", "In Progress", "Done", "On Hold"], 
                                                  index=["Todo", "In Progress", "Done", "On Hold"].index(task["status"]))
                        new_priority = st.selectbox("Prioritas", ["Tinggi", "Sedang", "Rendah"],
                                                    index=["Tinggi", "Sedang", "Rendah"].index(task["priority"]))
                        
                        # Checklist editor
                        if task.get("checklist"):
                            st.markdown("**Checklist:**")
                            updated_checks = []
                            for ci, item in enumerate(task["checklist"]):
                                checked = st.checkbox(item["text"], value=item["done"], key=f"chk_{task['id']}_{ci}")
                                updated_checks.append({**item, "done": checked})
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            save_edit = st.form_submit_button("💾 Simpan", use_container_width=True)
                        with c2:
                            delete_task = st.form_submit_button("🗑 Hapus", use_container_width=True)
                        
                        if save_edit:
                            for t in data["tasks"]:
                                if t["id"] == task["id"]:
                                    t["status"] = new_status
                                    t["priority"] = new_priority
                                    if task.get("checklist"):
                                        t["checklist"] = updated_checks
                            save_data(data)
                            st.rerun()
                        if delete_task:
                            data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                            save_data(data)
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MEMO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Memo & Catatan":
    st.markdown('<div class="section-title">📝 Memo & Catatan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Simpan catatan penting, ide, atau informasi apapun</div>', unsafe_allow_html=True)
    
    # Add Memo Form
    with st.expander("➕ Tulis Memo Baru", expanded=False):
        with st.form("add_memo"):
            memo_title = st.text_input("Judul Memo *", placeholder="Judul singkat memo...")
            memo_body = st.text_area("Isi Memo", placeholder="Tulis catatan kamu di sini...", height=150)
            memo_category = st.selectbox("Kategori", ["Umum", "Pekerjaan", "Ide", "Personal", "Penting"])
            submitted = st.form_submit_button("📌 Simpan Memo", use_container_width=True, type="primary")
            if submitted and memo_title:
                data["memos"].append({
                    "id": str(uuid.uuid4())[:8],
                    "title": memo_title,
                    "body": memo_body,
                    "category": memo_category,
                    "created": str(datetime.now().strftime("%d %b %Y, %H:%M"))
                })
                save_data(data)
                st.success("📌 Memo tersimpan!")
                st.rerun()
    
    st.markdown("---")
    
    memos = data.get("memos", [])
    if not memos:
        st.info("Belum ada memo. Tulis memo pertamamu!")
    else:
        # Filter
        cats = ["Semua"] + list(set(m["category"] for m in memos))
        selected_cat = st.selectbox("Filter Kategori", cats, label_visibility="collapsed")
        
        filtered = memos if selected_cat == "Semua" else [m for m in memos if m["category"] == selected_cat]
        
        cat_colors = {"Umum": "#7c6af7", "Pekerjaan": "#f7c56a", "Ide": "#6af7c5", "Personal": "#f76a8f", "Penting": "#f76a6a"}
        
        cols = st.columns(2)
        for idx, memo in enumerate(reversed(filtered)):
            with cols[idx % 2]:
                c = cat_colors.get(memo.get("category", "Umum"), "#7c6af7")
                st.markdown(f"""
                <div class="memo-card" style="border-left-color:{c};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div class="memo-title">{memo['title']}</div>
                        <span class="tag" style="background:rgba(255,255,255,0.05);color:var(--text3);">{memo.get('category','Umum')}</span>
                    </div>
                    <div class="memo-body">{memo['body']}</div>
                    <div class="memo-date">🕐 {memo.get('created','')}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑 Hapus", key=f"del_memo_{memo['id']}", use_container_width=True):
                    data["memos"] = [m for m in data["memos"] if m["id"] != memo["id"]]
                    save_data(data)
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REMINDER
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Reminder":
    st.markdown('<div class="section-title">🔔 Reminder</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Jadwalkan pengingat agar tidak ada yang terlewat</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Tambah Reminder Baru", expanded=False):
        with st.form("add_reminder"):
            c1, c2 = st.columns(2)
            with c1:
                rem_title = st.text_input("Judul Reminder *", placeholder="Meeting dengan klien...")
                rem_date = st.date_input("Tanggal", value=date.today())
            with c2:
                rem_note = st.text_area("Catatan", placeholder="Detail reminder...", height=100)
                rem_priority = st.selectbox("Prioritas", ["Tinggi", "Sedang", "Rendah"])
            submitted = st.form_submit_button("🔔 Set Reminder", use_container_width=True, type="primary")
            if submitted and rem_title:
                data["reminders"].append({
                    "id": str(uuid.uuid4())[:8],
                    "title": rem_title,
                    "date": str(rem_date),
                    "note": rem_note,
                    "priority": rem_priority,
                    "done": False
                })
                save_data(data)
                st.success("🔔 Reminder ditambahkan!")
                st.rerun()
    
    st.markdown("---")
    
    reminders = data.get("reminders", [])
    if not reminders:
        st.info("Belum ada reminder. Tambah pengingat pertamamu!")
    else:
        # Sort by date
        reminders_sorted = sorted(reminders, key=lambda x: x.get("date", ""), reverse=False)
        
        today = date.today()
        overdue = [r for r in reminders_sorted if r.get("date") and datetime.strptime(r["date"], "%Y-%m-%d").date() < today and not r.get("done")]
        today_r = [r for r in reminders_sorted if r.get("date") and datetime.strptime(r["date"], "%Y-%m-%d").date() == today and not r.get("done")]
        upcoming = [r for r in reminders_sorted if r.get("date") and datetime.strptime(r["date"], "%Y-%m-%d").date() > today and not r.get("done")]
        done_r = [r for r in reminders_sorted if r.get("done")]
        
        sections = [
            ("⚠️ Terlambat", overdue, "reminder-overdue", "#f76a6a"),
            ("🔔 Hari Ini", today_r, "reminder-today", "#f7e06a"),
            ("📅 Mendatang", upcoming, "reminder-upcoming", "#6af7c5"),
            ("✅ Selesai", done_r, "reminder-upcoming", "#5a5a70"),
        ]
        
        for section_name, section_items, cls, color in sections:
            if section_items:
                st.markdown(f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:0.85rem;color:{color};margin:1rem 0 0.5rem;">{section_name} ({len(section_items)})</div>', unsafe_allow_html=True)
                for rem in section_items:
                    c1, c2, c3 = st.columns([5, 2, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="reminder-card {cls}">
                            <div style="flex:1;">
                                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.88rem;{'text-decoration:line-through;color:var(--text3);' if rem.get('done') else ''}">{rem['title']}</div>
                                {f'<div style="font-size:0.75rem;color:var(--text3);margin-top:2px;">{rem["note"]}</div>' if rem.get('note') else ''}
                                <div style="font-size:0.7rem;color:var(--text3);margin-top:4px;">📅 {rem['date']} &nbsp;·&nbsp; <span style="color:{color};">{rem.get('priority','')}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        if not rem.get("done"):
                            if st.button("✓ Done", key=f"done_rem_{rem['id']}", use_container_width=True):
                                for r in data["reminders"]:
                                    if r["id"] == rem["id"]:
                                        r["done"] = True
                                save_data(data)
                                st.rerun()
                    with c3:
                        if st.button("🗑", key=f"del_rem_{rem['id']}", use_container_width=True):
                            data["reminders"] = [r for r in data["reminders"] if r["id"] != rem["id"]]
                            save_data(data)
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CHECKLIST
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Checklist":
    st.markdown('<div class="section-title">✅ Checklist & Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Buat checklist untuk berbagai proyek dan pantau progressnya</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Buat Checklist Baru", expanded=False):
        with st.form("add_checklist"):
            cl_title = st.text_input("Nama Checklist *", placeholder="Sprint 1 Tasks, Persiapan Meeting...")
            cl_items_text = st.text_area("Item Checklist (satu per baris)", placeholder="Buat desain mockup\nCode implementasi\nUjicoba fitur\nDeploy ke staging", height=120)
            cl_color = st.selectbox("Warna Tema", ["Ungu", "Kuning", "Hijau", "Merah"])
            submitted = st.form_submit_button("✅ Buat Checklist", use_container_width=True, type="primary")
            if submitted and cl_title and cl_items_text.strip():
                items = []
                for line in cl_items_text.strip().split("\n"):
                    if line.strip():
                        items.append({"id": str(uuid.uuid4())[:8], "text": line.strip(), "done": False})
                data["checklists"].append({
                    "id": str(uuid.uuid4())[:8],
                    "title": cl_title,
                    "items": items,
                    "color": cl_color,
                    "created": str(date.today())
                })
                save_data(data)
                st.success("✅ Checklist dibuat!")
                st.rerun()
    
    st.markdown("---")
    
    checklists = data.get("checklists", [])
    if not checklists:
        st.info("Belum ada checklist. Buat checklist pertamamu!")
    else:
        color_map = {"Ungu": "#7c6af7", "Kuning": "#f7c56a", "Hijau": "#6af7c5", "Merah": "#f76a8f"}
        
        for cl in checklists:
            total_items = len(cl["items"])
            done_items = sum(1 for i in cl["items"] if i["done"])
            pct = int((done_items / total_items) * 100) if total_items > 0 else 0
            p_color = progress_color(pct)
            cl_color_val = color_map.get(cl.get("color", "Ungu"), "#7c6af7")
            
            with st.container():
                st.markdown(f"""
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1rem;border-left:3px solid {cl_color_val};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
                        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1rem;">{cl['title']}</div>
                        <div style="font-size:1.5rem;font-family:'Syne',sans-serif;font-weight:800;color:{p_color};">{pct}%</div>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:var(--text3);margin-bottom:6px;">
                        <span>✓ {done_items} dari {total_items} item selesai</span>
                        <span>📅 {cl.get('created','')}</span>
                    </div>
                    <div class="progress-wrap" style="height:8px;">
                        <div class="progress-fill" style="width:{pct}%;background:linear-gradient(90deg,{cl_color_val},{p_color});"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Checklist items
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    for item in cl["items"]:
                        checked = st.checkbox(
                            item["text"],
                            value=item["done"],
                            key=f"cl_{cl['id']}_{item['id']}"
                        )
                        if checked != item["done"]:
                            for checklist in data["checklists"]:
                                if checklist["id"] == cl["id"]:
                                    for it in checklist["items"]:
                                        if it["id"] == item["id"]:
                                            it["done"] = checked
                            save_data(data)
                            st.rerun()
                
                with c_right:
                    # Add item
                    new_item = st.text_input("Tambah item", key=f"new_item_{cl['id']}", placeholder="Item baru...")
                    if st.button("➕ Tambah", key=f"add_item_{cl['id']}", use_container_width=True):
                        if new_item.strip():
                            for checklist in data["checklists"]:
                                if checklist["id"] == cl["id"]:
                                    checklist["items"].append({"id": str(uuid.uuid4())[:8], "text": new_item.strip(), "done": False})
                            save_data(data)
                            st.rerun()
                    
                    if st.button("🗑 Hapus List", key=f"del_cl_{cl['id']}", use_container_width=True):
                        data["checklists"] = [c for c in data["checklists"] if c["id"] != cl["id"]]
                        save_data(data)
                        st.rerun()
                    
                    if pct == 100:
                        st.markdown('<div style="text-align:center;font-size:1.5rem;margin-top:0.5rem;">🎉</div>', unsafe_allow_html=True)
                
                st.markdown("---")
