# ShopPulse — Analytics & Metrics Validation Report

This report provides a strict, independent recalculation and audit of all analytical metrics, aggregations, and textual claims displayed in the **ShopPulse** dashboard, verified against the cleaned dataset [`data/processed/cleaned_data.csv`](file:///d:/Programs/ShopPulse/data/processed/cleaned_data.csv).

---

## 1. Executive KPIs & Global Baselines

All metrics independently verified from first principles against 12,199 cleaned rows.

| # | Metric | Dashboard Value | Verified Value | Difference | Status | Verification Formula |
| :-: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | Total Sessions | 12,199 | 12,199 | 0 | **MATCH** | `len(df)` |
| **2** | Total Conversions | 1,908 | 1,908 | 0 | **MATCH** | `sum(df['Revenue'] == True)` |
| **3** | Overall Conversion Rate | 15.64% | 15.64% | 0.00% | **MATCH** | `(1,908 / 12,199) * 100` |
| **4** | Average Session Duration | 22.1 min | 22.07 min | -0.03 min | **MATCH** | `mean(Total_Duration_Min)` (rounded to 1 dec) |
| **5** | Average Pages Visited | 34.9 pages | 34.91 pages | -0.01 pages | **MATCH** | `mean(Total_Pages)` (rounded to 1 dec) |
| **6** | Average Bounce Rate | 2.03% | 2.03% | 0.00% | **MATCH** | `mean(BounceRates) * 100` |

---

## 2. Dimensional Conversion Breakdowns

### 2.1 Conversion by Visitor Type
| Visitor Type | Sessions | Conversions | Dashboard CR | Verified CR | Difference | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Returning_Visitor** | 10,425 | 1,470 | 14.10% | 14.10% | 0.00% | **MATCH** |
| **New_Visitor** | 1,693 | 422 | 24.93% | 24.93% | 0.00% | **MATCH** |
| **Other** | 81 | 16 | 19.75% | 19.75% | 0.00% | **MATCH** |

### 2.2 Conversion by Traffic Segment & Top Sources
| Traffic Dimension | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **High-Converting Niche (7,8,10,20)** | 1,025 | 247 | 8.40% | 24.10% | 24.10% | **MATCH** |
| **Major Channels (1-4)** | 9,375 | 1,454 | 76.85% | 15.51% | 15.51% | **MATCH** |
| **Other Channels** | 1,799 | 207 | 14.75% | 11.51% | 11.51% | **MATCH** |
| — *Traffic Type 2* | 3,910 | 847 | 32.05% | 21.66% | 21.66% | **MATCH** |
| — *Traffic Type 1* | 2,388 | 262 | 19.58% | 10.97% | 10.97% | **MATCH** |
| — *Traffic Type 3* | 2,011 | 180 | 16.48% | 8.95% | 8.95% | **MATCH** |
| — *Traffic Type 4* | 1,066 | 165 | 8.74% | 15.48% | 15.48% | **MATCH** |
| — *Traffic Type 13* | 728 | 43 | 5.97% | 5.91% | 5.91% | **MATCH** |

### 2.3 Conversion by Page View Bucket
| Page View Bucket | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 page** | 479 | 8 | 3.93% | 1.67% | 1.67% | **MATCH** |
| **2-5 pages** | 1,449 | 59 | 11.88% | 4.07% | 4.07% | **MATCH** |
| **6-15 pages** | 3,036 | 341 | 24.89% | 11.23% | 11.23% | **MATCH** |
| **16-30 pages** | 2,861 | 495 | 23.45% | 17.30% | 17.30% | **MATCH** |
| **31+ pages** | 4,374 | 1,005 | 35.86% | 22.98% | 22.98% | **MATCH** |

### 2.4 Conversion by Duration Bucket
| Duration Bucket | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **< 1 min** | 1,289 | 32 | 10.57% | 2.48% | 2.48% | **MATCH** |
| **1-5 min** | 2,335 | 158 | 19.14% | 6.77% | 6.77% | **MATCH** |
| **5-15 min** | 3,398 | 530 | 27.85% | 15.60% | 15.60% | **MATCH** |
| **15-30 min** | 2,423 | 493 | 19.86% | 20.35% | 20.35% | **MATCH** |
| **30+ min** | 2,754 | 695 | 22.58% | 25.24% | 25.24% | **MATCH** |

### 2.5 Monthly Conversion Trend (Chronological)
| Month | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Feb** | 181 | 3 | 1.48% | 1.66% | 1.66% | **MATCH** |
| **Mar** | 1,860 | 192 | 15.25% | 10.32% | 10.32% | **MATCH** |
| **May** | 3,327 | 365 | 27.27% | 10.97% | 10.97% | **MATCH** |
| **Jun** | 284 | 29 | 2.33% | 10.21% | 10.21% | **MATCH** |
| **Jul** | 432 | 66 | 3.54% | 15.28% | 15.28% | **MATCH** |
| **Aug** | 433 | 76 | 3.55% | 17.55% | 17.55% | **MATCH** |
| **Sep** | 448 | 86 | 3.67% | 19.20% | 19.20% | **MATCH** |
| **Oct** | 549 | 115 | 4.50% | 20.95% | 20.95% | **MATCH** |
| **Nov** | 2,979 | 760 | 24.42% | 25.51% | 25.51% | **MATCH** |
| **Dec** | 1,706 | 216 | 13.98% | 12.66% | 12.66% | **MATCH** |

### 2.6 Weekend vs. Weekday Conversion
| Day Type | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Weekday** | 9,341 | 1,409 | 76.57% | 15.08% | 15.08% | **MATCH** |
| **Weekend** | 2,858 | 499 | 23.43% | 17.46% | 17.46% | **MATCH** |

### 2.7 PageValue Tier Conversion
| PageValue Tier | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Zero (0)** | 9,469 | 370 | 77.62% | 3.91% | 3.91% | **MATCH** |
| **Low (0-10)** | 928 | 356 | 7.61% | 38.36% | 38.36% | **MATCH** |
| **Medium (10-40)** | 1,224 | 720 | 10.03% | 58.82% | 58.82% | **MATCH** |
| **High (40+)** | 578 | 462 | 4.74% | 79.93% | 79.93% | **MATCH** |

### 2.8 Exit Risk Profile Conversion
| Exit Risk Profile | Sessions | Conversions | Traffic Share | Dashboard CR | Verified CR | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Engaged** | 10,623 | 1,894 | 87.08% | 17.83% | 17.83% | **MATCH** |
| **High Exit Risk** | 793 | 9 | 6.50% | 1.13% | 1.13% | **MATCH** |
| **Bounced** | 783 | 5 | 6.42% | 0.64% | 0.64% | **MATCH** |

---

## 3. 5-Stage Shopper Conversion Funnel Audit

| Stage | Milestone Definition | Users | % of Initial | Drop-Off Count | Drop-Off % from Prior | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1. All Sessions** | Total Sessions | 12,199 | 100.00% | 0 | 0.00% | **MATCH** |
| **2. Product Browsing** | `ProductRelated >= 1` | 12,167 | 99.74% | 32 | 0.26% | **MATCH** |
| **3. Deep Engagement** | `ProductRelated >= 5` or `Total_Pages >= 5` | 10,632 | 87.15% | 1,535 | 12.62% | **MATCH** |
| **4. Intent / Account Action**| `PageValues > 0` or `Administrative >= 1` | 7,051 | 57.80% | 3,581 | 33.68% | **MATCH** |
| **5. Completed Purchase** | `Revenue == True` | 1,908 | 15.64% | 5,143 | 72.94% | **MATCH** |

---

## 4. Specific Numerical Claims & Discrepancies Audit

### 4.1 Mathematically Supported Claims
1. **PageValue >20x Lift:**
   - Calculation: `High Tier CR (79.93%) / Zero Tier CR (3.91%) = 20.44x`.
   - **Supported:** **YES** ($20.44\text{x} > 20\text{x}$).
2. **New Visitor 1.77x Lift:**
   - Calculation: `New Visitor CR (24.93%) / Returning Visitor CR (14.10%) = 1.7681x` $\approx 1.77\text{x}$.
   - **Supported:** **YES**.
3. **November 25.5% Conversion & ~3,000 Sessions:**
   - Calculation: `760 / 2,979 = 25.51%` ($\approx 25.5\%$) across 2,979 sessions ($\approx 3,000$).
   - **Supported:** **YES**.
4. **Weekend 17.5% vs. Weekday 15.1%:**
   - Calculation: `Weekend = 499 / 2,858 = 17.46%` ($\approx 17.5\%$), `Weekday = 1,409 / 9,341 = 15.08%` ($\approx 15.1\%$). Lift = $+2.38\%$ points ($\approx +2.4\%$).
   - **Supported:** **YES**.
5. **High Exit Risk 1.1% Conversion:**
   - Calculation: `9 / 793 = 1.13%` ($\approx 1.1\%$).
   - **Supported:** **YES**.

---

### 4.2 Identified Discrepancies, Rounding Inconsistencies & Misleading Labels

| # | Discrepancy Location | Dashboard Statement | Verified Value | Difference | Reason / Correction |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **D1** | Tab 5 — Strategy Item 1 | *"The sharpest funnel attrition occurs between Deep Engagement and Intent/Account Action (33.7% drop-off)."* | Stage 4 $\rightarrow$ 5 drops by **72.94%** (5,143 users). Stage 3 $\rightarrow$ 4 drops by **33.68%** (3,581 users). | **Misleading Ranking** | Calling Stage 3 $\rightarrow$ 4 "the sharpest attrition" is incorrect. The sharpest drop-off overall is Stage 4 to Stage 5 (checkout drop-off of 72.94% / 5,143 users). Stage 3 $\rightarrow$ 4 is only the sharpest *browsing / pre-intent* drop-off. |
| **D2** | Tab 5 — Strategy Item 3 | *"Traffic Type 2 drives 32% of volume with a stellar 21.6% conversion rate..."* | Volume: **32.05%**<br>CR: **21.66%** | -0.06% CR | In exact rounding, $21.66\%$ rounds to **21.7%** (or truncated to 21.6%). |
| **D3** | Tab 5 — Strategy Item 3 | *"...Traffic Type 13 delivers 6% of sessions at an anemic 5.8% conversion rate."* | Volume: **5.97%**<br>CR: **5.91%** | -0.11% CR | Exact CR is **5.91%** ($\approx 5.9\%$), not $5.8\%$. (Raw uncleaned was 5.83%, but on cleaned data it is 5.91%). |
| **D4** | Tab 1 Caption vs. Tab 5 Card 1 | Tab 1: *">13x higher PageValues"*<br>Tab 5: *">20x PageValue lift"* | Mean ratio: **13.77x**<br>Tier CR ratio: **20.44x** | Differing metrics | Both numbers are mathematically correct but refer to different metrics: 13.8x refers to *Average PageValue* (27.26 vs 1.98), while 20.4x refers to *Conversion Rate Ratio between Tiers* (79.93% vs 3.91%). Clarifying labels prevents user confusion. |

---

## 5. Conclusion & Action Items

- **Mathematical Soundness:** 100% of underlying analytical calculations in `metrics.py` and `analysis.py` match independent first-principles verification with zero calculation error.
- **Copy Alignment:** In a future update, refine the text in `app.py` for Strategy Item 1 (clarifying "sharpest pre-intent drop-off" vs. checkout drop-off) and tighten decimal rounding for Traffic Types 2 and 13.
