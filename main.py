import os
import random
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from zoneinfo import ZoneInfo
import pyodbc
import json


# --------------------------------------------------
# prettify functions is to structure the code in a beautiful way rather than plain text.
# generate_transaction_number to generate the unique transaction reporting number to FIU. It can be any unique number.
# clean_dataframe is to handle any Na values and to convert the data into string.
# --------------------------------------------------

def prettify(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_transaction_number():
    prefix = "TRNXML"
    random_number = random.randint(100000, 999999)
    date_part = datetime.today().strftime("%d %b %y").upper()
    return f"{prefix}{random_number} {date_part}"

def clean_dataframe(df):
    return df.fillna("").astype(str)

# --------------------------------------------------
# Main XML Functions
# --------------------------------------------------

def build_location(parent):
    location = ET.SubElement(parent, "location")
    ET.SubElement(location, "address_type").text = "1" #1 for permanent
    ET.SubElement(location, "address").text = "Address"
    ET.SubElement(location, "town").text = "TownName"
    ET.SubElement(location, "city").text = "CityName"
    ET.SubElement(location, "zip").text = "1" #ward no
    ET.SubElement(location, "country_code").text = "NP"
    ET.SubElement(location, "state").text = "Bagmati" #province name

def build_from_client(transaction, row):
    t_from = ET.SubElement(transaction, "t_from_my_client")
    ET.SubElement(t_from, "from_funds_code").text = "K"

    # Conductor
    conductor = ET.SubElement(t_from, "t_conductor")
    ET.SubElement(conductor, "first_name").text = row["FirstName"]
    if row["MiddleName"]:
        ET.SubElement(conductor, "middle_name").text = row["MiddleName"]
    ET.SubElement(conductor, "last_name").text = row["LastName"]

    # Person
    person = ET.SubElement(t_from, "from_person")
    ET.SubElement(person, "gender").text = row["Gender"]
    ET.SubElement(person, "first_name").text = row["FirstName"]
    if row["MiddleName"]:
        ET.SubElement(person, "middle_name").text = row["MiddleName"]
    ET.SubElement(person, "last_name").text = row["LastName"]
    ET.SubElement(person, "birthdate").text = f"{row['DOBAssured']}T00:00:00+05:45"
    ET.SubElement(person, "birth_place").text = row["FatherName"]
    ET.SubElement(person, "mothers_name").text = row["MotherName"]
    ET.SubElement(person, "ssn").text = row["CitizenshipNumber"]
    ET.SubElement(person, "nationality1").text = "NP"
    ET.SubElement(person, "residence").text = "NP"

    # Address
    addresses = ET.SubElement(person, "addresses")
    address = ET.SubElement(addresses, "address")
    ET.SubElement(address, "address_type").text = "1"
    ET.SubElement(address, "address").text = row["FullAddress"]
    ET.SubElement(address, "city").text = row["DistrictName"]
    ET.SubElement(address, "zip").text = row["WardNo"]
    ET.SubElement(address, "country_code").text = "NP"

    ET.SubElement(person, "occupation").text = row["Occupation"]
    ET.SubElement(t_from, "from_country").text = "NP"


def build_to_client(transaction, row):
    t_to = ET.SubElement(transaction, "t_to_my_client")
    ET.SubElement(t_to, "to_funds_code").text = "O"

    to_account = ET.SubElement(t_to, "to_account")
    ET.SubElement(to_account, "institution_name").text = "ABC Life Insurance Limited" #Name of the company
    ET.SubElement(to_account, "swift").text = "NA"
    ET.SubElement(to_account, "branch").text = row["BranchName"]
    ET.SubElement(to_account, "account").text = row["PolicyNo"]
    ET.SubElement(to_account, "currency_code").text = "NPR"
    ET.SubElement(to_account, "account_name").text = row["FULLName"]
    ET.SubElement(to_account, "account_type").text = "LI"

    related_persons = ET.SubElement(to_account, "related_persons")
    account_related_person = ET.SubElement(related_persons, "account_related_person")
    ET.SubElement(account_related_person, "is_primary").text = "true"

    t_person = ET.SubElement(account_related_person, "t_person")
    ET.SubElement(t_person, "gender").text = row["Gender"]
    ET.SubElement(t_person, "first_name").text = row["FirstName"]
    if row["MiddleName"] != "":
        ET.SubElement(t_person, "middle_name").text = row["MiddleName"]
    ET.SubElement(t_person, "last_name").text = row["LastName"]
    ET.SubElement(t_person, "birthdate").text = f"{row['DOBAssured']}T00:00:00+05:45"
    ET.SubElement(t_person, "birth_place").text = row["FatherName"] #issue in the mapping in FIU Nepal
    ET.SubElement(t_person, "mothers_name").text = row["MotherName"]
    ET.SubElement(t_person, "ssn").text = row["CitizenshipNumber"]
    ET.SubElement(t_person, "nationality1").text = "NP"
    ET.SubElement(t_person, "residence").text = "NP"

    addresses2 = ET.SubElement(t_person, "addresses")
    address2 = ET.SubElement(addresses2, "address")
    ET.SubElement(address2, "address_type").text = "1"
    ET.SubElement(address2, "address").text = row["FullAddress"]
    ET.SubElement(address2, "city").text = row["DistrictName"]
    ET.SubElement(address2, "zip").text = row["WardNo"]
    ET.SubElement(address2, "country_code").text = "NP"

    ET.SubElement(t_person, "occupation").text = row["Occupation"]
    ET.SubElement(account_related_person, "role").text = "A"

    ET.SubElement(to_account, "opened").text = f"{row['DOC']}T00:00:00+05:45"
    ET.SubElement(to_account, "balance").text = row["Premium"]
    ET.SubElement(to_account, "date_balance").text = f"{row['DOC']}T00:00:00+05:45"
    ET.SubElement(to_account, "status_code").text = "A"

    comments = (
        f"Term of Insurance Policy: {row['PolicyTerm']}, "
        f"Nature/Type of insurance policy: {row['PlanName']}, "
        f"Total insured Amount: {row['SumAssured']}, "
        f"Premium Installment Structure: {row['PayMode']}"
    )
    ET.SubElement(to_account, "comments").text = comments

    ET.SubElement(t_to, "to_country").text = "NP"

def build_report_xml(row):
    report = ET.Element("report")

    ET.SubElement(report, "rentity_id").text = "entity_id" #entity_id provided by the FIU
    ET.SubElement(report, "rentity_branch").text = "Location"
    ET.SubElement(report, "submission_code").text = "E"
    ET.SubElement(report, "report_code").text = "TTR"

    today = datetime.now(ZoneInfo("Asia/Kathmandu")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    ET.SubElement(report, "report_date").text = today.isoformat()
    ET.SubElement(report, "currency_code_local").text = "NPR"
    ET.SubElement(report, "reporting_user_code").text = "username" #username provided by the FIU

    build_location(report)

    transaction = ET.SubElement(report, "transaction")
    ET.SubElement(transaction, "transactionnumber").text = generate_transaction_number()
    ET.SubElement(transaction, "transaction_location").text = row["BranchName"]
    ET.SubElement(transaction, "transaction_description").text = \
        f"Direct Deposit by Customer to {row['DepositedBankAc']}"
    ET.SubElement(transaction, "date_transaction").text = \
        f"{row['TransactionDate']}T00:00:00+05:45"
    ET.SubElement(transaction, "transmode_code").text = "A"
    ET.SubElement(transaction, "amount_local").text = row["Premium"]

    build_from_client(transaction, row)
    build_to_client(transaction, row)

    return report


# --------------------------------------------------
# File Handling
# --------------------------------------------------

def write_xml(report, policy_no, report_dir):
    xml_output = prettify(report)
    filename = f"goAML{policy_no}.xml"
    file_path = os.path.join(report_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_output)
def create_zip(report_dir, zip_dir):
    os.makedirs(zip_dir, exist_ok=True)
    zip_filename = f"ZIP_REPORT_{datetime.today().strftime('%d %b %y').upper()}.zip"
    zip_path = os.path.join(zip_dir, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, report_dir)
                zipf.write(full_path, arcname)

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    with open('config.json') as f:
        config = json.load(f)

    db = config['database']
    conn_str = f"DRIVER={{{db['driver']}}};SERVER={db['server']};DATABASE={db['database']};UID={db['username']};PWD={db['password']}"
    mssql_conn = pyodbc.connect(conn_str)
    mssql_cursor = mssql_conn.cursor()

    with open('query.sql', 'r') as f:
        query = f.read()
    mssql_cursor.execute(query)

    rows = mssql_cursor.fetchall()
    columns = [column[0] for column in mssql_cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    df = clean_dataframe(df)   #Alternatively data from csv or from any soruces can be imported as dataframe

    report_dir = "report/xmlfile"
    os.makedirs(report_dir, exist_ok=True)

    for _, row in df.iterrows():
        report = build_report_xml(row)
        write_xml(report, row["PolicyNo"], report_dir)

    create_zip(report_dir, "report/zipfile")

    print(f"{len(df)} XML files created successfully.")


if __name__ == "__main__":
    main()
