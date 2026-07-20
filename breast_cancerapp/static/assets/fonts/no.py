from graphviz import Digraph

# Create system structure diagram using Graphviz
dot = Digraph(comment="Employment Salary Registration Folio System", format="png")
dot.attr(rankdir="LR", size="8")

# Main modules
dot.node("Login", "Login & Authentication")
dot.node("Dashboard", "Dashboard")
dot.node("EmpMgmt", "Employee Management")
dot.node("SalaryReg", "Salary Register (Folio)")
dot.node("Payroll", "Payroll Processing")
dot.node("Reports", "Reports Module")
dot.node("Admin", "System Administration")

# Submodules for Employee Management
dot.node("EmpReg", "Register Employee")
dot.node("EmpProfile", "Employee Profile & List")
dot.node("EmpUpdate", "Update/Terminate Employee")

# Submodules for Salary Register
dot.node("SalDetails", "Salary Details (Basic, Allowances, Deductions)")
dot.node("SalSlip", "Salary Slip")

# Submodules for Payroll
dot.node("GenPayroll", "Generate Payroll")
dot.node("Approval", "Approvals Workflow")
dot.node("PayReports", "Payment Reports")

# Submodules for Reports
dot.node("EmpReports", "Employee Reports")
dot.node("SalReports", "Salary Reports")
dot.node("Audit", "Audit Trail")

# Submodules for Admin
dot.node("UserMgmt", "User Management")
dot.node("Settings", "System Settings")
dot.node("Backup", "Backup & Restore")

# Connections
dot.edges([("Login", "Dashboard"),
           ("Dashboard", "EmpMgmt"),
           ("Dashboard", "SalaryReg"),
           ("Dashboard", "Payroll"),
           ("Dashboard", "Reports"),
           ("Dashboard", "Admin")])

# Employee Management connections
dot.edges([("EmpMgmt", "EmpReg"),
           ("EmpMgmt", "EmpProfile"),
           ("EmpMgmt", "EmpUpdate")])

# Salary Register connections
dot.edges([("SalaryReg", "SalDetails"),
           ("SalaryReg", "SalSlip")])

# Payroll connections
dot.edges([("Payroll", "GenPayroll"),
           ("Payroll", "Approval"),
           ("Payroll", "PayReports")])

# Reports connections
dot.edges([("Reports", "EmpReports"),
           ("Reports", "SalReports"),
           ("Reports", "Audit")])

# Admin connections
dot.edges([("Admin", "UserMgmt"),
           ("Admin", "Settings"),
           ("Admin", "Backup")])

# Render diagram
output_path = "/mnt/data/salary_register_folio_system"
dot.render(output_path, view=False)

output_path + ".png"
