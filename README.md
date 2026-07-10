# AML Sanctions Screening Tool

A Python-based screening tool that checks individuals and companies against public sanctions lists (OFAC SDN, EU Consolidated, UN) using fuzzy name matching. Built as a portfolio project demonstrating AML/KYC compliance domain knowledge.

---

## Features

- Fuzzy name matching — catches variations, transliterations, and abbreviations
- Three verdict levels: Confirmed Match / Possible Match / Clear
- Export results to CSV and JSON for audit trail
- Offline demo mode — built-in sample sanctions list, no internet required
- Live mode — fetches real OFAC SDN data directly from US Treasury

---

## Requirements

- Python 3.9+
- No external libraries required (standard library only)

---

## Usage

```bash
git clone https://github.com/anastasiaabudash-arch/aml-sanctions-screening-tool.git
cd aml-sanctions-screening-tool
python screening_tool.py
```

---

## Scoring Logic

| Score | Verdict |
|-------|---------|
| ≥ 0.88 | Confirmed Match |
| ≥ 0.70 | Possible Match |
| < 0.70 | Clear |

---

## Example Output
NAME                         VERDICT              SCORE    BEST MATCH
Roman Abramovich             CONFIRMED MATCH      1.000    Roman Abramovich
Gazprom OAO                  POSSIBLE MATCH       0.778    Gazprom
John Smith                   CLEAR                0.462    —
SUMMARY: 10 entities screened
Confirmed Matches : 3
Possible Matches  : 1
Clear             : 6

---

## Configuration

```python
FUZZY_THRESHOLD = 0.70   # Minimum score for Possible Match
EXACT_THRESHOLD = 0.88   # Minimum score for Confirmed Match
```

---

## Disclaimer

This tool is built for educational and portfolio purposes. For production AML/KYC compliance, use certified screening solutions such as Refinitiv World-Check or ComplyAdvantage.

---

## Author

Portfolio project | AML/KYC Compliance & Data Analysis
Skills: Python | AML | KYC | OFAC | EU Sanctions | Fuzzy Matching
