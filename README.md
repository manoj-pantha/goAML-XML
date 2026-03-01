# 🏦 goAML XML Reporting Generator (Python & SQL)

### 📂 Automated AML/CFT Compliance Tool
This project automates the extraction of the data from a SQL database and transforms it into the **goAML XML 4.0** (standardized by UNODC) for electronic filing.
[!IMPORTANT]
Disclaimer: This project is for educational purposes only. The reporting logic, SQL queries, and XML schemas provided are templates and must be modified to align with specific company rules, product specifications, and the latest regulatory guidelines from the Financial Intelligence Unit (FIU) or the regulators.
---

## 🚀 Key Features
- **SQL Data Extraction:** Optimized CTE-based queries to aggregate Transaction and data.
- **XML Schema Mapping:** Python logic to map flat database rows into nested XML structures (Report > Transaction > Entity).
- **Validation:** Automated check against XSD (XML Schema Definition) to ensure zero-rejections by the FIU.
- **Data Masking:** Built-in scripts to anonymize PII (Personally Identifiable Information) for testing environments.

---

## 🛠️ The Tech Stack
* **SQL (T-SQL/PostgreSQL):** For complex joins between `KYC`, `Policy`, and `Transactions` tables.
* **Python 3.x:** Using `lxml` or `ElementTree` for high-performance XML construction.
* **Pandas:** For intermediate data validation and cleaning.
* **zipfile:** To create a ZIP file for individual xml file.

---

## 📊 Data Flow Logic
1. **Extract:** SQL Query fetches transactions exceeding threshold.
2. **Transform:** Python cleanses addresses, formats dates to ISO 8601, and maps currency codes.
3. **Load:** The script generates a `.xml` file and `.zip` file ready for upload to the goAML Web portal.

---
