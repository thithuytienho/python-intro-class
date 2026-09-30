############################################
# IC # 4 # Pandas and Numpy Data Cleaning  #
#------------------------------------------#
# Thi Thuy Tien Ho # HSC4933.005 # 9/30/26 #
############################################

# Imports
import pandas as pd
import numpy as np

# Load csv
df = pd.read_csv("eye_health.csv")

# Print csv stats before cleaning
print(df.shape,
      df.dtypes,
      df.isna().sum(), # Print total number of NaN values
      df.nunique(),
      sep="/n")

# Print number of duplicated values
print("Duplicates:" , df.duplicated().sum())

df = df.dropna(axis=1, how="all") # Drop columns with no data (only NaN)
df = df.drop(columns = [c for c in df.columns if c.endswith("ID")]) # Drop columns that end in "ID"

df = df.dropna(subset=[]) # Drop rows with no value in the column "Data_Value"
df = df.drop(columns=["Geolocation", "Data_Value_Footnote_Symbol", "Data_Value_Footnote","StateAbbr", "NonWeightedSample", "Geographic Level", "Numerator"])


df.columns = df.columns.str.lower().str.replace(" ", "_") # Make column headers snake_case
df["error"] = (df["high_confidence_limit"] - df["low_confidence_limit"]) / 2 # Create new column "ci_width" and
df["prevalence_level"] = np.select([df["data_value"] < 5, df["data_value"] <= 7], ["Low", "Medium"], "High") # Create prevalence level description


df.to_csv("eye_health_2022_clean.csv", index=False) # Save to csv the different name
print(pd.read_csv("eye_health_2022_clean.csv").shape == df.shape) # Print t/f if dimensions match
print(pd.read_csv("eye_health_2022_clean.csv").shape) # Print saved file dimensions
print(pd.read_csv("eye_health_2022_clean.csv").head) # Print dataframe head (first 5 lines)

