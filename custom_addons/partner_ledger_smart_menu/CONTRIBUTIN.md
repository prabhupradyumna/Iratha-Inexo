
# 🤝 Contributing to Partner Ledger Wizard

Thank you for your interest in contributing to the **Partner Ledger Wizard** Odoo module!  
We welcome all types of contributions — from bug fixes and new features to documentation and UI enhancements.

---

## 🧭 Contribution Workflow

1. **Fork** this repository  
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/partner_ledger_wizard.git
   cd partner_ledger_wizard
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes and **commit** with a clear message:
   ```bash
   git commit -m "Add: ledger summary filter by journal"
   ```
5. **Push** your changes:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a **Pull Request** (PR) to the `main` branch.  
   Make sure your PR includes:
   - A short description of what you changed or added  
   - Screenshots (if applicable)  
   - Reference to related issues (if any)

---

## 🧩 Development Standards

### Code Style
- Follow **Odoo’s official coding guidelines** (PEP8 compliant)
- Use **snake_case** for field and method names.
- Add **docstrings** for all methods, especially compute and action methods.
- Keep logic modular — avoid hardcoding company- or partner-specific data.

Example:
```python
def _compute_ledger_balance(self):
    """Compute net balance (debit - credit) for each partner."""
    for partner in self:
        lines = self.env['account.move.line'].search([...])
        partner.ledger_balance = sum(lines.mapped('debit')) - sum(lines.mapped('credit'))
```

---

### Commit Message Format
Use clear, structured commit messages:
```
Add: new opening balance detection by journal code
Fix: incorrect receipt type detection for cash journals
Refactor: simplified ledger computation query
Docs: updated README with installation steps
```

---

## 🧱 Module Structure

```
partner_ledger_wizard/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py
│   └── partner_ledger_wizard.py
├── reports/
│   ├── report_partner_ledger.xml
│   └── templates.xml
├── views/
│   └── res_partner_view.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

---

## 🧪 Testing

Before submitting a PR:
1. Test in a local Odoo environment (v16 or v17).
2. Verify:
   - The ledger button appears on partner form.
   - Report generates correctly for date range.
   - Opening balance and receipts are classified correctly.
3. Run `odoo-bin -u partner_ledger_wizard` to check for errors.

---

## 🧠 Best Practices

- Avoid direct SQL unless necessary; use ORM where possible.  
- Keep report logic in models, not in templates.  
- Make UI elements (like labels or columns) translatable using `_()`.  
- Use descriptive variable names like `opening_balance`, `ledger_lines`, not `x` or `y`.  
- Reuse computed fields or helper methods to reduce duplication.

---

## 💬 Communication

- For feature requests, open a **GitHub Issue**.
- For general discussions, use the **Discussions** tab.
- For urgent bugs, mark the issue as **bug** and include replication steps.

---

## 🧑‍💻 Contributors

Special thanks to all contributors who help improve this project.  
Your ideas and PRs make this module better for the entire Odoo community. 🙌

---

> 💡 *Keep your PRs small, focused, and well-documented — this helps reviewers merge faster and keeps the codebase clean.*
````

---

Would you like me to also add a **`CODE_OF_CONDUCT.md`** (to make the repo open-source–ready on GitHub and contributor-friendly)? It’s short but builds trust with outside developers.
