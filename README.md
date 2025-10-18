## Work Force - Employee Management System

> **A comprehensive web-based employee management platform** built using **Flask**, **Bootstrap**, **Jinja2** and **JSON** for backend data management.  
> It offers **employee registration, attendance tracking, leave management, admin controls,**, **interactive animations**, and **responsive UI** for an organized workforce system.
---

## Features 

# Core Features

Employee Registration & Management: Admin can add, edit, and delete employees easily.

Attendance System: Employees can log in daily; attendance is recorded and visualized in a calendar.

Leave Management: Employees can apply for leave; admin can approve or reject requests.

Dashboards:

  Employee dashboard with attendance calendar and leave  requests.

  Admin dashboard to manage all employees and leave approvals.

Role-based Access: Admin and employee views with specific permissions.

Responsive Design: Fully optimized for desktop and mobile devices.

Navbar & Branding: Persistent navigation bar across pages with company logo.

Notifications: Flash messages for successful operations or errors.
---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/rickcache/WorkForce.git
cd work-force

```

### Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # On Linux/Mac
venv\Scripts\activate         # On Windows

```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python app.py
```

### Now open your browser and navigation to:
```bash
http://127.0.0.1:5000/
```
## Files

WorkForce/
│
├── static/
│ ├── css/
│ │ └── style.css
│ ├── images/
│ │ ├── logo.png
│ │ └── other assets...
│ └── js/
│ └── main.js
│
├── templates/
│ ├── layout.html
│ ├── admin_dashboard.html
│ ├── employee_dashboard.html
│ ├── register_employee.html
│ ├── edit_employee.html
│ ├── leave_management.html
│ ├── login.html
│ └── other templates...
│
├── app.py
├── requirements.txt
└── README.md

## Tech Stack

| Category               | Technology Used               |
| ---------------------- | ----------------------------- |
| **Frontend**           | HTML5, CSS3        |
| **Backend**            | Python (Flask)                |
| **Templating**         | Jinja2                        |
| **Database**           | JSON file / in-memory storage |
| **Hosting (Optional)** | Render      |
| **Version Control**    | Git & GitHub                  |

## Site Images

### Landing Page
![Landing Page/ Homepage Page](https://i.postimg.cc/qRckfxRn/Screenshot-2025-10-18-124510.png)

### Admin Dashboard
![Admin Dashboard](https://i.postimg.cc/mDSGpZXV/Screenshot-2025-10-18-124529.png)

### Employee Dashboard
![Employee Dashboard](https://i.postimg.cc/yYMr94nV/Screenshot-2025-10-18-124558.png)
## Hosting Options

You can host this project for free on:

Render (Recommended – free, reliable, supports Flask apps)

PythonAnywhere (Simpler setup, good for smaller sites)
## Example Json Structure

{
  "employees": [
    {
      "id": 101,
      "name": "Rick Biswas",
      "email": "rick@example.com",
      "phone": "9876543210",
      "address": "Kolkata, India",
      "password": "hashed_password",
      "role": "employee",
      "attendance": [],
      "leaves": []
    }
  ]
}
## UI & Design

Clean, polished dashboards for admin and employees.

Interactive calendars for attendance visualization.

Leave tables with color-coded status indicators.

Responsive navbar with logo and navigation links.

Modern section boxes with soft shadows and rounded corners.

Flash notifications for actions like leave requests, edits, and deletions.
## Notes

Built purely for educational and portfolio purposes.

Demonstrates role-based access, JSON data handling, and Flask CRUD operations.

Data is stored in JSON files; for production, a database is recommended.
## Author

Rick Biswas
🎓 B.Sc Computer Science | Bhairabh Ganguly College
💼 Aspiring QA Engineer | Automation Enthusiast
🌐 GitHub: rickcache