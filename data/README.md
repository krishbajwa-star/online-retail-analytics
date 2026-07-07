# Data

This project uses the **UCI Online Retail** dataset (~541K rows, Dec 2010 - Dec 2011).

Download it from: https://archive.ics.uci.edu/dataset/352/online+retail

Then:
1. Save the Excel file here and export/convert it to `online_retail_raw.csv`
   (or run: `python -c "import pandas as pd; pd.read_excel('data/Online Retail.xlsx').to_csv('data/online_retail_raw.csv', index=False)"`)
2. Run `python src/01_data_cleaning.py` to generate `online_retail_clean.csv`

Data files are gitignored due to size.
