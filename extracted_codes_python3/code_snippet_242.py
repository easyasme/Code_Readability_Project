import os
import re

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

import pyarrow as pa
import pyarrow.parquet as pq

import matplotlib.pyplot as plt
import seaborn as sns

# STATS
# from statsmodels.stats.outliers_influence import variance_inflation_factor

# ML
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelBinarizer
from sklearn.impute import SimpleImputer

from scipy import stats


os.chdir("../")
sns.set_theme(rc={"figure.figsize": (7, 4)}, style="darkgrid")


def read_parquet_file(dir_name: str, file_name: str):
    """Read parquet files based on provided name."""
    parquet_file_path = os.path.join(
        os.path.dirname(__file__), "..", "data", dir_name, f"{file_name}.parquet"
    )
    # Read the Parquet file into a PyArrow Table
    table = pq.read_table(parquet_file_path)

    # Convert the PyArrow Table to a Pandas DataFrame
    df = table.to_pandas()

    return df


def write_parquet_file(df: pd.DataFrame, dir_name: str, file_name: str):
    """Write DataFrame to a Parquet file."""
    # Construct the path to the Parquet file
    parquet_file_path = os.path.join(
        os.path.dirname(__file__), "..", "data", dir_name, f"{file_name}.parquet"
    )

    # Convert DataFrame to PyArrow Table
    table = pa.Table.from_pandas(df)

    # Write the PyArrow Table to Parquet
    pq.write_table(table, parquet_file_path)

    print(
        f"{file_name} has been Successfully written to parquet file in folder {dir_name}."
    )

    return


def ChangeType(df: pd.DataFrame, org_type: str, target_type: str) -> pd.DataFrame:
    """function to change the type of columns>

    Args:
        df:
            DataFrame to change the types
        org_type:
            The initial type we are intended to change.
        target_type:
            The target type to change.

    Returns:
        Pandas DataFrame with changed types.
    """
    selected_cols = df.select_dtypes(org_type).columns
    df.loc[:, selected_cols] = df.loc[:, selected_cols].astype(target_type)
    return df


def plot_car_histogram(df: pd.DataFrame, str_value: str):
    """Plot the histogram of 'OWN_CAR_AGE'."""
    ax = df["OWN_CAR_AGE"].plot(kind="hist", bins=150)
    ax.set_title(f"Distribution of OWN_CAR_AGE {str_value} filling NA values")
    plt.show()
    df["OWN_CAR_AGE"].describe()

    return


def select_numerical_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Select the numerical values from the given DataFrame.

    Args:
        df:
            The initial DataFrame to select numerical values.

    Returns:
        The DataFrame with only the Numerical columns.
    """
    numerical_dtypes = ["int32", "float32", "int64", "float64"]
    df = df.drop(columns=["SK_ID_CURR", "TARGET"])
    numerical_df = df.select_dtypes(numerical_dtypes)
    numerical_columns = numerical_df.columns

    print("Numerical columns are: \n", numerical_columns.tolist(), "\n")

    return numerical_df


def compute_triu_corr_df(corr_matrix: pd.DataFrame) -> pd.DataFrame:
    """Compute the Upper triangle of the correlation DataFrame.

    Args:
        corr_matrix:
            correlation DataFrame.

    Returns:
        A DataFrame containing the upper triangle values of correlation matrix,
        the lower triangle matrix is filled with NA values.
    """
    # Select the upper triangle, not incuding the ones
    upper_triangle_array = np.triu((corr_matrix), k=1)

    # Build the DataFrame
    filtered_corr_df = pd.DataFrame(
        upper_triangle_array,
        index=corr_matrix.index,
        columns=corr_matrix.columns,
    )

    return filtered_corr_df


def compute_entire_correlation(df: pd.DataFrame, threshold: float = 0.7):
    """Find the columns which have high correlation with each other.

    Args:
        df:
            The initila DataFrame containing the variable names as columns and the related
            values for each of them. We wiil select the numerical columns from the gicen DataFrame.
        threshold:
            The threshold value for selecting the high correlation variables.

    """
    # Select Numerical columns
    numerical_df = select_numerical_variables(df)

    # Find the Correlation matrix
    correlation_matrix = numerical_df.corr()

    # use the Upper triangle matrix and create a DataFrame to find the names of the high correlated columns
    filtered_correlation_df = compute_triu_corr_df(correlation_matrix)
    total_list = []

    # Find the Related high correlation values based on threshold value for each column
    for name, row in filtered_correlation_df.iterrows():
        name_list = []
        name_list.append(name)
        col_names = row[(row >= threshold)].index.tolist()
        if len(col_names) != 0:
            name_list.extend(col_names)
            total_list.append(name_list)

    total_correlation_names = pd.DataFrame(total_list)
    print(
        "The final Variables which has higher than threshold correlation are as table below: \n",
        total_correlation_names,
    )

    return


def compute_corr_hist_plot(df: pd.DataFrame, col_list: list):
    """Plot pair wise and show the correlation matrix for specified columns.

    Args:
        df:
            The main DataFrame.
        col_list:
            List of columns to show the pair plot and compute correlation.
    """
    g = sns.pairplot(df[col_list])
    for ax in g.axes.flat:
        ax.set_xlabel(ax.get_xlabel(), fontsize=9)  # Set x-axis label size
        ax.set_ylabel(ax.get_ylabel(), fontsize=9)  # Set y-axis label size
        ax.tick_params(labelsize=9)  # Set tick label size for both axes

    plt.show()
    print(f"Correlation between {len(col_list)} variables: \n", df[col_list].corr())

    return


def find_outliers(
    data_df: pd.DataFrame, col_name: str, outlier_type: str = None
) -> tuple[pd.DataFrame, float, float]:
    """Find the outliers based on InterQuartile Range.

    Args:
        data_df:
            The DataFrame containing the data.
        col_name:
            The name of the column to find the outliers.
        outlier_type:
            If we should find the upper or lower outliers of the data.

    Returns:
        A tuple containing the DataFRame of the outliers, and two float values containig the
        values for Q1 and Q3.
    """
    # Finding Quantiles
    Q1 = data_df[col_name].quantile(0.25)
    Q3 = data_df[col_name].quantile(0.75)
    IQR = Q3 - Q1

    # Define the boundaries
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Find outliers
    if outlier_type == "upper":
        outliers = data_df[(data_df[col_name] > upper_bound)]
    elif outlier_type == "lower":
        outliers = data_df[(data_df[col_name] < lower_bound)]
    else:
        outliers = data_df[
            (data_df[col_name] < lower_bound) | (data_df[col_name] > upper_bound)
        ]

    return outliers, Q1, Q3


def compute_transform_zscore(
    data_df: pd.DataFrame, col_name: str
) -> tuple[pd.DataFrame, StandardScaler]:
    """Compute the zscore of log-transform and replace outliers.

    Args:
        data_df:
            Main DataFrame containig data.
        col_name:
            Name of the column to apply the transformation.

    Returns:
        A tuple containing the DataFrame of the transfomred values for the specified 'col_name' and
        the StandardScaler fitted on the specified column.
    """
    stdscaler = StandardScaler()
    data_df[f"{col_name}_LOG"] = np.log(data_df[f"{col_name}"])

    data_df[f"{col_name}_ZS"] = stdscaler.fit_transform(
        data_df[f"{col_name}_LOG"].values.reshape(-1, 1)
    )

    # Define COnditions for zscore filtering
    zscore_condition_upper = data_df[f"{col_name}_ZS"] <= 3
    zscore_condition_lower = data_df[f"{col_name}_ZS"] >= -3

    # Find the relative Log values to zscores
    zscore_thresh_upper = (
        data_df.loc[zscore_condition_upper, :]
        .sort_values(by=[f"{col_name}_ZS"], ascending=False)
        .iloc[1, :][f"{col_name}_LOG"]
    )
    zscore_thresh_lower = (
        data_df.loc[zscore_condition_lower, :]
        .sort_values(by=[f"{col_name}_ZS"], ascending=True)
        .iloc[1, :][f"{col_name}_LOG"]
    )

    # Define condition to replace extreme values
    replace_condition_upper = data_df[f"{col_name}_LOG"] > zscore_thresh_upper
    replace_condition_lower = data_df[f"{col_name}_LOG"] < zscore_thresh_lower

    # Replace the values
    data_df.loc[replace_condition_upper, f"{col_name}_LOG"] = zscore_thresh_upper
    data_df.loc[replace_condition_lower, f"{col_name}_LOG"] = zscore_thresh_lower

    # Calculate the new zscore values based on LOG data
    data_df[f"{col_name}_ZS"] = stdscaler.fit_transform(
        data_df[f"{col_name}_LOG"].values.reshape(-1, 1)
    )

    return data_df, stdscaler


def substitute_yn_values(data_df: pd.DataFrame, col_names: list) -> pd.DataFrame:
    """Substitue the specified column Y, N values with 1,0

    Args:
        data_df:
            Main DataFrame containing the 'Y' and 'N' values.
        col_names:
            The name of columns which has 'Y', 'N' values.

    Returns:
        Main DataFrame with 'Y', 'N' values sibstitute for 1 and 0.
    """
    for col in col_names:
        data_df[col] = data_df[col].replace({"Y": 1, "N": 0})
    return data_df


def clean_organization_col(data_df: pd.DataFrame):
    data_df["ORGANIZATION_TYPE"] = (
        data_df["ORGANIZATION_TYPE"].apply(
            lambda x: re.sub(r"(type|Type)\s+\d+", "", x, flags=re.IGNORECASE)
            .replace(":", "")
            .strip()
        )
        # .value_counts()
    )
    return data_df


def plot_hist_var_target(
    data_df: pd.DataFrame, col_name: str, log_scale: bool = False, axs=None
):
    """Plot the Histogram of the column with distinct charts for TARGET values."""
    hist_fig = sns.histplot(
        data_df, x=col_name, hue="TARGET", kde=True, log_scale=log_scale, ax=axs
    )
    hist_fig.set(title=f"Chart of {col_name} based on TARGET values")
    hist_fig.set_xlim(data_df[col_name].min(), data_df[col_name].max())

    # plt.show()

    return


def plot_box_var(
    data_df: pd.DataFrame, col_name: str, log_scale: bool = False, axs=None
):
    """Plot the box chart.

    Args:
        data_df:
            Main DatFrame containing all the data.
        col_name:
            The specified column name to plot.
        log_scale:
            If we should apply the Logarithmic scale or not.
        axs:
            Matplotlib axes object to plot the chart.
    """
    box_fig = sns.boxplot(
        data_df,
        x=col_name,
        log_scale=log_scale,
        notch=True,
        flierprops={"marker": "x"},
        width=0.3,
        ax=axs,
    )
    box_fig.set(
        title=f"BoxPlot for distribution of {col_name} values and log_scale: {log_scale}"
    )
    if axs is None:
        plt.show()
    return


def explore_var_vs_target(
    data_df: pd.DataFrame, col_name: str, log_scale: bool = False
):
    """Plot Box and histogram chart of the data.

    This function is mainly used to explore the given data for outliers and the type of
    distribution they has.

    Args:
        data_df:
            Main DataFrame containig data.
        col_name:
            Name of the column to pot.
        log_scale:
            If we should pply the logarithmic scale or not.
    """
    # Initialize the plot
    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(15, 4))

    # Add the Box plot
    plot_box_var(data_df, col_name, log_scale, ax[0])

    # add the histogram plot
    plot_hist_var_target(data_df, col_name, log_scale, ax[1])

    plt.show()
    return


def plot_var_zscore(data_df: pd.DataFrame, col_name: str, log_scale: bool):
    """Plot the zscore transformation of the data.

    Args:
        data_df:
            Main DataFrame containig data.
        col_name:
            Name of the column to plot.
        log_scale:
            if we should apply Log transformation or not.
    """
    plot_df = data_df.copy()
    if log_scale:
        plot_df.loc[:, col_name] = np.log(plot_df[col_name].values)

    plot_df.loc[:, col_name] = stats.zscore(plot_df[col_name], nan_policy="omit")

    fig = sns.histplot(plot_df, x=col_name, hue="TARGET", kde=True)
    fig.set_title(
        f"Disrtribution of Z-Transform of {col_name} based on target values, log_scale is {log_scale}"
    )
    plt.tight_layout()
    plt.show()

    return


def transform_test_data_zscore(
    test_data: pd.DataFrame, col_name: str, apply_log: bool, std_scaler: StandardScaler
) -> np.ndarray:
    """Transform the specified column to standard scale.

    Args:
        test_data:
            Main DataFrame containing data.
        col_name:
            The name of the specified column to transform
        apply_log:
            If we should apply the log transformation or not.
        std_scaler:
            The standard scaler object fitted on the train data.

    Returns:
        Array containing the transformed values of the specified column.
    """
    array_values = test_data[col_name].values
    if apply_log:
        array_values = np.log(array_values)
    std_values = std_scaler.transform(array_values.reshape(-1, 1))

    return std_values


def find_replace_array_size(df: pd.DataFrame, val_name: str):
    # Replacing condition
    replace_cond = (df["OCCUPATION_TYPE"].isna()) & (df["NAME_INCOME_TYPE"] == val_name)

    # Length of replacing array
    replace_len = df[replace_cond].shape[0]

    return replace_cond, replace_len


def replace_occupation_nan(
    data_train: pd.DataFrame, data_test: pd.DataFrame, income_type_val: str
):
    working_occupation = data_train[
        (data_train["NAME_INCOME_TYPE"] == income_type_val)
    ]["OCCUPATION_TYPE"].value_counts(dropna=True, normalize=True)

    # Use the values which are repeated more than 10% of the time
    working_occupation = working_occupation[(working_occupation >= 0.1)]

    # Normalize
    working_occupation = working_occupation / sum(working_occupation)

    replace_condition, replace_size = find_replace_array_size(
        data_train, income_type_val
    )

    # Using the probabilities to egenrate random values
    random_list = np.random.choice(
        working_occupation.index.tolist(),
        size=replace_size,
        p=working_occupation.values,
    ).tolist()

    data_train.loc[replace_condition, "OCCUPATION_TYPE"] = random_list

    # Apply the probabilities to the test data
    replace_condition, replace_size = find_replace_array_size(
        data_test, income_type_val
    )

    test_random_list = np.random.choice(
        working_occupation.index.tolist(),
        size=replace_size,
        p=working_occupation.values,
    ).tolist()

    data_test.loc[replace_condition, "OCCUPATION_TYPE"] = test_random_list

    return data_train, data_test


def find_na_cols(data_df: pd.DataFrame, na_thresh: float = 30):
    """

    Args:
        na_thresh:
            Value threshold for selecting the na values, in percent
    """
    na_percent_values = data_df.isna().sum(axis=0) / data_df.shape[0] * 100
    na_cols = (na_percent_values <= na_thresh) & (na_percent_values > 0)

    print("* The percentage of NA values in each column: \n")

    print(
        data_df.loc[:, na_cols].isna().sum(axis=0).sort_values(ascending=False)
        / len(data_df)
        * 100,
        "\n",
    )

    print("* The information about the NA columns: \n")

    # Capture DataFrame info as a string
    info_string = data_df.loc[:, na_cols].info(memory_usage="deep", show_counts=True)

    # Print the formatted string
    print(info_string)

    return


def impute_na_cols(data_df: pd.DataFrame, select_cols: list):
    knn_imputer = KNNImputer(n_neighbors=5)
    impute_array = knn_imputer.fit_transform(data_df[select_cols])

    sns.pairplot(pd.DataFrame(data=impute_array, columns=select_cols))
    plt.show()

    data_df.loc[:, select_cols] = impute_array

    return data_df, knn_imputer


# def find_na_cols(data_df: pd.DataFrame):
#     na_series = data_df.isna().sum()
#     na_series = na_series[(na_series != 0)]
#     na_cols = na_series.index

#     # See the Null values from low to high
#     print(na_series.sort_values(ascending=True))

#     print("Number of Null columns: {}".format(len(na_series)))

#     return
