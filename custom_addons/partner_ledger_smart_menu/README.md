
# 🧾 Partner Ledger Wizard – Odoo Custom Module

---

## 📘 Overview

The **Partner Ledger Wizard** module adds a fast, user-friendly way to view and print **partner-wise ledger reports** in Odoo.  
It lets you instantly analyze receivable/payable balances, opening balances, and all financial movements for a specific customer or vendor — right from the Partner form.

This module is designed for accounting teams and developers who want better visibility and customization of partner-level transactions.

---

## ✨ Key Features

✅ **Ledger Balance on Partner Form** — computed real-time from posted move lines  
✅ **Ledger Button** — opens a wizard for report generation  
✅ **Dynamic Date Range Filtering**  
✅ **Smart Transaction Detection**
- Automatically identifies *Opening Balances* (e.g. `999999`, `OPN`, “Opening”)  
- Classifies *Receipts* via Bank/Cash journals  
- Distinguishes *Sales, Purchases, Credit/Debit Notes,* and *Journal Entries*  
✅ **Printable QWeb Report** (HTML/PDF)  
✅ **Clean Table Layout** with totals and running balance  

---

## 🧩 Technical Details

### 1️⃣ Model: `res.partner`
- Adds a computed monetary field `ledger_balance`
- Adds a stat button to open the ledger wizard
- Quick access to ledger via Partner form view

### 2️⃣ Model: `partner.ledger.wizard`
- Handles date input and partner selection
- Calculates opening balance before start date
- Fetches and classifies all partner transactions
- Provides structured data to QWeb report

### 3️⃣ XML Views
- Button added inside Partner form’s button box  
- QWeb report with styled table and totals row  
- Report action defined for PDF/HTML generation

---

## 🖥️ User Flow

1. Navigate to **Contacts → Select a Partner**  
2. Click the **Ledger** stat button (📘 icon)  
3. Choose **Start Date** and **End Date**  
4. View or Print the **Partner Ledger Report**

---

## ⚙️ Installation

1. Copy this module folder to your Odoo custom addons directory.  
2. Update your app list:
   ```bash
   odoo -u all
   ```
3. Install **Partner Ledger Wizard** from the Odoo Apps menu.  
4. Open any partner record → click **Ledger** to generate a report.

---

## 🧮 Example Report Output

| Date       | Voucher No  | Type            | Debit    | Credit   | Balance  |
|-------------|-------------|-----------------|----------:|----------:|----------:|
|             |             | **Opening Balance** | 0.00     | 0.00     | 8,560.00 |
| 01-04-2025  | INV/2025/001 | Sale           | 5,000.00 | 0.00     | 13,560.00 |
| 05-04-2025  | PAY/2025/001 | Receipt        | 0.00     | 3,560.00 | 10,000.00 |
|             |             | **Total**       | 5,000.00 | 3,560.00 | 10,000.00 |

---

## 🤝 Contributing

We’d love community contributions to make this module even better!  
You can help with:
- Adding new ledger filters or transaction types  
- Improving multi-currency support  
- Enhancing report visuals  
- Writing tests or improving documentation  

### 🛠 How to Contribute
1. Fork this repository  
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature: your-feature-name"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request 🎉

---

## 📜 License

This project is licensed under the **AGPL-3.0 License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Developed by:** Irshad K T  
**Tech Stack:** Odoo 19 | Python | QWeb | XML  
**Tags:** `#Odoo` `#Python` `#ERP` `#Accounting` `#OpenSource` `#PartnerLedger`

---

> 💡 *A clean, simple, and powerful ledger reporting tool that bridges usability and financial clarity in Odoo.*
````

---

