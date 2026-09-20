# 📊 Customer Engagement & Product Utilization Analytics

An interactive Streamlit dashboard for analyzing customer engagement, product utilization, financial behavior, and churn patterns to support data-driven customer retention strategies.

## 📌 Project Overview

Customer retention in banking depends not only on financial strength but also on customer engagement and relationship depth.

This project analyzes customer behavior to understand how activity levels, product usage, balances, credit card ownership, and other behavioral indicators are associated with customer retention and churn.

The project provides an interactive Streamlit dashboard that helps explore customer segments, identify potential retention risks, and understand product utilization patterns.

---

## 🎯 Problem Statement

Banks may have customers with strong financial profiles who still become disengaged or churn.

The key challenge is to identify behavioral patterns that may indicate retention risk and understand whether deeper product relationships and stronger engagement are associated with customer loyalty.

---

## 🎯 Project Objectives

- Evaluate the relationship between customer engagement and churn.
- Measure the impact of product depth on customer retention.
- Identify inactive customers with high account balances.
- Analyze the retention impact of credit card ownership.
- Assess relationship strength using engagement and product utilization.
- Identify customer segments that may require retention-focused attention.
- Support data-driven customer retention and product strategies.

---

## 📂 Dataset

The project uses a European banking customer dataset containing **10,000 customer records and 14 columns**.

### Main Features

| Feature | Description |
|---|---|
| CustomerId | Unique customer identifier |
| Surname | Customer surname |
| CreditScore | Customer credit score |
| Geography | Customer country |
| Gender | Customer gender |
| Age | Customer age |
| Tenure | Years with the bank |
| Balance | Customer account balance |
| NumOfProducts | Number of banking products used |
| HasCrCard | Credit card ownership indicator |
| IsActiveMember | Customer activity indicator |
| EstimatedSalary | Estimated customer salary |
| Exited | Customer churn indicator |
| Year | Dataset year |

### Data Quality

- Records: **10,000**
- Columns: **14**
- Missing values: **0**
- Duplicate rows: **0**
- Duplicate Customer IDs: **0**
- Dataset year: **2025**

---

## 🔎 Methodology

The analysis follows these major stages:

### 1. Data Ingestion & Validation
- Loaded the banking customer dataset.
- Checked data types and structure.
- Verified missing values.
- Checked duplicate records and Customer IDs.

### 2. Engagement Analysis
Customers are analyzed according to their engagement status:

- Active and engaged customers
- Inactive and disengaged customers
- Active customers with low product usage
- Inactive customers with high balances

### 3. Product Utilization Analysis
The dashboard evaluates:

- Churn rate by number of products
- Single-product vs multi-product customers
- Product depth and retention patterns
- Customer activity across product segments

### 4. Financial Commitment vs Engagement

The analysis explores:

- Balance vs customer activity
- High-balance inactive customers
- Salary and balance patterns
- Potential high-value disengaged customers

### 5. Retention Strength Analysis

Customer relationship strength is examined using:

- Engagement
- Product utilization
- Customer activity
- Retention and churn behavior

---

## 📊 Key KPIs

The dashboard includes important retention and engagement indicators such as:

### Engagement Retention Ratio
Compares retention among active and inactive customers.

### Product Depth Index
Measures product usage among retained customers relative to overall product usage.

### High-Balance Disengagement Rate
Measures the proportion of high-balance customers who are inactive.

### Credit Card Stickiness Score
Compares retention rates between customers with and without credit cards.

### Relationship Strength Index
Combines engagement and product utilization indicators into a relationship-strength measure.

### Core Customer KPIs

- Total Customers
- Churned Customers
- Churn Rate
- Active Customers %
- Average Products
- Average Balance

---

## 📈 Dashboard Features

The Streamlit dashboard provides interactive analysis through:

- Engagement and churn overview
- Product utilization analysis
- Customer retention analysis
- High-balance disengagement monitoring
- Risk segmentation
- Customer-level exploration
- Product utilization explorer
- Geography and gender filters
- Product count filtering
- Balance range filtering
- Salary range filtering
- Engagement status filtering
- Customer status filtering

---

## 🎯 Customer Risk Explorer

The dashboard includes an interactive risk segmentation module that considers multiple customer indicators, including:

- Customer activity
- Product depth
- Account balance
- Churn status

Customers can be explored through different risk levels and individual customer profiles.

---

## 💡 Key Analytical Insights

The dashboard is designed to help identify patterns such as:

- Differences in churn behavior between active and inactive customers.
- Changes in churn across different product-count segments.
- High-balance customers who are not actively engaged.
- Differences in retention associated with credit card ownership.
- Customer segments showing stronger or weaker relationship depth.
- Potential retention-risk customers requiring further attention.

---

## 🛠️ Technologies Used

- **Python**
- **Pandas**
- **Plotly**
- **Streamlit**
- **CSV**
- **GitHub**

---

## 📁 Project Structure

```text
Customer_Engagement_Retention_Analytics/
│
├── app.py
├── European_Bank_Cleaned.csv
├── requirements.txt
└── README.md
