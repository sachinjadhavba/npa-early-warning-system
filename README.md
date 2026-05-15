# NPA Early Warning Indicator System
### Rule-Based EWI Framework for SME Loan Portfolio Risk Monitoring

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)](https://python.org)
[![Domain](https://img.shields.io/badge/Domain-Credit_Risk-1F4E79?style=flat)](https://finsight-one-4cao.vercel.app/)
[![Author](https://img.shields.io/badge/Author-Sachin_Jadhav-2E75B6?style=flat)](https://www.linkedin.com/in/sachin-jadhav-consulting)
[![Experience](https://img.shields.io/badge/Banking_Experience-19_Years-27AE60?style=flat)](https://www.linkedin.com/in/sachin-jadhav-consulting)

---

## The Problem This Solves

Most lenders discover problem accounts when they hit **90 days overdue** — by then it's already NPA.

This system flags accounts at **Day 15–30** using 8 behavioural and financial triggers — giving credit teams 60–75 days to intervene before classification.

> *"In 19 years of managing SME loan portfolios, I've seen these 8 triggers predict over 70% of NPAs before they were classified."*
> — Sachin Jadhav, Credit Risk Consultant

---

## 8 EWI Triggers

| # | Trigger | Weight | What It Catches |
|---|---------|--------|-----------------|
| T1 | EMI Bounce Frequency | 2 | Cash flow stress — most reliable signal |
| T2 | Cheque Dishonour | 2 | Liquidity crisis — strongest dual-signal with T4 |
| T3 | Monthly Turnover Decline | 2 | Business revenue stress — shows before EMI bounce |
| T4 | High Leverage Ratio | 2 | Over-leveraged borrowers — >3.5x = high risk |
| T5 | DPD Creep | 1 | Early delinquency trend |
| T6 | Account Dormancy | 1 | Business activity proxy |
| T7 | Insurance/Collateral Lapse | 1 | Collateral risk exposure |
| T8 | Industry Stress Flag | 1 | Systematic sector risk |

**Risk Classification:**
- Score 0–2: Normal — standard monitoring
- Score 3–4: Watch — enhanced monthly review
- Score 5–6: Special Mention — RM visit + restructure assessment
- Score 7+: Immediate Action — credit committee escalation

---

## Sample Output

```
======================================================================
  EWI ACTION LIST — WEEKLY CREDIT REVIEW
  Generated: 13 May 2026
  Total Flagged: 47 accounts
======================================================================

  ⚠⚠⚠ A0234 — Borrower 234
  Risk Level   : Immediate Action (Score: 7/12)
  Segment      : SME Manufacturing
  Outstanding  : ₹284.3 Lac
  DPD          : 45 days
  Triggers     : T1(HIGH) T2 T3(HIGH) T4(HIGH) T5
  RM           : RM_B
  Action       : Credit committee escalation — NPA prevention
  -----------------------------------------------------------------

  ⚠⚠⚠ A0089 — Borrower 89
  Risk Level   : Special Mention (Score: 5/12)
  Segment      : Retail Trade
  Outstanding  : ₹156.8 Lac
  DPD          : 15 days
  Triggers     : T1(HIGH) T3(HIGH) T6
  RM           : RM_A
  Action       : Immediate RM visit — restructure assessment
```

---

## Installation & Usage

```bash
git clone https://github.com/sachinjadhavba/npa-early-warning-system.git
cd npa-early-warning-system
pip install -r requirements.txt
python npa_early_warning_system.py
```

**To use with your own portfolio data:**
```python
import pandas as pd
from npa_early_warning_system import score_ewi

# Load your loan portfolio
df = pd.read_csv('your_portfolio.csv')

# Score all accounts
df_scored = score_ewi(df)

# Get flagged accounts
flagged = df_scored[df_scored['ewi_flagged'] == True]
print(f"Accounts requiring action: {len(flagged)}")
```

---

## Requirements

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
```

---

## About the Author

**Sachin Jadhav** — 19 years in BFSI. This EWI framework is based on real-world credit monitoring experience managing ₹500+ Crore SME loan portfolios at IndusInd Bank and CSB Bank.

- 🌐 [FinsightOne](https://finsight-one-4cao.vercel.app/)
- 💼 [LinkedIn](https://www.linkedin.com/in/sachin-jadhav-consulting)
- 📧 jadhav.sachin6290@gmail.com
- 📅 [Book a discovery call](https://calendly.com/jadhav-sachin6290)

---

*Built from real banking experience. Every trigger threshold has been calibrated against live portfolio outcomes.*
