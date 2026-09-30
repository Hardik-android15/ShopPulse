ShopPulse — Online Shopper Conversion Intelligence

An interactive analytics dashboard for understanding online shopper behaviour, conversion patterns, funnel drop-offs, and high-intent customer segments.

Live Demo: https://shoppulse-m2dprjolm7gumnckchwudj.streamlit.app

GitHub: https://github.com/Hardik-android15/ShopPulse
________________________________________
📊 Overview

ShopPulse is an interactive web-based analytics platform built to analyse online shopping sessions and identify the behavioural patterns that influence purchase 
conversion.

The project transforms raw session-level e-commerce data into actionable insights through:

•	Data cleaning and validation

•	Feature engineering

•	Behavioural segmentation

•	Conversion analysis

•	Funnel analysis    

•	Temporal analysis

•	Interactive visualizations

•	Dynamic filtering

•	Business-oriented insights

The dashboard is built with Python, Pandas, NumPy, Plotly, and Streamlit and is deployed as a live web application.

________________________________________

🎯 Problem Statement

E-commerce websites receive large volumes of visitor traffic, but only a fraction of sessions result in a purchase.

The key challenge is to understand:

•	What differentiates converting and non-converting visitors?

•	How does browsing depth relate to conversion?

•	Does session duration influence purchase behaviour?

•	Which visitor types convert more frequently?

•	Which traffic sources perform better?

•	Where does the largest funnel drop-off occur?

•	How do seasonal and temporal patterns affect conversion?

ShopPulse addresses these questions through an interactive analytics dashboard.

________________________________________

🎯 Objectives

1.	Clean and validate the raw shopper session dataset.

2.	Engineer meaningful behavioural and conversion features.

3.	Analyse visitor, traffic, engagement, and temporal behaviour.

4.	Compare converting and non-converting sessions.

5.	Construct a multi-stage conversion funnel.

6.	Identify major conversion patterns and drop-off points.

7.	Provide an interactive dashboard for exploration and decision support.

________________________________________

📁 Dataset

ShopPulse uses the Online Shoppers Purchasing Intention dataset from the UCI Machine Learning Repository.
Dataset characteristics

Property	Value

Raw sessions	12,330

Raw features	18

Analysed sessions	12,199

Target variable	Revenue

Analysis level	Session

Important variables include:

•	Administrative page views

•	Administrative duration

•	Informational page views

•	Informational duration

•	Product-related page views

•	Product-related duration

•	Bounce rate

•	Exit rate

•	Page value

•	Special day

•	Month

•	Operating system

•	Browser

•	Region

•	Traffic type

•	Visitor type

•	Weekend

•	Revenue

________________________________________

🧹 Data Processing Pipeline

<img width="327" height="733" alt="image" src="https://github.com/user-attachments/assets/0f58662c-f96a-44f2-8a7a-7b9ac431e839" />

Data cleaning

The pipeline performs:

•	Exact duplicate detection and removal

•	Invalid/ghost session detection

•	Category normalization

•	Data type validation

•	Numerical field validation

•	Missing-value handling where applicable

Feature engineering

The project generates behavioural features including:

•	Total Pages

•	Total Session Duration

•	Average Duration per Page

•	Product Page Share

•	Administrative Page Share

•	Informational Page Share

•	Conversion Status

•	Page Value Tier

•	Page View Bucket

•	Duration Bucket

•	Exit Risk Profile

•	Month Number

•	Quarter

•	Season

•	Day Type

•	Traffic Segment

The raw dataset remains unchanged while the processed dataset is generated separately.

________________________________________

📈 Analytical Methodology

ShopPulse analyses shopper behaviour across multiple dimensions.

Visitor Analysis

Comparison of conversion behaviour across:

•	New Visitors

•	Returning Visitors

•	Other visitor categories

Traffic Analysis

Traffic sources are analysed using:

•	Session volume

•	Conversion rate

•	Bounce behaviour

Engagement Analysis

The dashboard evaluates the relationship between:

•	Page depth

•	Session duration

•	Product browsing

•	Page value

•	Conversion

Temporal Analysis

Conversion behaviour is analysed across:

•	Months

•	Weekdays vs weekends

•	Quarters

•	Seasons

Funnel Analysis

The conversion funnel tracks progression from initial sessions to completed purchases.

________________________________________

🔥 Key Verified Findings

Overall Conversion

12,199 analysed sessions resulted in 1,908 conversions, producing an overall conversion rate of:
15.64%

Visitor Behaviour

New visitors recorded a conversion rate of 24.93%, compared with 14.10% for returning visitors.

Page Value

High PageValue sessions had a 20.44× conversion-rate ratio compared with Zero PageValue sessions.

Separately, converting buyers demonstrated 13.77× higher average PageValue than non-buyers.

Monthly Behaviour

November recorded the highest monthly conversion rate at approximately:
25.51%

Weekend Behaviour

•	Weekend conversion: 17.46%

•	Weekday conversion: 15.08%

Funnel Drop-off

The largest overall funnel drop occurs between:

Intent / Account Action → Completed Purchase

with a 72.94% drop-off.

________________________________________

🖥️ Dashboard

Dashboard Overview

 <img width="1917" height="1048" alt="image" src="https://github.com/user-attachments/assets/36608dca-354e-4533-916a-dba9ff59ccc1" />

ShopPulse provides an interactive dashboard with dynamic filters, KPI cards, analytical charts, conversion funnel analysis, and business insights.
Conversion Funnel
 
The funnel visualizes progression from initial sessions to completed purchases and highlights the largest points of user drop-off.
Visitor & Traffic Behaviour
 
This section compares visitor segments and traffic sources using conversion and engagement metrics.
Engagement & Dwell Time
 
Engagement analysis explores relationships between page-view depth, session duration, and conversion behaviour.
Key Insights
 
The dashboard dynamically generates business-oriented insights from the currently selected data slice.
________________________________________

🛠️ Technology Stack

Technology	Purpose

Python	Core analytics

Pandas	Data processing

NumPy	Numerical computation

Plotly	Interactive visualizations

Streamlit	Dashboard & web application

Git / GitHub	Version control & hosting

Streamlit Community Cloud	Live deployment

________________________________________

📂 Project Structure

ShopPulse/

│

├── app.py

├── requirements.txt

├── .gitignore

│

├── data/

│   ├── raw/

│   │   └── online_shoppers_intention.csv
│   │

│   └── processed/

│       └── cleaned_data.csv

│

├── src/

│   ├── data_cleaning.py

│   ├── metrics.py

│   └── analysis.py

│

├── docs/

│   └── ANALYTICS_VALIDATION.md

│

└── screenshots/

	├── dashboard-overview.png

	├── conversion-funnel.png
    
	├── visitor-traffic-analysis.png
    
	├── engagement-analysis.png
    
	└── key-insights.png

________________________________________

▶️ Run Locally

Clone the repository:

git clone https://github.com/Hardik-android15/ShopPulse.git

cd ShopPulse

Create and activate a virtual environment:

python -m venv .venv

Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the dashboard:

streamlit run app.py

The application will open locally at:

http://localhost:8501

________________________________________

☁️ Deployment

ShopPulse is deployed using Streamlit Community Cloud and can be accessed through the live demo link at the top of this README.

The application loads the processed dataset directly and includes a pipeline fallback to regenerate processed data if required.

________________________________________

✅ Analytics Validation

The dashboard metrics were independently recalculated from the cleaned dataset to verify the correctness of:

•	Core KPIs

•	Conversion rates

•	Visitor segmentation

•	Traffic segmentation

•	Page-view buckets

•	Duration buckets

•	Monthly conversion

•	Weekend vs weekday conversion

•	PageValue tiers

•	Exit-risk profiles

•	Five-stage funnel

Detailed verification is available in:

docs/ANALYTICS_VALIDATION.md

________________________________________

🚀 Future Scope

Potential extensions include:

•	Real-time e-commerce event ingestion

•	Automated data pipelines

•	Predictive conversion modelling

•	Customer segmentation

•	Experiment/A-B testing analytics

•	Automated anomaly detection

•	Production data warehouse integration

These are future extensions and are not part of the current prototype.

________________________________________

👨‍💻 Project

ShopPulse — Online Shopper Conversion Intelligence

Built as a data analytics hackathon project focused on transforming shopper session data into actionable conversion intelligence.

Developer: Hardik Kumawat

GitHub: https://github.com/Hardik-android15/ShopPulse

