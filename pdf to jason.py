import pdfplumber
import json
import os
import re
from collections import defaultdict

pdf_infos = {
    "dhan_2.pdf": "15/05/2024",
    "GOLDMINE_1.pdf": "10/05/2024",
    "GOLDMINE_2.pdf": "14/05/2024",
    "JM FINANCIAL.PDF": "03/04/2024",
    "ARIHANT CAPITAL MARKETS LTD.pdf": "19/10/2023",
    "AXIS.pdf": "18/01/2024",
    "BP Equities Pvt. Ltd..pdf": "23/05/2024",
    "JAVERI FISCAL SERVICES LTD..pdf": "12/11/2023",
    "Kotak_06-04-2021_Bill.pdf": "06/04/2021",
    "greshma.pdf": "14/12/2023",
    "rudra (1).pdf": "09/05/2024",
    "CN_20231019_482600121_MER.pdf (1).pdf": "19/10/2023",
    "CNB_11_COMMON_CONTRACT_12Nov2023_S137__3951_signed (1).pdf": "12/11/2023",
    "Zerodha 11102018.pdf": "11/10/2018",
    "zerodha_old.pdf": "15/10/2018"
    
}


data = []

def validate_time_format(time_str):
    if not isinstance(time_str, str):
        return False
    parts = time_str.strip().split(":")
    return len(parts) == 3 and all(part.isdigit() for part in parts)

def process_goldmine_generic(pdf_path, trade_date):
    pattern = re.compile(
        r"(\d{13,})\s+"          
        r"(\d{2}:\d{2}:\d{2})\s+" 
        r"(\d+)\s+"               
        r"(\d{2}:\d{2}:\d{2})\s+" 
        r"(.+?)\s+"               
        r"([BS])\s+"              
        r"(\d+)\s+"               
        r"([\d.]+)\s+"            
        r"([\d.]+)\s+"            
        r"([\d.]+)\s+"            
        r"([-]?\d+\.\d+)"         
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": match.group(4),
                    "Trade No": match.group(3),
                    "Trade Date": trade_date,
                    "Security/Contract Description": match.group(5).strip(),
                    "Buy(B)/Sell(S)": match.group(6),
                    "Quantity": match.group(7),
                    "Trade Price Per Unit": match.group(8),
                    "Net Total": match.group(11)
                })


def process_dhan(pdf_path, trade_date):
    trade_pattern = re.compile(
        r"(?P<order_no>\d{13,})\s+"
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>SELAN EXPLO\. TECH LT)\s*D?\s+"
        r"(?P<side>BUY|SELL)\s+"
        r"(?P<qty>\d+)\s*(?:D)?\s+"
        r"(?P<price>\d+\.\d+)\s+"         
        r"(?P<brokerage>\d+\.\d+)\s+"     
        r"(?P<net_rate>\d+\.\d+)\s+"      
        r"(?P<closing_rate>\d+\.\d+)\s+"  
        r"(?P<stt>\d+\.\d+)\s+"           
        r"(?P<net_total>-?\d+\.\d+)\s+"
        r"(NSE-M|BSE)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in trade_pattern.finditer(text):
                try:
                    gd = match.groupdict()
                    data.append({
                        "Source PDF": os.path.basename(pdf_path),
                        "Trade Time": gd["trade_time"],
                        "Trade No": gd["trade_no"],
                        "Trade Date": trade_date,
                        "Security/Contract Description": gd["security"],
                        "Buy(B)/Sell(S)": "B" if gd["side"] == "BUY" else "S",
                        "Quantity": gd["qty"],
                        "Trade Price Per Unit": gd["price"],
                        "Net Total": gd["net_total"]
                    })
                except Exception as e:
                    print(f"⚠️ Parse error: {e}")


def process_jm_financial(pdf_path, trade_date):
    pattern = re.compile(
        r"(\d+)\s+"
        r"(\d{2}:\d{2}:\d{2})\s+"
        r"(\d+)\s+"
        r"(\d{2}:\d{2}:\d{2})\s+"
        r"(.+?)\s+"
        r"(BUY|SELL)\s+"
        r"(\d+)\s+"
        r"([\d,]+\.\d+)\s+"
        r"([\d,]+\.\d+)\s+"
        r"([\d,]+\.\d+)"
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                qty = int(match.group(7))
                price = float(match.group(8).replace(",", ""))
                net_total = round(qty * price, 2)
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": match.group(4),
                    "Trade No": match.group(3),
                    "Trade Date": trade_date,
                    "Security/Contract Description": match.group(5).strip(),
                    "Buy(B)/Sell(S)": "B" if match.group(6) == "BUY" else "S",
                    "Quantity": match.group(7),
                    "Trade Price Per Unit": str(price),
                    "Net Total": str(net_total)
                })
def process_arihant(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<security>.+?)\s+"  
        r"(?P<side>[BS])\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"[\d.]+\s+"  
        r"[\d.]+\s+"  
        r"(?P<net_total>[-\d.]+)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                gd = match.groupdict()
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": gd["side"],
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": gd["net_total"]
                })


def process_axis(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<security>.+?)\s+"
        r"(?P<side>BUY|SELL)\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"[\d.]+\s+"  
        r"[\d.]+\s+"  
        r"(?P<net_total>[\d,().-]+)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for match in pattern.finditer(text):
                gd = match.groupdict()
                net_total = gd["net_total"].replace(",", "").strip("()")
                if gd["net_total"].startswith("("):
                    net_total = f"-{net_total}"
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": "B" if gd["side"] == "BUY" else "S",
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": net_total
                })



def process_bp_equities(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>.+?)\s+"
        r"(?P<side>Buy|Sell)\s+[-]?(?=\d)"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"(?P<brokerage>[\d.]+)\s+"
        r"(?P<net_rate>[\d.]+)\s+"
        r"(?P<closing_rate>[\d.]+)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                gd = match.groupdict()
                qty = int(gd["qty"])
                price = float(gd["price"])
                net_total = round(qty * price, 2)
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": "B" if gd["side"].upper() == "BUY" else "S",
                    "Quantity": str(qty),
                    "Trade Price Per Unit": str(price),
                    "Net Total": str(net_total)
                })


def process_javeri(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<order_no>\d+)\s+"
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>.+?)\s+"
        r"(?P<side>Buy|Sell)\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                gd = match.groupdict()
                qty = int(gd["qty"])
                price = float(gd["price"])
                net_total = round(qty * price, 2)
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": "B" if gd["side"].upper() == "BUY" else "S",
                    "Quantity": str(qty),
                    "Trade Price Per Unit": str(price),
                    "Net Total": str(net_total)
                })

def process_greshma(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<security>.+?)\s+"
        r"(?P<side>[BS])\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"(?P<brokerage>[\d.]+)\s+"
        r"(?P<net_rate>[\d.]+)\s+"
        r"(?P<net_total>[-\d,.()]+)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                gd = match.groupdict()
                net_total = gd["net_total"].replace(",", "").strip("()")
                if gd["net_total"].startswith("("):
                    net_total = f"-{net_total}"
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": gd["side"],
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": net_total
                })


def process_kotak(pdf_path, trade_date):
    pattern = re.compile(
        r"(GMDCLTD EQ|SUN RETAIL LIMITED)\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"(?P<amount>[\d,.]+)"
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for match in pattern.finditer(text):
                qty = int(match.group("qty"))
                price = float(match.group("price"))
                net_total = match.group("amount").replace(",", "")
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": "",
                    "Trade No": "",
                    "Trade Date": trade_date,
                    "Security/Contract Description": match.group(1),
                    "Buy(B)/Sell(S)": "S",
                    "Quantity": str(qty),
                    "Trade Price Per Unit": str(price),
                    "Net Total": net_total
                })


def process_rudra(pdf_path, trade_date):
    pattern = re.compile(
        r"NSE\s+(?P<price>\d+\.\d+)\s+(?P<amount>\d+\.\d+)D\s+(?P<qty>\d+)\s+(?P<total>\d+\.\d+)"
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if "NSE" in line and "D" in line:
                    match = pattern.search(line)
                    if match:
                        qty = match.group("qty")
                        price = match.group("price")
                        total = match.group("total")
                        security = lines[i - 1].strip() if i > 0 else "UNKNOWN"
                        data.append({
                            "Source PDF": os.path.basename(pdf_path),
                            "Trade Time": "",  
                            "Trade No": "",    
                            "Trade Date": trade_date,
                            "Security/Contract Description": security,
                            "Buy(B)/Sell(S)": "S",  
                            "Quantity": qty,
                            "Trade Price Per Unit": price,
                            "Net Total": total
                        })


def process_arihant_mer(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<price>\d+\.\d+)\s+0\.0000\s+(?P<net_rate>\d+\.\d+)\s+(?P<brokerage>\d+\.\d+)\s+(?P<gross_rate>\d+\.\d+)\s+(?P<qty>\d+)(?P<side>[BS])\s+OPTSTK\s+(?P<security>.+?)\s+(?P<trade_time>\d{2}:\d{2}:\d{2})\s+(?P<trade_no>\d+)\s+(?P<order_time>\d{2}:\d{2}:\d{2})\s+(?P<order_no>\d+)"
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text().replace("\n", " ")
            for match in pattern.finditer(text):
                gd = match.groupdict()
                net_total = float(gd["price"]) * int(gd["qty"])
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": f"OPTSTK {gd['security'].strip()}",
                    "Buy(B)/Sell(S)": gd["side"],
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": str(round(net_total, 2))
                })
def process_javeri_signed(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<order_no>\d+)\s+"
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>.+?)\s+"
        r"(?P<side>Buy|Sell)\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)"
    )
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text().replace("\n", " ")
            for match in pattern.finditer(text):
                gd = match.groupdict()
                qty = int(gd["qty"])
                price = float(gd["price"])
                net_total = round(qty * price, 2)
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": "B" if gd["side"].lower() == "buy" else "S",
                    "Quantity": str(qty),
                    "Trade Price Per Unit": str(price),
                    "Net Total": str(net_total)
                })
def process_zerodha_old(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<order_no>\d+)\s+"
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>.+?)\s*/\s+INE\d+[A-Z0-9]*\s+"
        r"(?P<side>[BS])\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"(?P<net_total>\(?-?[\d.]+\)?)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            text = text.replace("\n", " ")
            for match in pattern.finditer(text):
                gd = match.groupdict()
                net_total = gd["net_total"].replace("(", "-").replace(")", "")
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": gd["side"],
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": net_total
                })


def process_zerodha_2018_style(pdf_path, trade_date):
    pattern = re.compile(
        r"(?P<order_no>\d+)\s+"
        r"(?P<order_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<trade_no>\d+)\s+"
        r"(?P<trade_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<security>.+?)\s*/\s+INE\d+[A-Z0-9]*\s+"
        r"(?P<side>[BS])\s+"
        r"(?P<qty>\d+)\s+"
        r"(?P<price>[\d.]+)\s+"
        r"(?P<net_total>\(?-?[\d.]+\)?)"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            text = text.replace("\n", " ")
            for match in pattern.finditer(text):
                gd = match.groupdict()
                net_total = gd["net_total"].replace("(", "-").replace(")", "")
                data.append({
                    "Source PDF": os.path.basename(pdf_path),
                    "Trade Time": gd["trade_time"],
                    "Trade No": gd["trade_no"],
                    "Trade Date": trade_date,
                    "Security/Contract Description": gd["security"].strip(),
                    "Buy(B)/Sell(S)": gd["side"],
                    "Quantity": gd["qty"],
                    "Trade Price Per Unit": gd["price"],
                    "Net Total": net_total
                })


dispatch_map = {
    "dhan_2.pdf": process_dhan,
    "GOLDMINE_1.pdf": process_goldmine_generic,
    "GOLDMINE_2.pdf": process_goldmine_generic,
    "JM FINANCIAL.PDF": process_jm_financial,
    "ARIHANT CAPITAL MARKETS LTD.pdf": process_arihant,
    "AXIS.pdf": process_axis,
    "BP Equities Pvt. Ltd..pdf": process_bp_equities,
    "JAVERI FISCAL SERVICES LTD..pdf": process_javeri,
    "Kotak_06-04-2021_Bill.pdf": process_kotak,
    "greshma.pdf": process_greshma,
    "rudra (1).pdf": process_rudra,
    "CN_20231019_482600121_MER.pdf (1).pdf": process_arihant_mer,
    "CNB_11_COMMON_CONTRACT_12Nov2023_S137__3951_signed (1).pdf": process_javeri_signed,
    "Zerodha 27112018.pdf": process_zerodha_2018_style,
    "zerodha_old.pdf": process_zerodha_old
    
  
}

for file_name, date in pdf_infos.items():
    path = os.path.join("C:/Users/DELL8/OneDrive/Desktop/equity_trading", file_name)
    print(f"\n Processing: {file_name}")

    if not os.path.exists(path):
        print(f" File not found: {path}")
        continue

    try:
        handler = dispatch_map[file_name]
        print(f" Using parser: {handler.__name__}")
        handler(path, date)
        print(f" Finished parsing {file_name}")
    except Exception as e:
        print(f" Failed to process {file_name}: {e}")



grouped_data = defaultdict(list)
for entry in data:
    grouped_data[entry["Source PDF"]].append(entry)

for pdf_file, trades in grouped_data.items():
    print(f"\n Trades from: {pdf_file}")
    print(json.dumps(trades, indent=4))

print(f"\n Total Trades Extracted: {len(data)}")

with open("trades_output.json", "w") as f:
    json.dump(data, f, indent=4) 