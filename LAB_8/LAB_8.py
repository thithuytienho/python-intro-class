############################################
# Peer Code Review # LAB.8, 2026 (C)       #
# -------------10/18/2026----------------- #
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
#------------------------------------------#
# For research and educational use         #
# only, not for clinical decisions.        #
############################################

# imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

# prompt for dataset
def load_dataset():
    CSV_PATH = input("Enter the dataset filename: ").strip()

    # load cvs
    df = pd.read_csv(CSV_PATH)

    # clean column names to snake_case
    df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False))

    # Remove row names if the CSV includes that column
    if "rownames" in df.columns:
        df = df.drop(columns=["rownames"])

    # display available columns
    print("\navailable columns:")
    for col in df.columns:
        print(col)
    return df

# prompt for variables
def select_variables(df):
    x_col = input("/nEnter the X variable:").strip().lower()
    y_col = input("Enter the Y variable:").strip().lower()

    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError("One or both column names were not found.")

    if x_col == y_col:
        raise ValueError("Choose two different columns for X and Y.")

    # keep only selected columns
    data = df[[x_col, y_col]].copy()

    # convert values to numeric
    for column in (x_col, y_col):
        data[column] = (data[column].astype(str).str.replace(" ", "_", regex=False))
        data[column] = (data[column].astype(str).str.replace(" ", "_", regex=False))

        data[column] = pd.to_numeric(data[column], errors="coerce")
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # remove missing values
    data = data.dropna()

    if len(data) < 2:
     raise ValueError("At least two valid numeric rows are required")

    return data, x_col, y_col

# Improvement 1: optionally perform regression within selected X and Y ranges.
def filter_data_range(data, x_col, y_col):
    answer=input("/nWould you like to limit the X and Y ranges? (yes/no): ").strip().lower()

    if answer != "yes":
        return data.copy()

    try:
        x_min = float(input(f"Minimum value for{x_col}:").strip())
        x_max = float(input(f"Maximum value for{x_col}:").strip())
        y_min = float(input(f"Minimum value for{y_col}:").strip())
        y_max = float(input(f"Maximum value for{y_col}:").strip())
    except ValueError as exc:
        raise ValueError("Please enter numeric values for all range limits.") from exc

    if x_min > x_max or y_min > y_max:
        raise ValueError("Each minimum value must be less than or equal to its maximum")

    filtered_data = data[data[x_col].between(x_min, x_max) & data[y_col].between(y_min, y_max)].copy()

    if len(filtered_data) < 2:
        raise ValueError("Fewer than two rows match those range. Please try wider ranges")

    print(f"Rows before range filtering: {len(filtered_data)}")
    print(f"Rows used for regression: {len(filtered_data)}")

    return filtered_data

# Improvement 2: ask the user how the plot should look.
def get_plot_options(x_col, y_col):
    point_color = input("Scatterplot point color (default steelblue): ").strip() or "steelblue"
    line_color = input("OLS line color (default crimson): ").strip() or "crimson"
    try:
        width_text= input("OLS line width(default 2):").strip()
        line_width= float(width_text) if width_text else 2.0
        if line_width <= 0:
            raise ValueError
    except ValueError as exc:
        raise ValueError("line width must be a positive number") from exc

    grid_answer= input("show gridlines? (yes/no, default yes):").strip().lower()
    show_grid= grid_answer != "no"

    default_title = f"{y_col} vs. {x_col} with OLS regression"
    plot_title= input(f"custom plot title (press Enter for'{default_title}'):").strip() or default_title

    return point_color, line_color, line_width, show_grid, plot_title

# Run the OLS regression and display the plot.
def run_regression(data, x_col, y_col, plot_options):
    point_color, line_color, line_width, show_grid, plot_title = plot_options

    # Add an intercept and fit the ordinary least squares model
    x = sm.add_constant(data[x_col])
    model = sm.OLS(data[y_col],x).fit()

    print("\nOLS regression summary:")
    print(model.summary())

    # Print the main statistics for the assignment
    print(f"Beta O (intercept): {model.params['const']:.4f}")
    print(f"Beta 1(slope): {model.params[x_col]:.6g}")
    print(f"R²: {model.rsquared:.4f}")
    print(f"Rows analyzed: {len(data)}")

    # Calculate points for the fitted OLS line.
    x_line =np.linspace(data[x_col].min(), data[x_col].max(), 100)
    y_line = model.params["const"] + model.params[x_col] * x_line

    # Plot the observations and regression line.
    fig, ax = plt.subplots(figsize=(8,6))
    ax.scatter(data[x_col],data[y_col],alpha=0.6,color=point_color,edgecolor="black",linewidths=0.3,label="observed data",)
    ax.plot(x_line, y_line, color=line_color, linewidth=line_width, label=f"OLS line (R² = {model.rsquared:.3f})")

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(plot_title)
    ax.grid(show_grid, alpha=0.3)

    fig.tight_layout()

    # Allow the user to save the plot.
    save_plot = input ("\nWould you like to save the plot? (yes/no): ").strip().lower()
    if save_plot == "yes":
        output_file = input("enter output filename:").strip()

        if not output_file.endswith(".png"):
            output_file += ".png"

        fig.savefig(output_file,dpi=300, bbox_inches="tight")
        print(f"saved saved plot -> {output_file}")

    # display figure
    plt.show()

if __name__ == "__main__":
    try:
        df = load_dataset()
        data, x_col, y_col = select_variables(df)
        data = filter_data_range(data, x_col, y_col)
        plot_options = get_plot_options(x_col, y_col)
        run_regression(data, x_col, y_col, plot_options)

    except (FileNotFoundError, pd.errors.ParserError, ValueError, KeyError) as error:
        print(f"Error: {error}")