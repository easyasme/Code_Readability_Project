import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler

# Load the CSV data
data = pd.read_csv('csv/code_pypi_readability_complete.csv')

# Prepare the data
X = data[['Style Guide Adherence', 'Variable Name Quality', 'Complexity Score', 'Max Line']]
y = data['Readability Category']
y = y.replace({0: 0, 1: 0, 2: 1, 3: 2, 4: 2})

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Define parameter grid for Decision Tree
dt_param_grid = {
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'criterion': ['gini', 'entropy']
}

# Perform Grid Search for Decision Tree
dt_grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42), dt_param_grid, cv=5, scoring='accuracy', return_train_score=True)
dt_grid_search.fit(X_train_scaled, y_train)

# Get results from Grid Search
cv_results = dt_grid_search.cv_results_
results_df = pd.DataFrame(cv_results)

# Print the best parameters and their accuracy
print("Best parameters found:", dt_grid_search.best_params_)
print(f"Best accuracy: {dt_grid_search.best_score_:.4f}")

# Visualize parameter tuning results
def plot_grid_search_results(results, param1, param2, score='mean_test_score'):
    """
    Plot a heatmap for Grid Search results.
    """
    pivot_table = results.pivot_table(values=score, index=param1, columns=param2)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, annot=True, cmap='YlGnBu')
    plt.title(f'Grid Search Results: {param1} vs {param2}')
    plt.xlabel(param2)
    plt.ylabel(param1)
    plt.show()

# Plot max_depth vs min_samples_split
plot_grid_search_results(results_df, 'param_max_depth', 'param_min_samples_split')

# Plot max_depth vs min_samples_leaf
plot_grid_search_results(results_df, 'param_max_depth', 'param_min_samples_leaf')

# Plot min_samples_split vs min_samples_leaf
plot_grid_search_results(results_df, 'param_min_samples_split', 'param_min_samples_leaf')

# Plot criterion vs max_depth
plot_grid_search_results(results_df, 'param_criterion', 'param_max_depth')
