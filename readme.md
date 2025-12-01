# Fraud Transaction Rule Engine (Python)

## Introduction

This project is a simulator for a **Rule Engine** written in Python, designed to monitor and detect **suspicious financial transactions** (Fraud Detection).

The project demonstrates key skills in **data analytics, business rule implementation, system optimization,** and **reporting**, all of which are required for a Fraudulent Transaction Countermeasures Specialist role.

---

## Project Goals

1.  **Rule Implementation and Testing:** To create three distinct behavioral and temporal rules for flagging high-risk transactions.
2.  **Sequential Analysis:** To utilize time windows and grouping (`groupby()`, `rolling()`) for analyzing the transaction patterns of individual clients.
3.  **Efficient Reporting:** To generate a report in Excel format, which is crucial for further analysis and optimization.

---

## Technology Stack

* **Language:** Python 3.x
* **Libraries:** Pandas, NumPy, `openpyxl` (for Excel export)

### Prerequisites

Ensure you have all the necessary libraries installed:

```bash
pip install pandas numpy openpyxl
```

## Implemented Analytical Rules

The rule engine implements three core monitoring mechanisms:

### Rule 1: Geo-Velocity Check (Geographically Impossible Transactions)

* **Logic:** Flags a large-sum foreign transaction ($>1000$ PLN) if it occurs within **<6 hours** of a transaction in Poland. This indicates potential cloned card usage across different continents.

### Rule 2: Multiple Failed Attempts in a Short Time

* **Logic:** Flags the current transaction as suspicious if the `Client_ID` had **failed transactions** within the last **30 minutes**. This suggests automated card testing attempts.


### Rule 3: Abnormal Transaction Amount (Amount Deviation)

* **Logic:** Flags a transaction whose amount is (3.0 times) higher than that client's historical **average amount of successful transactions**. This helps detect sudden, atypical spending profiles.

---

## Results and Analytical Insights

After running on the dataset (10,000 records), the rule engine produced the following summary:

* **Total Number of Actual Fraud Cases (TP + FN)** | 193 | The number of transactions that were truly fraudulent (based on the manual flag in the synthetic data). |
* **Number of Transactions Flagged as Suspicious** | 1093 | Transactions flagged by the rules (TP + FP). |
