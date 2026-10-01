############################################
# Dataset Conversion LAB.5, 2026 (C)       #
#------------------------------------------#
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
############################################

# Import libraries
import pandas as pd

# open the .csv
df = pd.read_csv("Maternal Health Risk Data Set.csv")

# Remove duplicate columns
df = df.loc[:, ~df.columns.duplicated()]

# save it as a .parquet
df.to_parquet("Maternal Health Risk Data Set.parquet", engine="pyarrow", index=False)

print(df)
