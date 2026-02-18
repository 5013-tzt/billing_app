"""
reset_data.py
=============
billing_system.db ထဲက နမူနာ data အားလုံးကို ရှင်းထုတ်မယ်။
Structure (tables) တွေကိုတော့ မထိဘဲ data ပဲဖျက်မယ်။

Run နည်း:
    python reset_data.py
"""

import sqlite3
import os

# ── Database path ── သင့် project folder နဲ့ညှိပါ ──────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'billing_system.db')


def reset_all_data():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database မတွေ့ဘူး: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ── ဖျက်ခင် count ကြည့်မယ် ──────────────────────────────────────────────
    tables = ['invoice_items', 'invoices', 'clients', 'companies']
    print("=" * 45)
    print("  ဖျက်ခင် record အရေအတွက်")
    print("=" * 45)
    for t in tables:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<20} : {n} rows")
        except Exception as e:
            print(f"  {t:<20} : Error — {e}")

    print()
    confirm = input("⚠️  Data အားလုံးဖျက်မှာ သေချာပါသလား? (yes / no) : ").strip().lower()
    if confirm != 'yes':
        print("❌ ဖျက်ခြင်း ပယ်ဖျက်လိုက်သည်။")
        conn.close()
        return

    print()

    # ── FK constraint ကို ယာယီပိတ်ပြီး ဖျက်မယ် ─────────────────────────────
    c.execute("PRAGMA foreign_keys = OFF")

    delete_order = ['invoice_items', 'invoices', 'clients', 'companies']
    for t in delete_order:
        try:
            c.execute(f"DELETE FROM {t}")
            print(f"  ✅ {t} — ရှင်းပြီး")
        except Exception as e:
            print(f"  ❌ {t} — Error: {e}")

    # ── Auto-increment ID တွေ reset ──────────────────────────────────────────
    for t in delete_order:
        try:
            c.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
        except:
            pass  # sqlite_sequence မရှိရင် ကိုယ်ပဲ ignore

    c.execute("PRAGMA foreign_keys = ON")

    # ── Settings ကိုတော့ default ပြန်ထားမယ် (မဖျက်ဘူး) ─────────────────────
    try:
        existing = c.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
        if existing == 0:
            c.execute("""
                INSERT INTO settings (id, admin_name, admin_user, password)
                VALUES (1, 'Administrator', 'admin', '1234')
            """)
            print("  ✅ settings — default ပြန်ထည့်ပြီး")
        else:
            print("  ℹ️  settings — မထိဘဲထား (login info ကျန်ရစ်)")
    except Exception as e:
        print(f"  ❌ settings — {e}")

    conn.commit()
    conn.close()

    print()
    print("=" * 45)
    print("  ✅ Data ရှင်းထုတ်ခြင်း အောင်မြင်သည်။")
    print("  Tables structure တွေ ပျက်မသွားဘဲ data ပဲဖျက်ပြီး")
    print("  Settings (login) ကို မထိဘဲ ထားသည်။")
    print("=" * 45)


if __name__ == '__main__':
    reset_all_data()
