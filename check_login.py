"""
check_login.py
==============
Login credentials ကို စစ်ဆေးပြီး လိုအပ်ရင် reset လုပ်မယ်။
Project folder မှာ run ပါ: python check_login.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'billing_system.db')

def check_and_fix():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database မတွေ့ဘူး: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()

    print("=" * 40)
    print("  လက်ရှိ Login Info")
    print("=" * 40)
    if row:
        print(f"  Display Name : {row['admin_name']}")
        print(f"  Username     : {row['admin_user']}")
        print(f"  Password     : {row['password']}")
    else:
        print("  ❌ Settings row မတွေ့ဘူး!")
    print("=" * 40)
    print()

    ans = input("Password ကို '1234' လို့ reset လုပ်မလား? (yes/no): ").strip().lower()
    if ans == 'yes':
        if row:
            conn.execute(
                "UPDATE settings SET admin_user='admin', password='1234' WHERE id=1"
            )
        else:
            conn.execute(
                "INSERT INTO settings (id, admin_name, admin_user, password) VALUES (1,'Administrator','admin','1234')"
            )
        conn.commit()
        print()
        print("✅ Reset လုပ်ပြီး!")
        print("   Username : admin")
        print("   Password : 1234")
    else:
        print("❌ ပယ်ဖျက်လိုက်သည်။")

    conn.close()

if __name__ == '__main__':
    check_and_fix()
