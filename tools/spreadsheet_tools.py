"""
NEXUS Spreadsheet Intelligence Tools
Parses Excel (.xlsx, .xls) and CSV datasets for suppliers, components, inventory levels,
daily burn rates, lead times, and documented backup options.
"""

import os
import io
import csv
from typing import Dict, List, Any, Optional
import pandas as pd


def parse_spreadsheet(file_name: str, file_bytes_or_path) -> Dict[str, Any]:
    """Parse an Excel or CSV file into structured tabular records."""
    ext = os.path.splitext(file_name)[1].lower()
    tables = {}
    
    try:
        if ext in [".xlsx", ".xls"]:
            # Load with pandas/openpyxl
            excel_file = file_bytes_or_path
            if isinstance(file_bytes_or_path, bytes):
                excel_file = io.BytesIO(file_bytes_or_path)
            
            xls = pd.ExcelFile(excel_file)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                # Clean column headers
                df.columns = [str(c).strip() for c in df.columns]
                # Convert NaN to None or empty
                records = df.where(pd.notnull(df), None).to_dict(orient="records")
                tables[sheet_name] = {
                    "columns": list(df.columns),
                    "rows": records,
                    "row_count": len(records)
                }
        elif ext == ".csv":
            content_io = None
            if isinstance(file_bytes_or_path, str):
                df = pd.read_csv(file_bytes_or_path)
            elif isinstance(file_bytes_or_path, bytes):
                df = pd.read_csv(io.BytesIO(file_bytes_or_path))
            else:
                df = pd.read_csv(file_bytes_or_path)
            
            df.columns = [str(c).strip() for c in df.columns]
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            tables["Sheet1"] = {
                "columns": list(df.columns),
                "rows": records,
                "row_count": len(records)
            }
        else:
            return {
                "success": False,
                "error": f"Unsupported spreadsheet format: {ext}",
                "tables": {},
                "file_name": file_name
            }
            
        return {
            "success": True,
            "file_name": file_name,
            "tables": tables,
            "summary": f"Successfully parsed {len(tables)} sheet(s) from {file_name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse spreadsheet {file_name}: {str(e)}",
            "tables": {},
            "file_name": file_name
        }


def extract_inventory_metrics(spreadsheet_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extracts structured inventory coverage metrics from parsed spreadsheets.
    Maps component names to stock levels, burn rate, and calculated coverage days.
    """
    inventory_map = {}
    if not spreadsheet_data.get("success"):
        return inventory_map
        
    for sheet_name, table in spreadsheet_data.get("tables", {}).items():
        rows = table.get("rows", [])
        for row in rows:
            # Find candidate component column
            comp_name = None
            for key in ["Component", "Item", "Part_Name", "Part Name", "Item_Name", "Component_Name"]:
                if key in row and row[key]:
                    comp_name = str(row[key]).strip()
                    break
            
            if not comp_name:
                continue
                
            # Current stock
            stock = None
            for key in ["Current_Stock", "Stock", "Quantity", "Units_Available", "Inventory_Units"]:
                if key in row and row[key] is not None:
                    try:
                        stock = float(str(row[key]).replace(",", "").strip())
                        break
                    except ValueError:
                        pass
                        
            # Daily burn rate
            burn_rate = None
            for key in ["Daily_Burn_Rate", "Burn_Rate", "Daily_Consumption", "Usage_Per_Day"]:
                if key in row and row[key] is not None:
                    try:
                        burn_rate = float(str(row[key]).replace(",", "").strip())
                        break
                    except ValueError:
                        pass
                        
            # Explicit Coverage Days or calculated
            coverage_days = None
            for key in ["Coverage_Days", "Days_Coverage", "Inventory_Coverage_Days", "Days_Of_Supply"]:
                if key in row and row[key] is not None:
                    try:
                        coverage_days = float(str(row[key]).replace(",", "").strip())
                        break
                    except ValueError:
                        pass
                        
            if coverage_days is None and stock is not None and burn_rate is not None and burn_rate > 0:
                coverage_days = round(stock / burn_rate, 2)
                
            inventory_map[comp_name.lower()] = {
                "component_name": comp_name,
                "current_stock": stock,
                "daily_burn_rate": burn_rate,
                "coverage_days": coverage_days,
                "source_sheet": sheet_name,
                "raw_row": row
            }
            
    return inventory_map


def extract_supplier_catalog(spreadsheet_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extracts supplier names, components supplied, lead times, and backup suppliers."""
    supplier_map = {}
    if not spreadsheet_data.get("success"):
        return supplier_map
        
    for sheet_name, table in spreadsheet_data.get("tables", {}).items():
        rows = table.get("rows", [])
        for row in rows:
            supplier_name = None
            for key in ["Supplier", "Supplier_Name", "Vendor", "Partner"]:
                if key in row and row[key]:
                    supplier_name = str(row[key]).strip()
                    break
            if not supplier_name:
                continue
                
            component = None
            for key in ["Component", "Supplies", "Part", "Component_Supplied"]:
                if key in row and row[key]:
                    component = str(row[key]).strip()
                    break
                    
            backup = None
            for key in ["Backup_Supplier", "Alternative_Supplier", "Secondary_Source", "Backup"]:
                if key in row and row[key]:
                    backup_val = str(row[key]).strip()
                    if backup_val.lower() not in ["none", "n/a", "no", "false", ""]:
                        backup = backup_val
                    break
                    
            lead_time = None
            for key in ["Lead_Time_Days", "Lead_Time", "Days_Lead"]:
                if key in row and row[key] is not None:
                    try:
                        lead_time = float(str(row[key]).replace(",", "").strip())
                        break
                    except ValueError:
                        pass
                        
            supplier_map[supplier_name.lower()] = {
                "supplier_name": supplier_name,
                "component": component,
                "backup_supplier": backup,
                "lead_time_days": lead_time,
                "source_sheet": sheet_name,
                "raw_row": row
            }
            
    return supplier_map
