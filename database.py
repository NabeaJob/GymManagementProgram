import sqlite3
from datetime import datetime, timedelta

DB_NAME = "gym_management.db"

def init_db():
    """Initializes the SQLite database schemas."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Members Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                membership_status TEXT DEFAULT 'Active',
                join_date TEXT NOT NULL
            )
        """)
        
        # Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                check_in_time TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)
        
        # Personal Training Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pt_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                trainer_name TEXT NOT NULL,
                session_datetime TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)
        
        # Billing Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'Unpaid',
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def add_member(name, email, phone):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            join_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO members (name, email, phone, join_date) VALUES (?, ?, ?, ?)",
                (name, email, phone, join_date)
            )
            conn.commit()
            return True, f"Member '{name}' registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Error: A member with this email already exists."

def get_all_members():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, membership_status FROM members")
        return cursor.fetchall()

def log_attendance(member_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, membership_status FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return False, "Error: Member ID not found."
        if member[1] != 'Active':
            return False, f"Warning: Member '{member[0]}' is currently Inactive."

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO attendance (member_id, check_in_time) VALUES (?, ?)", (member_id, now))
        conn.commit()
        return True, f"Checked-in: '{member[0]}' logged at {now}."

def schedule_pt(member_id, trainer_name, date_str, time_str):
    try:
        session_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return False, "Error: Invalid format. Use YYYY-MM-DD for date and HH:MM for time."

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM members WHERE id = ?", (member_id,))
        if not cursor.fetchone():
            return False, "Error: Member ID not found."

        cursor.execute(
            "INSERT INTO pt_sessions (member_id, trainer_name, session_datetime) VALUES (?, ?, ?)",
            (member_id, trainer_name, session_datetime.strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        return True, f"PT Session booked with Coach {trainer_name}."

def get_upcoming_pt_sessions():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pt.id, m.name, pt.trainer_name, pt.session_datetime 
            FROM pt_sessions pt
            JOIN members m ON pt.member_id = m.id
            WHERE pt.session_datetime >= datetime('now') AND pt.status = 'Scheduled'
            ORDER BY pt.session_datetime ASC
        """)
        return cursor.fetchall()

def run_monthly_billing(base_rate=50.0):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM members WHERE membership_status = 'Active'")
        active_members = cursor.fetchall()
        
        if not active_members:
            return 0
            
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        generated_count = 0
        
        for member in active_members:
            cursor.execute(
                "SELECT id FROM billing WHERE member_id = ? AND due_date = ? AND status = 'Unpaid'", 
                (member[0], due_date)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO billing (member_id, amount, due_date) VALUES (?, ?, ?)",
                    (member[0], base_rate, due_date)
                )
                generated_count += 1
                
        conn.commit()
        return generated_count

def get_invoices():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, m.name, b.amount, b.due_date, b.status 
            FROM billing b
            JOIN members m ON b.member_id = m.id
            ORDER BY b.due_date ASC
        """)
        return cursor.fetchall()

def collect_payment(invoice_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM billing WHERE id = ?", (invoice_id,))
        if not cursor.fetchone():
            return False, "Error: Invoice ID not found."
            
        cursor.execute("UPDATE billing SET status = 'Paid' WHERE id = ?", (invoice_id,))
        conn.commit()
        return True, f"Invoice #{invoice_id} marked as PAID."
