############################################
# Dataset Conversion LAB.5, 2026 (C)       #
#------------------------------------------#
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
############################################

# Import libraries
import pandas as pd

# open the .parquet
df = pd.read_parquet("Maternal Health Risk Data Set.parquet", engine="pyarrow")

# Remove duplicate columns
df = df.loc[:, ~df.columns.duplicated()]

# save it as a .xlsx
df.to_excel("Maternal Health Risk Data Set.xlsx", index=False)

print(df)
