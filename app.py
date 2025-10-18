from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json, os, datetime, time

app = Flask(__name__)
app.secret_key = "your_secret_key"

# --- File Paths ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

EMP_FILE = os.path.join(DATA_DIR, "employees.json")
ATT_FILE = os.path.join(DATA_DIR, "attendance.json")
SALARY_FILE = os.path.join(DATA_DIR, "salary.json")
LEAVE_FILE = os.path.join(DATA_DIR, "leaves.json")
TIME_FILE = "data/time.json"
LEAVES_FILE = "leaves.json"


# ---------- Helper functions ----------
def load_leaves():
    if os.path.exists(LEAVES_FILE):
        with open(LEAVES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_leaves(leaves):
    with open(LEAVES_FILE, "w") as f:
        json.dump(leaves, f, indent=4)



#=============== TIME MANAGEMENT ================
def load_time_data():
    if not os.path.exists(TIME_FILE):
        return []
    with open(TIME_FILE, "r") as f:
        return json.load(f)

def save_time_data(data):
    with open(TIME_FILE, "w") as f:
        json.dump(data, f, indent=4)

#================ LEAVE MANAGEMENT ==================
def load_leaves():
    """Load all leaves from JSON file."""
    if not os.path.exists(LEAVE_FILE):
        return []
    with open(LEAVE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_leaves(leaves):
    """Save all leaves to JSON file."""
    with open(LEAVE_FILE, "w") as f:
        json.dump(leaves, f, indent=4)

# --- Helper Functions ---
def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=4)
    else:
        try:
            with open(path, "r") as f:
                json.load(f)
        except Exception:
            with open(path, "w") as f:
                json.dump(default, f, indent=4)

def load_json(path):
    ensure_file(path, [])
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_employees():
    return load_json(EMP_FILE)

def save_employees(employees):
    save_json(EMP_FILE, employees)

# Ensure files exist
ensure_file(EMP_FILE, [])
ensure_file(ATT_FILE, [])
ensure_file(SALARY_FILE, [])
ensure_file(LEAVE_FILE, [])

# === Mark Attendance ===
def mark_attendance(emp_id):
    attendance = load_json(ATT_FILE)
    today = str(datetime.date.today())
    emp_record = next((item for item in attendance if item.get("id") == emp_id), None)
    if not emp_record:
        emp_record = {"id": emp_id, "records": {}}
        attendance.append(emp_record)
    if today not in emp_record["records"]:
        emp_record["records"][today] = {"status": "Present", "hours": 0}
    save_json(ATT_FILE, attendance)

# ================== ROUTES ===================
@app.route("/")
def home():
    return render_template("index.html")

# ================== EMPLOYEE LOGIN ===================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        employees = load_employees()
        emp = next(
            (e for e in employees if e.get("email") == email and e.get("password") == password and e.get("role") == "employee"),
            None
        )

        if emp:
            session["employee_id"] = emp.get("id")
            session["employee"] = {"id": emp.get("id"), "name": emp.get("name")}
            session["login_time"] = time.time()  # record login time

            mark_attendance(emp.get("id"), emp.get("name"))
            return redirect(url_for("employee_dashboard"))
        else:
            flash("Invalid email or password!", "error")

    # GET request or failed login
    return render_template("login.html")



# ================== ADMIN LOGIN ===================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        employees = load_employees()  # using your load_employees helper
        admin = next(
            (
                emp for emp in employees
                if emp.get("role") == "admin"
                and emp.get("username") == username
                and emp.get("email") == email
                and emp.get("password") == password
            ),
            None
        )
        if admin:
            # Store only essential info in session
            session["admin_user"] = {
                "id": admin.get("id"),
                "username": admin.get("username"),
                "role": "admin"
            }
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials!", "error")
    return render_template("admin_login.html")


# ================== ADMIN DASHBOARD ===================
@app.route("/admin")
def admin_dashboard():
    user = session.get("admin_user")
    if not user or user.get("role") != "admin":
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html", admin_username=user.get("username"))

# ================== EMPLOYEE DASHBOARD ===================

@app.route("/employee/dashboard")
def employee_dashboard():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    emp_id = session["employee_id"]
    emp_name = session["employee"]["name"]

    # Mark attendance once per day
    mark_attendance(emp_id, emp_name)

    # Load employee and attendance
    employees = load_employees()
    emp = next((e for e in employees if e.get("id") == emp_id), {})
    attendance = load_attendance()
    emp_att = next((a.get("records", {}) for a in attendance if a.get("id") == emp_id), {})

    today = datetime.date.today()  # pass today's date
    
    leaves = load_leaves()  # ✅ load leave requests

    return render_template(
        "employee_dashboard.html",
        employee=emp,
        attendance=emp_att,
        today=today,
        leaves=leaves
    )

#====================== EMPLOYEE LOGOUT =======================
@app.route("/employee/logout")
def employee_logout():
    if "employee_id" in session:
        emp_id = session["employee_id"]
        emp_name = session.get("employee", {}).get("name", "Unknown")
        login_time = session.get("login_time")

        if login_time:
            logout_time = time.time()
            total_seconds = int(logout_time - login_time)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            data = load_time_data()
            data.append({
                "id": emp_id,
                "name": emp_name,
                "login_time": datetime.datetime.fromtimestamp(login_time).strftime("%Y-%m-%d %H:%M:%S"),
                "logout_time": datetime.datetime.fromtimestamp(logout_time).strftime("%Y-%m-%d %H:%M:%S"),
                "worked_hours": f"{hours}h {minutes}m"
            })
            save_time_data(data)

    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for("home"))


# ================== REGISTER EMPLOYEE ===================
@app.route("/register_employee", methods=["GET", "POST"])
def register_employee():
    employees = load_employees()
    
    if request.method == "POST":
        # get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        
        # generate a unique ID
        emp_id = f"EMP{len(employees)+1:03d}"

        # create new employee dict
        new_employee = {
            "id": emp_id,
            "name": name,
            "email": email,
            "password": password,
            "address": address,
            "phone": phone,
            "role": "employee"
        }

        employees.append(new_employee)
        save_employees(employees)
        
        # flash message for admin
        flash(f"Employee '{name}' added successfully!", "success")


        # redirect back to admin dashboard
        return redirect(url_for("admin_dashboard"))

    # GET request returns the registration form
    return render_template("register_employee.html")



#======================= FORGOT PASSWORD =================== 
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        employees = load_json(EMP_FILE)
        emp = next((e for e in employees if e.get("email") == email), None)
        if emp:
            flash(f"Your password is: {emp.get('password')}", "info")
        else:
            flash("Email not found!", "error")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


#========================== DELETE EMPLOYEE ===================
@app.route("/delete_employee", methods=["POST"])
def delete_employee():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    emp_id = request.form.get("emp_id")
    employees = load_employees()

    emp = next((e for e in employees if e.get("id") == emp_id), None)
    if emp:
        employees = [e for e in employees if e.get("id") != emp_id]
        save_employees(employees)
        flash(f"Employee {emp.get('name', emp_id)} deleted successfully.", "success")
    else:
        flash(f"Employee {emp_id} not found!", "error")

    return redirect(url_for("delete_employee_page"))


#======================== DELETE EMPLOYEE PAGE ====================
@app.route("/delete_employee_page")
def delete_employee_page():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    employees = load_employees()  # load all employees
    return render_template("delete_employee.html", employees=employees)


# ================== EMPLOYEE LIST PAGE ===================
@app.route("/employee_list")
def employee_list():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    employees = load_employees()  # load all employees
    total_employees = len(employees)
    return render_template("employee_list.html", employees=employees, total_employees=total_employees)


# ================== EDIT EMPLOYEE LIST ===================
@app.route("/edit_employee_list")
def edit_employee_list():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    employees = load_employees()  # Load all employees from JSON
    return render_template("edit_employee_list.html", employees=employees)


# ================== EDIT EMPLOYEE PAGE ===================
@app.route("/edit_employee/<emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    employees = load_employees()
    emp = next((e for e in employees if e.get("id") == emp_id), None)

    if not emp:
        flash("Employee not found!", "error")
        return redirect(url_for("edit_employee_list"))

    if request.method == "POST":
        # Update employee details
        emp["name"] = request.form.get("name", emp.get("name"))
        emp["email"] = request.form.get("email", emp.get("email"))
        emp["phone"] = request.form.get("phone", emp.get("phone"))
        emp["address"] = request.form.get("address", emp.get("address"))

        save_employees(employees)  # Save JSON
        flash(f"Employee '{emp['name']}' edited successfully!", "success")
        return redirect(url_for("edit_employee_list"))

    return render_template("edit_employee.html", emp=emp)



#==================== LOGOUT =====================
@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))  # Go back to homepage



#========================== APPLY LEAVE =======================
@app.route("/employee/apply_leave", methods=["POST"])
def apply_leave():
    if "employee_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("employee_login"))

    emp_id = session["employee_id"]
    emp_name = session["employee"]["name"]

    # match field names from HTML
    start_date = request.form.get("from_date")
    end_date = request.form.get("to_date")
    reason = request.form.get("reason")

    if not start_date or not end_date or not reason:
        flash("All fields are required!", "error")
        return redirect(url_for("employee_dashboard"))

    leaves = load_leaves()
    leaves.append({
        "employee_id": emp_id,
        "name": emp_name,
        "from_date": start_date,
        "to_date": end_date,
        "reason": reason,
        "status": "Pending",
        "applied_on": datetime.datetime.now().strftime("%Y-%m-%d")
    })
    save_leaves(leaves)

    flash("Leave request submitted successfully!", "success")
    return redirect(url_for("employee_dashboard"))


#===================== ADMIN VIEW PAGE ===================
@app.route("/admin/manage_leave")
def manage_leave():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    leaves = load_leaves()
    return render_template("manage_leave.html", leaves=leaves)

# ====================== APPROVE/REJECT =======================
@app.route("/admin/update_leave", methods=["POST"])
def update_leave():
    if "admin_user" not in session:
        flash("Please log in as admin!", "error")
        return redirect(url_for("admin_login"))

    emp_id = request.form.get("emp_id")
    start_date = request.form.get("start_date")
    action = request.form.get("action")  # approve / reject

    leaves = load_leaves()

    for leave in leaves:
        if str(leave.get("employee_id")) == str(emp_id) and leave.get("from_date") == start_date:
            leave["status"] = "Approved" if action == "approve" else "Rejected"
            break

    save_leaves(leaves)
    flash(f"Leave {action}d successfully!", "success")
    return redirect(url_for("manage_leave"))



# ========== ATTENDANCE MANAGEMENT ==========
def load_attendance():
    """Load attendance from JSON file"""
    if not os.path.exists(ATT_FILE):
        return []
    with open(ATT_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_attendance(attendance):
    """Save attendance to JSON file"""
    with open(ATT_FILE, "w") as f:
        json.dump(attendance, f, indent=4)

def mark_attendance(emp_id, emp_name):
    """Mark today's attendance if not already marked"""
    attendance = load_attendance()
    today = str(datetime.date.today())

    emp_record = next((e for e in attendance if e["id"] == emp_id), None)
    if not emp_record:
        emp_record = {"id": emp_id, "name": emp_name, "records": {}}
        attendance.append(emp_record)

    if today not in emp_record["records"]:
        emp_record["records"][today] = "Present"

    save_attendance(attendance)


# ---------- Employee: Apply Leave ----------
@app.route("/employee/apply_leave", methods=["POST"])
def employee_apply_leave():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    emp_id = session["employee_id"]
    emp_name = session["employee"]["name"]  # ✅ get name from session

    data = request.form
    leaves = load_leaves()

    new_leave = {
        "id": len(leaves) + 1,
        "employee_id": emp_id,
        "employee_name": emp_name,  # ✅ fixed here
        "from_date": data.get("from_date"),
        "to_date": data.get("to_date"),
        "reason": data.get("reason"),
        "status": "Pending",
        "applied_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    leaves.append(new_leave)
    save_leaves(leaves)

    flash("Leave request submitted successfully!", "success")
    return redirect(url_for("employee_dashboard"))



# ---------- Admin: View Leave Requests ----------
@app.route("/admin/leaves")
def admin_leaves():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    leaves = load_leaves()
    return render_template("admin_leaves.html", leaves=leaves)


# ---------- Admin: Approve Leave ----------
@app.route("/admin/approve_leave/<int:leave_id>")
def approve_leave(leave_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    leaves = load_leaves()
    for leave in leaves:
        if leave["id"] == leave_id:
            leave["status"] = "Approved"
            break

    save_leaves(leaves)
    flash("Leave approved!", "success")
    return redirect(url_for("admin_leaves"))


# ---------- Admin: Reject Leave ----------
@app.route("/admin/reject_leave/<int:leave_id>")
def reject_leave(leave_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    leaves = load_leaves()
    for leave in leaves:
        if leave["id"] == leave_id:
            leave["status"] = "Rejected"
            break

    save_leaves(leaves)
    flash("Leave rejected!", "error")
    return redirect(url_for("admin_leaves"))

#============== UPDATE PHONE ===============
@app.route("/employee/update_phone", methods=["POST"])
def update_phone():
    if "employee_id" not in session:
        flash("Please log in first!", "error")
        return redirect(url_for("login"))

    emp_id = session["employee_id"]
    new_phone = request.form.get("phone").strip()

    if not new_phone:
        flash("Phone number cannot be empty!", "error")
        return redirect(url_for("employee_dashboard"))

    # Load employees
    employees = load_employees()
    for emp in employees:
        if emp.get("id") == emp_id:
            emp["phone"] = new_phone
            break

    save_employees(employees)
    flash("Phone number updated successfully!", "success")
    return redirect(url_for("employee_dashboard"))


if __name__=="__main__":
    app.run(debug=True)
