############################################################
# Logistic and Count-Variable Regression # LAB.9, 2026 (C) #
# -------------10/25/2026--------------------------------- #
# Thi Thuy Tien Ho # thithuytienho@usf.edu                 #
# -------------------------------------------------------- #
# For research and educational use                         #
# only, not for clinical decisions.                        #
############################################################

# Imports
import os
import re
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools import add_constant

# Clean column names to snake_case
def clean_column_names(df):
    df = df.copy()
    df.columns = [re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", col.strip())).strip("_").lower() for col in df.columns]
    return df

# Ask user to select a CSV file
def load_data():
    while True:
        file_path = input("Enter the path to your CSV file:").strip().strip('"')

        try:
            df = pd.read_csv(file_path)
            df = clean_column_names(df)

            print("/nDataset loaded successfully.")
            print("/nAvailable columns:")
            for col in df.columns:
                print(col)

            return df

        except FileNotFoundError:
            print("File not found. Please enter a valid path.")
        except Exception as error:
            print(f"Error loading dataset: {error}")

# Calculate and display VIF
def calculate_vif(data, predictors):
    x = data[predictors].astype(float)

    x = x.loc[:, x.nunique() > 1]

    if x.shape[1] == 0:
        print("Cannot calculate VIF: no varying predictors.")
        return

    x = add_constant(x, has_constant="add")
    vif_df = pd.DataFrame()
    vif_df["Feature"] = x.columns
    vif_df["VIF"] = [variance_inflation_factor(x.values, i) for i in range(x.shape[1])]
    print("/nVariance Inflation Factor (VIF):")
    print(vif_df.to_string(index=False))
    print("-" * 40)

# Logistic regression
def run_logistic(df, predictors, response):
    data = df[predictors + [response]].dropna().copy()

    if data.empty:
        raise ValueError("No complete rows remain after removing missing values.")

    if not set(data[response].unique()).issubset({0,1}):
        raise ValueError(f"The logistic response '{response}' must contain only 0 and 1.")

    if data[response].nunique() != 2:
        raise ValueError("The response must contain both classes: O and 1.")

    print(f"/nComplete cases: {len(data)}")

    x = data[predictors]
    y = data[response].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    print("/nLogistic Regression Results")
    print("-" * 40)
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")

    print("/nClassification Report:")
    print(classification_report(y_test, predictions, zero_division=0))

    print("/nConfusion Matrix:")
    print("Labels are ordered as 0, 1")
    print(confusion_matrix(y_test, predictions, labels=[0, 1]))

    # Fit a statsmodels model to show coefficient significance
    formula = response + " ~ " + " + ".join(predictors)
    print("Fitting statistical model...")
    stats_model = smf.logit(formula=formula, data=data).fit(disp=False)
    print(stats_model.summary())

# Poisson regression
def run_poisson(df, predictors, response):
    data = df[predictors + [response]].dropna().copy()

    if data.empty:
        raise ValueError("No complete rows remain after removing missing values.")

    if not pd.api.types.is_numeric_dtype(data[response]):
        raise ValueError("The Poisson response must be numeric.")

    if (data[response] < 0).any():
        raise ValueError("Poisson response cannot contain negative values.")

    print(f"/nComplete cases: {len(data)}")

    is_integer_count = (
            (data[response] % 1 == 0).all()
            and (data[response] >= 0).all()
    )

    if not is_integer_count:
        print("/nWARNING: The response contains non-integer values. ""It may be a prevalence/rate rather than a count variable. ""Check whether Poisson regression is appropriate.")

    df_scaled = data.copy()

    for col in predictors:
        if not pd.api.types.is_numeric_dtype(df_scaled[col]):
            raise ValueError(f"Predictor '{col}' must be numeric.")

        std = df_scaled[col].std()
        if std == 0 or pd.isna(std):
            raise ValueError(f"Predictor '{col}' has no variation and cannot be scaled.")
        df_scaled[col] = (df_scaled[col] - df_scaled[col].mean()) / std

    # Calculate and display VIF
    calculate_vif(df_scaled, predictors)
    formula = response + " ~ " + " + ".join(predictors)

    # Fit Poisson regression
    print("/nFitting Poisson model...")
    model = smf.poisson(formula=formula, data=df_scaled).fit()

    print("\nPoisson Regression Results")
    print("-" * 40)
    print(model.summary())

    null_model = smf.poisson(formula=response + " ~ 1", data=df_scaled).fit(disp=False)
    pseudo_r2 = 1 - (model.llf / null_model.llf)
    print(f"/nMcFadden-style pseudo-R-squared: {pseudo_r2:.4f}")

# Main program
def main():
    df = load_data()

    print("/nChoose a regression model:")
    print("1. Logistic Regression")
    print("2. Count-Variable Regression (Poisson)")

    choice = input("Enter 1 or 2: ").strip()
    while choice not in ["1", "2"]:
        choice = input("Please enter 1 or 2: ").strip()

    predictors_input = input("/nEnter predictor column names separated by commas: ")
    predictors = [col.strip().lower() for col in predictors_input.split(",")if col.strip()]

    response = input("Enter the response column name: ").strip().lower()

    if not predictors:
        print("You must enter at least one predictor.")
        return

    if len(set(predictors)) != len(predictors):
        print("Duplicate predictor names were entered.")
        return

    if response in predictors:
        print("The response cannot also be a predictor.")
        return

    missing_columns = [col for col in predictors + [response] if col not in df.columns]

    if missing_columns:
        print("These columns were not found:", missing_columns)
        print("Please check the available column names and try again.")
        return

    # Capture printed output so the user can optionally save it
    import io
    from contextlib import redirect_stdout

    output_buffer = io.StringIO()

    try:
        with redirect_stdout(output_buffer):
            if choice == "1":
                run_logistic(df, predictors, response)
            else:
                run_poisson(df, predictors, response)

    except Exception as error:
        print(output_buffer.getvalue())
        print(f"/nError: {error}")
        return

    results = output_buffer.getvalue()
    print(results)

    save = input("/nWould you like to save the output to a .txt file? (yes/no): ")
    if save.strip().lower() in ["yes", "y"]:
        filename = input("Enter the output filename: ").strip()

        if not filename.lower().endswith(".txt"):
            filename += ".txt"

        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(results)

            print(f"Output saved to: {os.path.abspath(filename)}")
        except Exception as error:
            print(f"Could not save output: {error}")

if __name__ == "__main__":
    main()