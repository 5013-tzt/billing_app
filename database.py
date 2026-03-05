import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'billing_system.db')

def get_db():
    """Database connection ရယူမယ်"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Database ကိုစတင်ပြင်ဆင်မယ်"""
    conn = get_db()
    
    # Clients table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            abbr TEXT,
            addr1 TEXT,
            addr2 TEXT,
            addr3 TEXT,
            c1_name TEXT,
            c1_pos TEXT,
            c1_ph TEXT,
            c1_em TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Companies table (Mother Companies)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            tax_number TEXT,
            logo TEXT,
            is_default INTEGER DEFAULT 0,
            bank_name TEXT DEFAULT '',
            beneficiary TEXT DEFAULT '',
            account_no TEXT DEFAULT '',
            kpay_no TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migration: existing companies table မှာ payment columns မရှိရင် ထည့်
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(companies)")
    company_cols = [col[1] for col in cursor.fetchall()]
    
    payment_cols = {
        'bank_name':   "ALTER TABLE companies ADD COLUMN bank_name   TEXT DEFAULT ''",
        'beneficiary': "ALTER TABLE companies ADD COLUMN beneficiary TEXT DEFAULT ''",
        'account_no':  "ALTER TABLE companies ADD COLUMN account_no  TEXT DEFAULT ''",
        'kpay_no':     "ALTER TABLE companies ADD COLUMN kpay_no     TEXT DEFAULT ''",
        'website':     "ALTER TABLE companies ADD COLUMN website     TEXT DEFAULT ''",
    }
    for col, sql in payment_cols.items():
        if col not in company_cols:
            print(f"Adding {col} column to companies table...")
            try:
                cursor.execute(sql)
            except Exception as e:
                print(f"{col} may already exist: {e}")

    # First, check existing columns in invoices table
    cursor.execute("PRAGMA table_info(invoices)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Create invoices table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE,
            invoice_date TEXT,
            client_id INTEGER,
            mother_company_id INTEGER,
            company_name TEXT,
            address TEXT,
            contact_name TEXT,
            contact_pos TEXT,
            contact_ph TEXT,
            contact_email TEXT,
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            advance REAL DEFAULT 0,
            grand_total REAL DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            inv_title TEXT DEFAULT '',
            service_type TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (mother_company_id) REFERENCES companies (id)
        )
    ''')
    
    if 'inv_title' not in column_names:
        print("Adding inv_title column to invoices table...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN inv_title TEXT DEFAULT ''")
        except:
            print("inv_title column may already exist")
    
    if 'service_type' not in column_names:
        print("Adding service_type column to invoices table...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN service_type TEXT DEFAULT ''")
        except:
            print("service_type column may already exist")

    if 'paid_date' not in column_names:
        print("Adding paid_date column to invoices table...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN paid_date TEXT DEFAULT NULL")
        except:
            print("paid_date column may already exist")

    if 'payment_method' not in column_names:
        print("Adding payment_method column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN payment_method TEXT DEFAULT ''")
        except:
            print("payment_method may already exist")

    if 'payment_note' not in column_names:
        print("Adding payment_note column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN payment_note TEXT DEFAULT ''")
        except:
            print("payment_note may already exist")

    if 'receipt_no' not in column_names:
        print("Adding receipt_no column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN receipt_no TEXT DEFAULT ''")
        except:
            print("receipt_no may already exist")

    if 'inv_type' not in column_names:
        print("Adding inv_type column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN inv_type TEXT DEFAULT 'Monthly'")
        except:
            print("inv_type may already exist")

    if 'use_work_days' not in column_names:
        print("Adding use_work_days column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN use_work_days INTEGER DEFAULT 0")
        except:
            print("use_work_days may already exist")

    if 'advance_text' not in column_names:
        print("Adding advance_text column...")
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN advance_text TEXT DEFAULT ''")
        except:
            print("advance_text may already exist")
    
    # Invoice items table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            description TEXT,
            qty INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0,
            amount REAL DEFAULT 0,
            days REAL DEFAULT 0,
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')

    # Migration: invoice_items မှာ days/start_date/end_date မရှိရင် ထည့်
    cursor.execute("PRAGMA table_info(invoice_items)")
    item_cols = [col[1] for col in cursor.fetchall()]
    for col, sql in [
        ('days',       "ALTER TABLE invoice_items ADD COLUMN days REAL DEFAULT 0"),
        ('start_date', "ALTER TABLE invoice_items ADD COLUMN start_date TEXT DEFAULT ''"),
        ('end_date',   "ALTER TABLE invoice_items ADD COLUMN end_date TEXT DEFAULT ''"),
    ]:
        if col not in item_cols:
            try: cursor.execute(sql)
            except: pass
    
    # Settings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_name TEXT,
            admin_user TEXT,
            password TEXT,
            theme TEXT DEFAULT 'dark'
        )
    ''')
    
    # === Theme preference migration ===
    cursor.execute("PRAGMA table_info(settings)")
    settings_cols = [col[1] for col in cursor.fetchall()]
    
    if 'theme' not in settings_cols:
        print("Adding theme column to settings table...")
        try:
            cursor.execute("ALTER TABLE settings ADD COLUMN theme TEXT DEFAULT 'dark'")
        except Exception as e:
            print(f"theme column may already exist: {e}")
    
    settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    if not settings:
        conn.execute('''
            INSERT INTO settings (id, admin_name, admin_user, password, theme)
            VALUES (1, 'Administrator', 'admin', '1234', 'light')
        ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def get_theme_preference():
    """Get user's theme preference from database"""
    try:
        conn = get_db()
        result = conn.execute("SELECT theme FROM settings WHERE id=1").fetchone()
        conn.close()
        return result['theme'] if result and result['theme'] else 'light'
    except:
        return 'light'


def set_theme_preference(theme_name):
    """Save user's theme preference to database"""
    try:
        conn = get_db()
        conn.execute("UPDATE settings SET theme=? WHERE id=1", (theme_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving theme preference: {e}")
        return False


if __name__ == '__main__':
    init_db()