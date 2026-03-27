import io
import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docxtpl import DocxTemplate

DB_PATH = "clients.db"
TEMPLATE_PATH = "execution_petition_TEMPLATE.docx"

st.set_page_config(
    page_title="Execution Petition Manager",
    page_icon="⚖️",
    layout="wide",
)

# Visible stamp so you know Streamlit Cloud is running the latest commit
st.info("APP VERSION: 2026-03-27 v4 — form_submit_button present")


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE,
                petitioner_name TEXT,
                petitioner_address TEXT,
                respondent_name TEXT,
                respondent_address TEXT,
                marriage_date TEXT,
                decree_date TEXT,
                children_info TEXT,
                decree_amount TEXT,
                court_costs TEXT,
                execution_mode TEXT,
                filing_deadline TEXT,
                prepared_by TEXT,
                status TEXT DEFAULT "Active"
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def load_clients(search: str = "") -> pd.DataFrame:
    conn = get_connection()
    try:
        if search:
            query = """
            SELECT * FROM clients
            WHERE petitioner_name LIKE ?
               OR respondent_name LIKE ?
               OR case_number LIKE ?
               OR status LIKE ?
            """
            s = f"%{search}%"
            return pd.read_sql_query(query, conn, params=(s, s, s, s))
        return pd.read_sql_query(
            "SELECT * FROM clients ORDER BY filing_deadline ASC", conn
        )
    finally:
        conn.close()


def add_client(data: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO clients
                (case_number, petitioner_name, petitioner_address, respondent_name,
                 respondent_address, marriage_date, decree_date, children_info,
                 decree_amount, court_costs, execution_mode, filing_deadline,
                 prepared_by, status)
            VALUES
                (:case_number, :petitioner_name, :petitioner_address, :respondent_name,
                 :respondent_address, :marriage_date, :decree_date, :children_info,
                 :decree_amount, :court_costs, :execution_mode, :filing_deadline,
                 :prepared_by, :status)
            """,
            data,
        )
        conn.commit()
    finally:
        conn.close()


def delete_client(case_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM clients WHERE id=?", (case_id,))
        conn.commit()
    finally:
        conn.close()


def ensure_template() -> None:
    if os.path.exists(TEMPLATE_PATH):
        return

    doc = Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(11)

    title = doc.add_heading("EXECUTION PETITION", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    court = doc.add_paragraph("IN THE FAMILY COURT")
    court.alignment = WD_ALIGN_PARAGRAPH.CENTER

    case_no = doc.add_paragraph("Case No: {{case_number}}")
    case_no.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("")
    doc.add_heading("PARTIES", level=1)

    p = doc.add_paragraph()
    p.add_run("Decree Holder (Petitioner): ").bold = True
    p.add_run("{{petitioner_name}}, residing at {{petitioner_address}}")

    r = doc.add_paragraph()
    r.add_run("Judgment Debtor (Respondent): ").bold = True
    r.add_run("{{respondent_name}}, residing at {{respondent_address}}")

    doc.add_paragraph("")
    doc.add_heading("PARTICULARS OF EXECUTION", level=1)

    table = doc.add_table(rows=10, cols=2)
    table.style = "Table Grid"

    rows_data = [
        ("1.  Case Number", "{{case_number}}"),
        ("2.  Petitioner vs Respondent", "{{petitioner_name}} vs {{respondent_name}}"),
        ("3.  Date of Marriage", "{{marriage_date}}"),
        ("4.  Date of Divorce Decree", "{{decree_date}}"),
        ("5.  Children", "{{children_info}}"),
        ("6.  Relief / Amount Granted", "{{decree_amount}}"),
        ("7.  Court Costs Allowed", "{{court_costs}}"),
        ("8.  Execution Against", "{{respondent_name}}"),
        ("9.  Mode of Execution", "{{execution_mode}}"),
        ("10. Filing Deadline", "{{filing_deadline}}"),
    ]

    for i, (label, value) in enumerate(rows_data):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value
        if row.cells[0].paragraphs and row.cells[0].paragraphs[0].runs:
            row.cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph("")
    doc.add_heading("PRAYER", level=1)
    doc.add_paragraph(
        "The Decree Holder respectfully requests that this Hon'ble Court execute the "
        "order dated {{decree_date}} against {{respondent_name}} and provide all necessary assistance."
    )

    doc.add_paragraph("")
    doc.add_paragraph("Date: {{today_date}}")
    doc.add_paragraph("Prepared by: {{prepared_by}}")

    doc.add_paragraph("")
    doc.add_paragraph("_" * 40)
    doc.add_paragraph("Signature of Decree Holder / Authorized Representative")

    doc.save(TEMPLATE_PATH)


def generate_doc(case: dict) -> bytes:
    ensure_template()
    tpl = DocxTemplate(TEMPLATE_PATH)

    context = {k: (v if v not in (None, "") else "-") for k, v in case.items()}
    context["today_date"] = str(date.today())

    tpl.render(context)
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)
    return buf.read()


init_db()
ensure_template()

st.sidebar.title("⚖️ Petition Manager")
page = st.sidebar.radio(
    "Navigate",
    ["📋 Client Table", "➕ Add New Case", "📄 Generate Document"],
)

if page == "📋 Client Table":
    st.title("📋 Client Case Table")
    search = st.text_input("🔍 Search by name, case number, or status", "")
    df = load_clients(search)

    if df.empty:
        st.info("No clients found. Add a new case from the sidebar.")
    else:
        today = date.today()

        def urgency(deadline_str: str) -> str:
            try:
                d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                diff = (d - today).days
                if diff < 0:
                    return "🔴 OVERDUE"
                if diff <= 2:
                    return "🔴 Urgent"
                if diff <= 7:
                    return "🟠 This Week"
                return "🔵 On Track"
            except Exception:
                return "—"

        df["⏳ Urgency"] = df["filing_deadline"].apply(urgency)
        st.dataframe(df, use_container_width=True, hide_index=True)

        with st.expander("🗑️ Delete a Case"):
            case_ids = df[["id", "case_number", "petitioner_name"]].copy()
            case_ids["label"] = (
                case_ids["case_number"] + " – " + case_ids["petitioner_name"]
            )
            chosen = st.selectbox("Select case to delete", case_ids["label"].tolist())
            if st.button("Delete Selected Case", type="secondary"):
                cid = case_ids[case_ids["label"] == chosen]["id"].values[0]
                delete_client(int(cid))
                st.success(f"Deleted: {chosen}")
                st.rerun()

elif page == "➕ Add New Case":
    st.title("➕ Add New Client Case")

    with st.form("new_case_form", clear_on_submit=True):
        case_number = st.text_input("Case Number *")
        prepared_by = st.text_input("Prepared By *")
        status = st.selectbox("Status", ["Active", "Completed", "On Hold"])
        filing_deadline = st.date_input("Filing Deadline *", min_value=date.today())

        petitioner_name = st.text_input("Petitioner Name *")
        petitioner_address = st.text_input("Petitioner Address *")
        respondent_name = st.text_input("Respondent Name *")
        respondent_address = st.text_input("Respondent Address *")

        marriage_date = st.date_input("Date of Marriage")
        decree_date = st.date_input("Date of Divorce Decree")

        children_info = st.text_input("Children Info")
        decree_amount = st.text_input("Relief / Amount Granted")
        court_costs = st.text_input("Court Costs Allowed")
        execution_mode = st.selectbox(
            "Mode of Execution",
            [
                "Salary Attachment",
                "Bank Account Garnishment",
                "Property Attachment",
                "Other",
            ],
        )

        # IMPORTANT: submit button must be INSIDE the form
        submitted = st.form_submit_button("💾 Save Case", type="primary")

    if submitted:
        if not all([case_number, petitioner_name, respondent_name, prepared_by]):
            st.error("Please fill in all required (*) fields.")
        else:
            try:
                add_client(
                    {
                        "case_number": case_number,
                        "petitioner_name": petitioner_name,
                        "petitioner_address": petitioner_address,
                        "respondent_name": respondent_name,
                        "respondent_address": respondent_address,
                        "marriage_date": str(marriage_date),
                        "decree_date": str(decree_date),
                        "children_info": children_info,
                        "decree_amount": decree_amount,
                        "court_costs": court_costs,
                        "execution_mode": execution_mode,
                        "filing_deadline": str(filing_deadline),
                        "prepared_by": prepared_by,
                        "status": status,
                    }
                )
                st.success(f"✅ Case {case_number} saved successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "📄 Generate Document":
    st.title("📄 Generate Execution Petition")
    df = load_clients()

    if df.empty:
        st.warning("No cases in the database. Please add a case first.")
    else:
        df["label"] = (
            df["case_number"]
            + " — "
            + df["petitioner_name"]
            + " vs "
            + df["respondent_name"]
        )
        selected_label = st.selectbox("Select a case:", df["label"].tolist())
        selected_row = df[df["label"] == selected_label].iloc[0].to_dict()

        if st.button("⬇️ Generate & Download Document", type="primary"):
            with st.spinner("Generating document..."):
                doc_bytes = generate_doc(selected_row)

            filename = f"petition_{str(selected_row['case_number']).replace('-', '_')}.docx"
            st.download_button(
                label="📥 Click here to download",
                data=doc_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            st.success(f"✅ Document ready: {filename}")
