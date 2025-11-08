# PythonTransactionSyncUpTool

## 📖 Overview  
A command-line Python application that integrates database transactions with third-party APIs to enrich and transform financial data before storing it into database tables. Built for automation and reliability in data synchronization processes. A lightweight, Python-driven data integration engine that fuses transaction data from databases and APIs into a single unified structure. Ideal for ETL-style workflows where accuracy, performance, and reusability matter.

---
<br />


## 💡 Key Highlights

✅ Fetches transactions from source DB. <br />
✅ Integrates with two external APIs for data enrichment. <br />
✅ Applies business logic for validation and transformation. <br />
✅ Persists final processed data into structured database tables. <br />
✅ Acts as a custom ETL (Extract, Transform, Load) pipeline. <br />
✅ API and database integration handled via modular components. <br />
✅ Optimized for performance with clean and maintainable code.

---
<br />


## ⚡Technology Used
✅ Language: Python 3.x <br />
✅ Database: SQL Server <br />
✅ APIs: RESTful services <br />
✅ Libraries: requests, pyodbc (or sqlalchemy), logging.

---
<br />


## 🎓 Project Structure
```
PythonTransactionSyncUpTool
│
├── src
│   ├── fetch_main.py
│   ├── dbconnection.py
│   ├── fetch_security_details.py
│   ├── fetch_coupon_details.py
│   ├── log_handler.py
│   ├── sms.py
│   ├── entities.py
│   ├── cfg_main.py
│   ├── cfg.py
│   ├── requirements.txt
│   ├── config
│   ├── build.cmd
```

---
<br />


## ▶️ How to run the project ?
1️⃣ Clone the Repository - <b>git clone https://github.com/Sachin-4-5/PythonTransactionSyncUpTool </b> <br />
2️⃣ Execute the provided SQL script (DBScript.sql) to create required tables and seed sample data. <br />
3️⃣ Open the config file and update the required details as per your need. <br />
4️⃣ Follow all steps as it is from (PythonSetup) to setup python environments. <br />
5️⃣ Open terminal in the project directory and execute: python fetch_main.py <AsOfDate>

---
<br />


## 🤝 Contribution
Pull requests are welcome! To contribute:

1️⃣ Fork the repo <br />
2️⃣ Create a feature branch (git checkout -b feature-xyz) <br />
3️⃣ Commit changes (git commit -m "Added feature xyz") <br />
4️⃣ Push to your branch (git push origin feature-xyz) <br />
5️⃣ Create a pull request 

---
<br />
