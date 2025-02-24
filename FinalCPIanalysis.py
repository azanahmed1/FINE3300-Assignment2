import pandas as pd
import glob
import os

#1. Combine 11 DataFrames into one with correct columns (Item, Month, Jurisdiction, CPI)
file_path = os.path.dirname(os.path.abspath(__file__))  

files = [f for f in glob.glob(os.path.join(file_path, "*.csv")) if "monthly_change_report" not in f and "services_annual_change" not in f]

df_list = []
for file in files:
    df = pd.read_csv(file)
    province = os.path.basename(file).split(".")[0] 
    df['Jurisdiction'] = province 
    df_list.append(df)

cpi_data = pd.concat(df_list, ignore_index=True)

cpi_data = cpi_data.melt(id_vars=['Item', 'Jurisdiction'], var_name='Month', value_name='CPI')

cpi_data['CPI'] = pd.to_numeric(cpi_data['CPI'], errors='coerce')

#2. Print first 12 lines of the new data frame
print("Q2: First 12 rows of the new DataFrame:")
print(cpi_data.head(12))

#3. Compute the average month-to-month change in Food, Shelter, and All-items excluding food & energy
cpi_data = cpi_data.dropna(subset=['CPI'])  
cpi_data = cpi_data[cpi_data['CPI'] > 0]  
cpi_data['Monthly Change'] = cpi_data.groupby(['Jurisdiction', 'Item'])['CPI'].pct_change(fill_method=None) * 100
cpi_data['Monthly Change'] = cpi_data['Monthly Change'].clip(-100, 100)  

avg_monthly_change = cpi_data.groupby(['Jurisdiction', 'Item'])['Monthly Change'].mean().reset_index()
avg_monthly_change['Monthly Change'] = avg_monthly_change['Monthly Change'].round(1)

avg_monthly_change['Monthly Change'] = avg_monthly_change['Monthly Change'].apply(lambda x: f"{x}%" if pd.notna(x) else "N/A")

filtered_avg_monthly_change = avg_monthly_change[avg_monthly_change["Item"].isin(["Food", "Shelter", "All-items excluding food and energy"])]

print("\nQ3: Average Month-to-Month Change in Food, Shelter, and All-items Excluding Food & Energy:")
print(filtered_avg_monthly_change)

#4. Identify the single province with the highest average change
avg_monthly_change['Monthly Change'] = avg_monthly_change['Monthly Change'].str.replace('%', '').astype(float)
highest_avg_change_province = avg_monthly_change.groupby("Jurisdiction")["Monthly Change"].mean().idxmax()
highest_avg_change_value = avg_monthly_change.groupby("Jurisdiction")["Monthly Change"].mean().max()
highest_avg_change_value = f"{highest_avg_change_value:.1f}%"

print("\nQ4: Province with the Highest Average Change for above categories:")
print(f"{highest_avg_change_province} with an average change of {highest_avg_change_value}")

#5. Compute the annual CPI change for services across Canada and all provinces
services_data = cpi_data[cpi_data['Item'] == 'Services']
services_annual_change = services_data.groupby("Jurisdiction")["CPI"].agg(lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0]) * 100).reset_index()
services_annual_change.columns = ["Jurisdiction", "Annual CPI Change (%)"]
services_annual_change["Annual CPI Change (%)"] = services_annual_change["Annual CPI Change (%)"].round(1)

print("\nQ5: Annual CPI Change for Services Across Canada and Provinces:")
print(services_annual_change)

#6. Identify the region with the highest inflation in services
services_annual_change = services_annual_change.dropna(subset=['Annual CPI Change (%)'])

highest_services_inflation = services_annual_change.loc[services_annual_change['Annual CPI Change (%)'].idxmax()]
highest_services_region = highest_services_inflation["Jurisdiction"]
highest_services_value = highest_services_inflation["Annual CPI Change (%)"]

print("\nQ6: Region with Highest Inflation in Services:")
print(f"{highest_services_region} with an annual CPI change of {highest_services_value}%")
