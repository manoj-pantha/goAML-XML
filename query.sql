/*
  =============================================================================
  PROJECT: goAML Auto XML generation for Life Insurance
  MODULE:  Threshold Transaction Reporting (TTR-Life Insurance Sector)
  AUTHOR:  Manoj Pantha | Chartered Accountant & Actuarial SOA Student
  PURPOSE: Identifies Policyholders meeting the NPR 1,00,000 Annualized Premium  threshold for AML/CFT reporting.
  =============================================================================
*/
DECLARE @StartDate DATE = '2024-07-16';
DECLARE @EndDate DATE = '2025-07-16';

WITH ReportingData AS (
    SELECT
        pol.PolicyNo AS PolicyNo,
        br.BranchName AS BranchName,
        led.LedgerName AS DepositedBankAc,

        CAST(trx.TransactionDate AS DATE) AS TransactionDate,
        CAST(pol.DOC AS DATE) AS DOC,

        pol.Premium,
        pol.SumAssured,
        pol.TotalPremiumPaid AS Amount,

        CASE pol.MOP
            WHEN 'Q' THEN pol.Premium * 4
            WHEN 'M' THEN pol.Premium * 12
            WHEN 'H' THEN pol.Premium * 2
            ELSE pol.Premium
        END AS AnnualizedPremium,

        ins.FirstName,
        ins.MiddleName,
        ins.LastName,
        ins.FULLName AS FULLName,
        CASE WHEN ins.Gender = 'Male' THEN 'M' ELSE 'F' END AS Gender,
        ins.DOB AS DOBAssured,
        ins.FatherName,
        ins.MotherName,
        kyc.GrandFatherName,
        kyc.CitizenShipNo AS CitizenshipNumber,
        kyc.CitizenShipNoIssuedDate AS CitizenshipIssueDate,

        CONCAT(map.ProvinceName, ' ', map.DistrictName, ' ', kyc.WardNo, ' ', kyc.StreetName) AS FullAddress,
        map.DistrictName AS DistrictName,
        kyc.WardNo AS WardNo,
        kyc.MobileNo AS Mobile,
        kyc.Profession AS Occupation,
        prod.ProductName AS PlanName,
        pol.term AS PolicyTerm,

        CASE pol.MOP
            WHEN 'S' THEN 'Single'
            WHEN 'Y' THEN 'Yearly'
            WHEN 'H' THEN 'Half-Yearly'
            WHEN 'Q' THEN 'Quarterly'
            WHEN 'M' THEN 'Monthly'
            ELSE pol.MOP
        END AS PayMode,
        trx.CollectionType AS TranType

    FROM Underwriting.KYCTable kyc

    INNER JOIN Underwriting.InsuredDetails ins ON kyc.KYCNo = ins.KYCNo
    INNER JOIN Policy.PolicyTable pol ON ins.ProposalId = pol.ProposalId
    INNER JOIN Account.TransactionTable trx ON trx.SubLedgerNo = pol.PolicyNo

    LEFT JOIN Account.LedgerSetup led ON led.LedgerNo = trx.LedgerNo
    LEFT JOIN Settings.BranchSetup br ON pol.BranchCode = br.BranchCode
    LEFT JOIN Product.ProductSetup prod ON prod.ProductCode = pol.ProductCode
    LEFT JOIN Settings.MapSetup map ON map.DistrictId = kyc.DistrictId

    WHERE pol.MOP IN ('M','Q','H','S','Y')
      AND trx.CollectionType IN ('C','V')
      AND pol.DOC BETWEEN @StartDate AND @EndDate
)

SELECT * FROM ReportingData
WHERE AnnualizedPremium >= 100000
ORDER BY TransactionDate DESC;
