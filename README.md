# 🧾 PDF to JSON

A powerful Python tool to extract structured trade data from PDF contract notes issued by Indian stock brokers and convert it into JSON format.

> Built for Zerodha, Dhan, Arihant, Javeri, Axis, JM Financial, and more!

---

## 🚀 Features

- ✅ Auto-detects and parses broker-specific contract notes
- ✅ Supports multiple formats including Zerodha (old & new), Dhan, Arihant (MER), etc.
- ✅ Extracts trade time, security name, quantity, price, and net total
- ✅ Outputs clean structured data in JSON format
- ✅ Extensible with separate parser functions per broker

---

## 📂 Supported Brokers

| Broker Name              | Format Status |
|--------------------------|---------------|
| Dhan                     | ✅ Supported   |
| Arihant (Equity & MER)   | ✅ Supported   |
| Javeri Fiscal            | ✅ Supported   |
| Axis Securities          | ✅ Supported   |
| JM Financial             | ✅ Supported   |
| BP Equities              | ✅ Supported   |
| Greshma                  | ✅ Supported   |
| Kotak Securities         | ✅ Supported   |
| Rudra                    | ✅ Supported   |
| Goldmine                | ✅ Supported   |

---

## 🛠 How It Works

Each broker's contract note has its own layout. This script uses `pdfplumber` to extract text and regular expressions to match and parse trade data fields.

Parsed data includes:
- Trade Date
- Trade Time
- Trade No
- Security / Contract Description
- Buy/Sell Indicator
- Quantity
- Price per Unit
- Net Total

---


