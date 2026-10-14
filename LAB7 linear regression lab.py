###############################################
# Lab 7- OLS Regression and Scatterplots      #
# Kenda Breish | HSC4933 | 9/07/2026          #
# Loads a user-selcted dataset, cleans        #
# column names to snake_case, creates         #
# scatterplots, performs OLS regression,      #
# displays regression statistics, and         #
# optionally saves figures                    #
# for educational use only                    #
###############################################


# imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

# prompt for dataset
CSV_PATH = input("Enter the dataset filename: ").strip()

# load cvs
df = pd.read_csv(CSV_PATH)

# clean column names to snake_case
df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_"))

for column in df.columns:
    if df[column].name =="rownames":
        df.drop(column, axis=1, inplace=True)

# display available columns
print("\navailable columns:")
for col in df.columns:
    print(col)

# prompt for variables
x_col = input("/nEnter the X variable:").strip().lower()
y_col = input("Enter the Y variable:").strip().lower()

# Make sure the column exist
if x_col not in df.columns or y_col not in df.columns:
    print("Error: One of both column names were not found.")
    raise SystemExit

# keep only selected columns
data = df[[x_col, y_col]].copy()

# convert values to numeric
data[x_col] = (data[x_col].astype(str).str.replace(" ", "_", regex=False))
data[y_col] = (data[y_col].astype(str).str.replace(" ", "_", regex=False))

#Convert the selected columns to numeric values
data[x_col] = pd.to_numeric(data[x_col], errors="coerce")
data[y_col] = pd.to_numeric(data[y_col], errors="coerce")

# remove missing values
data = data.dropna()

# Display available rows
print(f"/nRows available for regrission: {len(data)}")

# create scatterplot
fig, ax = plt.subplots(figsize=(8, 6))

ax.scatter(data[x_col],data[y_col],alpha=0.6,edgecolor="k",linewidths=0.3,)

ax.set_xlabel(x_col)
ax.set_ylabel(y_col)
ax.set_title(f"{y_col} vs {x_col} (n= {len(data)})")
ax.grid(alpha=0.3)

fig.tight_layout()

# save scatterplot
save_scatter = input ("\nwould you like to save the sctaterplot? (yes/no): ").strip().lower()

if save_scatter.lower() == "yes":
    scatter_file = f"{df[x_col]}vs_{y_col}.png"

    fig.savefig(scatter_file,dpi=300)
    print(f"saved scatterplot -> {scatter_file}")

# perform OLS regression
x = sm.add_constant(data[x_col])
model = sm.OLS(data[y_col],x).fit()

# print regression summary
print("\nOLS regression summary:")
print(model.summary())

# print values needed for trends document
print("\nregression statistics:")
print("-----------------------")
print("β0 (intercept):", model.params["const"])
print("β1 (slope):", model.params[x_col])
print("R²:", model.rsquared)

# create regression line
x_line =np.linspace(data[x_col].min(), data[x_col].max(), 100)
y_line = model.params["const"] + model.params[x_col] * x_line

# plot regression line
ax.plot(x_line, y_line, color="crimson", linewidth=2, label=f"OLS line (R² = {model.rsquared:.3f})")

ax.set_title(f"{y_col} vs {x_col} with OLS regression (n= {len(data)})")
ax.legend()

# save regression figure
save_regression = input ("\nwould you like to save the scatterplot with regression plot? (yes/no): ").strip().lower()

if save_regression.lower() == "yes":
    ols_file = input(
        "enter regression figure file name (example: fig_2.png): "
    ).strip()
    fig.savefig(ols_file, dpi=300)
    print(f"saved scatterplot with OLS line -> {ols_file}")

# display figure
plt.show()