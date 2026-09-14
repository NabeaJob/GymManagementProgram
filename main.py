import database

def main():
    database.init_db()
    while True:
        print("\n==============================")
        print("    IRON PULSE GYM MANAGER    ")
        print("==============================")
        print("1. Add New Member")
        print("2. List All Members")
        print("3. Log Member Attendance")
        print("4. Schedule PT Session")
        print("5. View PT Schedule")
        print("6. Run Monthly Billing Batch")
        print("7. View Invoices Ledger")
        print("8. Pay Open Invoice")
        print("9. Exit Application")
        
        choice = input("\nSelect an option (1-9): ").strip()
        
        if choice == "1":
            name = input("Enter Member Name: ").strip()
            email = input("Enter Email Address: ").strip()
            phone = input("Enter Phone Number: ").strip()
            if name and email and phone:
                success, msg = database.add_member(name, email, phone)
                print(f"\n[{'✔' if success else '✖'}] {msg}")
            else:
                print("\n[✖] Cancelled: Fields cannot be blank.")
                
        elif choice == "2":
            members = database.get_all_members()
            print("\n--- GYM MEMBERS ---")
            print(f"{'ID':<5}{'Name':<20}{'Email':<30}{'Status':<10}")
            print("-" * 65)
            for m in members:
                print(f"{m[0]:<5}{m[1]:<20}{m[2]:<30}{m[3]:<10}")
                
        elif choice == "3":
            try:
                m_id = int(input("Enter Member ID: "))
                success, msg = database.log_attendance(m_id)
                print(f"\n[{'✔' if success else '✖'}] {msg}")
            except ValueError:
                print("\n[✖] Invalid Input: Numerical IDs only.")
                
        elif choice == "4":
            try:
                m_id = int(input("Enter Member ID: "))
                trainer = input("Trainer Name: ").strip()
                date_input = input("Date (YYYY-MM-DD): ").strip()
                time_input = input("Time (HH:MM): ").strip()
                if trainer and date_input and time_input:
                    success, msg = database.schedule_pt(m_id, trainer, date_input, time_input)
                    print(f"\n[{'✔' if success else '✖'}] {msg}")
                else:
                    print("\n[✖] Cancelled: Fields cannot be blank.")
            except ValueError:
                print("\n[✖] Invalid Input: Numerical IDs only.")
                
        elif choice == "5":
            sessions = database.get_upcoming_pt_sessions()
            print("\n--- UPCOMING PT SESSIONS ---")
            print(f"{'ID':<5}{'Member':<20}{'Trainer':<15}{'Date & Time':<20}")
            print("-" * 60)
            for s in sessions:
                print(f"{s[0]:<5}{s[1]:<20}{s[2]:<15}{s[3]:<20}")
                
        elif choice == "6":
            rate = input("Base subscription rate (Press Enter for default $50.00): ").strip()
            rate_val = 50.0 if rate == "" else float(rate)
            count = database.run_monthly_billing(rate_val)
            print(f"\n[✔] Billing Engine: Generated {count} new statement(s).")
                    
        elif choice == "7":
            invoices = database.get_invoices()
            print("\n--- BILLING AND INVOICES ---")
            print(f"{'Inv ID':<8}{'Member':<20}{'Amount':<10}{'Due Date':<15}{'Status':<10}")
            print("-" * 65)
            for inv in invoices:
                print(f"{inv[0]:<8}{inv[1]:<20}${inv[2]:<9.2f}{inv[3]:<15}{inv[4]:<10}")
                
        elif choice == "8":
            try:
                inv_id = int(input("Enter Invoice ID to pay: "))
                success, msg = database.collect_payment(inv_id)
                print(f"\n[{'✔' if success else '✖'}] {msg}")
            except ValueError:
                print("\n[✖] Invalid Input: Numerical IDs only.")
                
        elif choice == "9":
            print("\nExiting System. Goodbye!")
            break

if __name__ == "__main__":
    main()
