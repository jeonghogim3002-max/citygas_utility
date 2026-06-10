from flask import Flask, render_template_string
import pandas as pd
import json

app = Flask(__name__)

# Load CSV data
facility_df = pd.read_csv('data/facility_management.csv')
labor_df = pd.read_csv('data/labor_management.csv')
energy_df = pd.read_csv('data/energy_management.csv')
safety_df = pd.read_csv('data/safety_health.csv')
inspection_df = pd.read_csv('data/equipment_inspection.csv')

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Urban Gas Company Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #ddd;
        }
        .tab-btn {
            padding: 10px 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 16px;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab-btn.active {
            border-bottom-color: #2196F3;
            color: #2196F3;
            font-weight: bold;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background-color: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #ddd;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        .success {
            color: #4CAF50;
            padding: 20px;
            text-align: center;
            font-weight: bold;
            background-color: #e8f5e9;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
    <script>
        function showTab(tabName) {
            // Hide all tabs
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));

            // Remove active from all buttons
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // Show first tab by default
        window.onload = function() {
            document.querySelector('.tab-btn').click();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🏢 Urban Gas Company - Administrative Dashboard</h1>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Employees</h3>
                <div class="value">{{ total_employees }}</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h3>Total Facilities</h3>
                <div class="value">{{ total_facilities }}</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h3>Total Maintenance Cost</h3>
                <div class="value">{{ total_maintenance }}M</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <h3>Safety Incidents</h3>
                <div class="value">{{ total_accidents }}</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn" onclick="showTab('facility')">Facility Management</button>
            <button class="tab-btn" onclick="showTab('labor')">Labor Management</button>
            <button class="tab-btn" onclick="showTab('energy')">Energy Management</button>
            <button class="tab-btn" onclick="showTab('safety')">Safety & Health</button>
            <button class="tab-btn" onclick="showTab('inspection')">Equipment</button>
        </div>

        <div id="facility" class="tab-content">
            <h3>Facility Management Data</h3>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Facility</th>
                    <th>Employees</th>
                    <th>Maintenance</th>
                    <th>Electricity</th>
                    <th>Water</th>
                    <th>Gas</th>
                </tr>
                {{ facility_table }}
            </table>
        </div>

        <div id="labor" class="tab-content">
            <h3>Labor Management Data</h3>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Facility</th>
                    <th>Total Staff</th>
                    <th>Regular</th>
                    <th>Contract</th>
                    <th>New Hires</th>
                    <th>Resignations</th>
                </tr>
                {{ labor_table }}
            </table>
        </div>

        <div id="energy" class="tab-content">
            <h3>Energy Management Data</h3>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Facility</th>
                    <th>Gas Usage</th>
                    <th>Electricity (kWh)</th>
                    <th>Water</th>
                    <th>Efficiency</th>
                    <th>Target %</th>
                </tr>
                {{ energy_table }}
            </table>
        </div>

        <div id="safety" class="tab-content">
            <h3>Safety & Health Data</h3>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Facility</th>
                    <th>Accidents</th>
                    <th>Injured</th>
                    <th>Illness</th>
                    <th>Training %</th>
                    <th>Risk Factors</th>
                </tr>
                {{ safety_table }}
            </table>
        </div>

        <div id="inspection" class="tab-content">
            <h3>Equipment Inspection Data</h3>
            <table>
                <tr>
                    <th>Month</th>
                    <th>Facility</th>
                    <th>Regular Inspection</th>
                    <th>Emergency</th>
                    <th>Defects Found</th>
                    <th>Resolution %</th>
                </tr>
                {{ inspection_table }}
            </table>
        </div>

        <div class="success">✅ Dashboard loaded successfully! | {{ record_count }} total records</div>
    </div>
</body>
</html>
'''

def df_to_html_rows(df, columns):
    rows = ''
    for _, row in df.head(10).iterrows():
        rows += '<tr>'
        for col in columns:
            rows += f'<td>{row[col]}</td>'
        rows += '</tr>'
    return rows

@app.route('/')
def dashboard():
    # Prepare data
    total_employees = int(labor_df['Total_Staff'].sum())
    total_facilities = labor_df['Facility'].nunique()
    total_maintenance = int(facility_df['Maintenance_Cost'].sum())
    total_accidents = int(safety_df['Accidents'].sum())
    total_records = len(facility_df) + len(labor_df) + len(energy_df) + len(safety_df)

    # Generate table rows
    facility_table = df_to_html_rows(facility_df,
        ['Month', 'Facility', 'Employee_Count', 'Maintenance_Cost', 'Electricity_Cost', 'Water_Cost', 'Gas_Cost'])

    labor_table = df_to_html_rows(labor_df,
        ['Month', 'Facility', 'Total_Staff', 'Regular_Staff', 'Contract_Staff', 'New_Hire', 'Resignation'])

    energy_table = df_to_html_rows(energy_df,
        ['Month', 'Facility', 'Gas_Usage', 'Electricity_Usage', 'Water_Usage', 'Efficiency_Grade', 'Target_Achievement_Rate'])

    safety_table = df_to_html_rows(safety_df,
        ['Month', 'Facility', 'Accidents', 'Injured_Count', 'Illness_Count', 'Safety_Training_Rate', 'Risk_Factors'])

    inspection_table = df_to_html_rows(inspection_df,
        ['Month', 'Facility', 'Regular_Inspection', 'Emergency_Inspection', 'Defects_Found', 'Defect_Resolution_Rate'])

    return render_template_string(
        html_template,
        total_employees=total_employees,
        total_facilities=total_facilities,
        total_maintenance=total_maintenance,
        total_accidents=total_accidents,
        record_count=total_records,
        facility_table=facility_table,
        labor_table=labor_table,
        energy_table=energy_table,
        safety_table=safety_table,
        inspection_table=inspection_table
    )

if __name__ == '__main__':
    print("Starting dashboard on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=True)
