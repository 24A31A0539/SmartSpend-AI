# SmartSpend AI – Personal Financial Intelligence

SmartSpend AI is a Python-based expense analytics dashboard designed to help users understand their spending habits, analyze financial data, and make better budgeting decisions. It combines data analysis, interactive visualizations, and machine learning techniques to provide useful insights into personal expenses.

## Features

- **Expense Overview:** View total expenses, average monthly spending, highest expenses, and transaction counts.
- **Spending Analysis:** Analyze spending patterns through interactive charts and category-wise breakdowns.
- **Transaction Management:** Explore expense records and filter transactions based on available criteria.
- **Expense Forecasting:** Use Linear Regression to estimate future expenses based on historical spending data.
- **Anomaly Detection:** Identify potentially unusual expenses using statistical analysis.
- **Financial Insights:** Understand spending patterns and discover areas where expenses may be reduced.
- **CSV Data Support:** Analyze expense data using CSV files.

## Technologies Used

- **Programming Language:** Python
- **Web Framework:** Streamlit
- **Data Analysis:** Pandas, NumPy
- **Data Visualization:** Matplotlib, Seaborn
- **Machine Learning:** Scikit-learn
- **Data Format:** CSV
- **Version Control:** Git and GitHub

## How It Works

1. Expense data is loaded from a CSV file.
2. Pandas and NumPy are used to process and analyze the data.
3. Interactive charts display spending patterns and expense distributions.
4. Linear Regression estimates future expenses from historical data.
5. Statistical analysis helps identify potentially unusual transactions.
6. The Streamlit dashboard presents the results in an easy-to-understand format.

## Installation and Setup

### Prerequisites

- Python 3.9 or a compatible version supported by the project's dependencies
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/24A31A0539/SmartSpend-AI.git
```

### 2. Navigate to the Project Directory

```bash
cd SmartSpend-AI
```

### 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will start locally. Open the URL shown in your terminal, usually `http://localhost:8501`, in your browser.

## Machine Learning Approach

**Linear Regression:** Used to estimate future expense trends based on historical monthly spending totals.

**Statistical Anomaly Detection:** Used to flag transactions that may differ significantly from typical spending patterns.

These techniques provide estimates and analytical indicators, not guaranteed predictions or financial advice.

## Project Structure

```text
SmartSpend-AI/
├── app.py
├── requirements.txt
├── sample_expense_data.csv
├── README.md
├── runtime.txt
└── .gitignore
```

*Note: The structure above represents the expected main project files. Additional files or folders may exist in the repository.*

## Future Improvements

- Personalized budgeting recommendations
- Monthly savings goals and progress tracking
- Improved forecasting models
- User authentication and secure data storage
- Downloadable financial reports
- Enhanced interactive dashboards

## Author

**Jalaganika Yarramsetti**

- Email: [yarramsettijalaganika@gmail.com](mailto:yarramsettijalaganika@gmail.com)
- LinkedIn: [Jalaganika Yarramsetti](https://www.linkedin.com/in/jalaganika-yarramsetti-ba506632b)
- GitHub: [24A31A0539](https://github.com/24A31A0539)

## License

This project is available for educational and portfolio purposes. A formal open-source license has not been specified.

---

If you find this project useful, feel free to explore the repository and share your feedback.
