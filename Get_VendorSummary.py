import sqlite3
import pandas as pd
import logging

logging.basicConfig(
    filename= "logs/get_vendor_summary.log",
    level = logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def create_vendor_summary(conn):
    vendor_sales_summary = pd.read_sql_query("""
WITH FreightSummary AS (
    SELECT 
        VendorNumber,                       -- ADDED: Must select this to join it later
        SUM(Freight) AS FreightCost         -- FIXED: Added the actual calculation
    FROM vendor_invoice
    GROUP BY VendorNumber                   -- FIXED: 'GROUPO BY'
),

PurchaseSummary AS ( 
    SELECT
        p.VendorNumber,                     -- FIXED: Added missing comma
        p.VendorName,
        p.Brand,
        p.Description,
        p.PurchasePrice,
        pp.Price AS ActualPrice,
        pp.Volume,
        SUM(p.Quantity) AS TotalPurchaseQuantity,
        SUM(p.Dollars) AS TotalPurchaseDollars   -- FIXED: 'SUNM'
    FROM purchases as p
    JOIN purchase_prices as pp
        ON p.Brand = pp.Brand
    WHERE p.PurchasePrice > 0
    GROUP BY 
        p.VendorNumber, 
        p.VendorName, 
        p.Brand, 
        p.Description, 
        p.PurchasePrice, 
        pp.Price, 
        pp.Volume
),

SalesSummary AS (
    SELECT 
        VendorNo,
        Brand,
        SUM(SalesQuantity) AS TotalSalesQuantity, 
        SUM(SalesDollars) AS TotalSalesDollars,
        SUM(salesPrice) AS TotalSalesPrice,
        SUM(eXCISEtAX) as TotalExciseTax
    FROM sales
    GROUP BY VendorNo, Brand
)

SELECT
    ps.VendorNumber,
    ps.VendorName,
    ps.Brand,
    ps.Description,
    ps.PurchasePrice,
    ps.ActualPrice,
    ps.Volume,                              -- FIXED: 'ps,Volume'
    ps.TotalPurchaseQuantity,
    ps.TotalPurchaseDollars,
    ss.TotalSalesQuantity,                  -- FIXED: Added missing comma
    ss.TotalSalesDollars,                   -- FIXED: Added missing comma
    ss.TotalSalesPrice,                     -- FIXED: Added missing comma
    ss.TotalExciseTax,
    fs.FreightCost
FROM PurchaseSummary ps
LEFT JOIN SalesSummary ss                   -- FIXED: 'SlaesSummary'
    ON ps.VendorNumber = ss.VendorNo
    AND ps.Brand = ss.Brand
LEFT JOIN FreightSummary fs                 -- FIXED: 'FrieghtSummary'
    ON ps.VendorNumber = fs.VendorNumber
ORDER BY ps.TotalPurchaseDollars DESC
""", conn)

def clean_data(df):
    vendor_sales_summary['Volume'] =            vendor_sales_summary['Volume'].astype('float64')