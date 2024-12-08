# import streamlit as st
# import plotly.express as px
# from pycaret.regression import setup, compare_models, pull, save_model, load_model
# import pandas_profiling
# import pandas as pd
# from streamlit_pandas_profiling import st_profile_report
# import os
# import numpy as np

# # Set page configuration
# st.set_page_config(page_title="aToM.ai - Automated Machine Learning", layout="wide")

# # Initialize session state
# if 'df' not in st.session_state:
#     st.session_state.df = None

# # Function to load and validate data
# def load_data(file):
#     try:
#         df = pd.read_csv(file, index_col=None)
#         return df
#     except Exception as e:
#         st.error(f"Error loading file: {str(e)}")
#         return None

# # Function to convert dataframe to numeric where possible
# def prepare_data(df):
#     for col in df.columns:
#         try:
#             # Try to convert to numeric, fill NaN with 0
#             df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
#         except:
#             # If conversion fails, keep as is
#             continue
#     return df

# # Function to display data types in a readable format
# def display_dtypes(df):
#     dtype_df = pd.DataFrame({
#         'Column': df.dtypes.index,
#         'Data Type': df.dtypes.astype(str)
#     })
#     return dtype_df

# # Function to convert Styler to DataFrame and then to string
# def style_to_string_df(styler):
#     # Convert Styler to DataFrame
#     df = styler.data if hasattr(styler, 'data') else styler
#     # Convert to string
#     return df.astype(str)

# # Load existing dataset if available
# if os.path.exists('./dataset.csv'): 
#     st.session_state.df = pd.read_csv('dataset.csv', index_col=None)

# # Sidebar
# with st.sidebar: 
#     st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
#     st.title("aToM.ai")
#     choice = st.radio("Navigation", ["Upload","Profiling","Modelling", "Download"])
#     st.info("This project application helps you build and explore your data.")

# # Upload page
# if choice == "Upload":
#     st.title("Upload Your Dataset")
#     st.write("Please upload a CSV file with your dataset")
    
#     file = st.file_uploader("Upload Your Dataset", type=['csv'])
#     if file is not None:
#         with st.spinner('Loading data...'):
#             df = load_data(file)
#             if df is not None:
#                 st.session_state.df = df
#                 df.to_csv('dataset.csv', index=None)
#                 st.success("Data loaded successfully!")
                
#                 # Display data info
#                 st.subheader("Dataset Overview")
#                 st.write(f"Shape of dataset: {df.shape}")
                
#                 # Display data types in a table format
#                 st.subheader("Column Data Types")
#                 dtype_df = display_dtypes(df)
#                 st.table(dtype_df)
                
#                 # Display the first few rows
#                 st.subheader("Preview of the data")
#                 st.dataframe(df.head())
                
#                 # Display basic statistics
#                 st.subheader("Basic Statistics")
#                 st.write("Numeric columns statistics:")
#                 st.dataframe(df.describe().astype(str))

# # Profiling page
# if choice == "Profiling": 
#     st.title("Exploratory Data Analysis")
#     if st.session_state.df is not None:
#         try:
#             progress_text = st.empty()
#             progress_text.text("Generating profile report... Please wait.")
            
#             profile_df = st.session_state.df.profile_report()
#             st_profile_report(profile_df)
            
#             progress_text.empty()
#         except Exception as e:
#             st.error(f"Error generating profile report: {str(e)}")
#     else:
#         st.warning("Please upload a dataset first!")

# # Modeling page
# if choice == "Modelling": 
#     st.title("Machine Learning Modeling")
    
#     if st.session_state.df is not None:
#         # Data preparation
#         df_processed = prepare_data(st.session_state.df.copy())
        
#         # Only show numeric columns for target selection
#         numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
#         if len(numeric_columns) > 0:
#             chosen_target = st.selectbox('Choose the Target Column', numeric_columns)
            
#             if st.button('Run Modelling'): 
#                 try:
#                     with st.spinner('Setting up the model...'):
#                         setup(df_processed, target=chosen_target, silent=True, html=False)
#                         setup_df = pull()
#                         st.subheader("Setup Summary")
#                         # Convert setup_df Styler to string DataFrame
#                         setup_str_df = style_to_string_df(setup_df)
#                         st.dataframe(setup_str_df)
                    
#                     with st.spinner('Training models...'):
#                         best_model = compare_models()
#                         compare_df = pull()
#                         st.subheader("Model Comparison")
#                         # Convert compare_df Styler to string DataFrame
#                         compare_str_df = style_to_string_df(compare_df)
#                         st.dataframe(compare_str_df)
#                         save_model(best_model, 'best_model')
#                         st.success("Model training completed!")
                        
#                 except Exception as e:
#                     st.error(f"Error during modeling: {str(e)}")
#         else:
#             st.warning("No numeric columns found in the dataset. Please ensure your data contains numeric features.")
#     else:
#         st.warning("Please upload a dataset first!")

# # Download page
# if choice == "Download": 
#     st.title("Download Trained Model")
#     if os.path.exists('best_model.pkl'):
#         with open('best_model.pkl', 'rb') as f: 
#             st.download_button(
#                 label="Download Model",
#                 data=f,
#                 file_name="best_model.pkl",
#                 mime="application/octet-stream"
#             )
#         st.success("You can now download your trained model!")
#     else:
#         st.warning("No trained model found. Please train a model first!")



 # 
import streamlit as st
import plotly.express as px
from pycaret.regression import setup, compare_models, pull, save_model, load_model
import pandas_profiling
import pandas as pd
from streamlit_pandas_profiling import st_profile_report
import os
import numpy as np

# Previous code remains the same until the Modeling section...
# Set page configuration
st.set_page_config(page_title="aToM.ai - Automated Machine Learning", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None

# Function to load and validate data
def load_data(file):
    try:
        df = pd.read_csv(file, index_col=None)
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# Function to convert dataframe to numeric where possible
def prepare_data(df):
    for col in df.columns:
        try:
            # Try to convert to numeric, fill NaN with 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        except:
            # If conversion fails, keep as is
            continue
    return df

# Function to display data types in a readable format
def display_dtypes(df):
    dtype_df = pd.DataFrame({
        'Column': df.dtypes.index,
        'Data Type': df.dtypes.astype(str)
    })
    return dtype_df

# Function to convert Styler to DataFrame and then to string
def style_to_string_df(styler):
    # Convert Styler to DataFrame
    df = styler.data if hasattr(styler, 'data') else styler
    # Convert to string
    return df.astype(str)

# Load existing dataset if available
if os.path.exists('./dataset.csv'): 
    st.session_state.df = pd.read_csv('dataset.csv', index_col=None)

# Sidebar
with st.sidebar: 
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("aToM.ai")
    choice = st.radio("Navigation", ["Upload","Profiling","Modelling", "Download"])
    st.info("This project application helps you build and explore your data.")

# Upload page
if choice == "Upload":
    st.title("Upload Your Dataset")
    st.write("Please upload a CSV file with your dataset")
    
    file = st.file_uploader("Upload Your Dataset", type=['csv'])
    if file is not None:
        with st.spinner('Loading data...'):
            df = load_data(file)
            if df is not None:
                st.session_state.df = df
                df.to_csv('dataset.csv', index=None)
                st.success("Data loaded successfully!")
                
                # Display data info
                st.subheader("Dataset Overview")
                st.write(f"Shape of dataset: {df.shape}")
                
                # Display data types in a table format
                st.subheader("Column Data Types")
                dtype_df = display_dtypes(df)
                st.table(dtype_df)
                
                # Display the first few rows
                st.subheader("Preview of the data")
                st.dataframe(df.head())
                
                # Display basic statistics
                st.subheader("Basic Statistics")
                st.write("Numeric columns statistics:")
                st.dataframe(df.describe().astype(str))

# Profiling page
if choice == "Profiling": 
    st.title("Exploratory Data Analysis")
    if st.session_state.df is not None:
        try:
            progress_text = st.empty()
            progress_text.text("Generating profile report... Please wait.")
            
            profile_df = st.session_state.df.profile_report()
            st_profile_report(profile_df)
            
            progress_text.empty()
        except Exception as e:
            st.error(f"Error generating profile report: {str(e)}")
    else:
        st.warning("Please upload a dataset first!")
# Modeling page
# Modeling page
if choice == "Modelling": 
    st.title("Machine Learning Modeling")
    
    if st.session_state.df is not None:
        # Data preparation
        df_processed = prepare_data(st.session_state.df.copy())
        
        # Check for numeric columns
        numeric_columns = df_processed.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if len(numeric_columns) > 0:
            # Create tabs for better organization
            tab1, tab2 = st.tabs(["Basic Settings", "Advanced Settings"])
            
            with tab1:
                st.subheader("Basic Model Settings")
                
                # Target selection
                chosen_target = st.selectbox('Choose the Target Column', numeric_columns)
                
                # Basic settings
                test_size = st.slider("Test Set Size (%)", 10, 40, 30) / 100
                fold_number = st.slider("Number of Cross-Validation Folds", 2, 20, 10)
                
            with tab2:
                st.subheader("Advanced Model Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Data Preprocessing
                    st.write("Data Preprocessing")
                    remove_outliers = st.checkbox("Remove Outliers", value=False)
                    if remove_outliers:
                        outliers_threshold = st.slider("Outliers Threshold", 0.0, 1.0, 0.05)
                    
                    normalize = st.checkbox("Normalize Data", value=False)
                    if normalize:
                        normalize_method = st.selectbox("Normalization Method", 
                                                      ["zscore", "minmax", "maxabs", "robust"])
                    
                    feature_selection = st.checkbox("Enable Feature Selection", value=False)
                    if feature_selection:
                        feature_selection_method = st.selectbox("Feature Selection Method",
                                                              ["classic", "boruta"])
                    
                    remove_multicollinearity = st.checkbox("Remove Multicollinearity", value=False)
                    if remove_multicollinearity:
                        multicollinearity_threshold = st.slider("Multicollinearity Threshold", 
                                                              0.1, 1.0, 0.9)
                    
                with col2:
                    # Feature Engineering
                    st.write("Feature Engineering")
                    create_clusters = st.checkbox("Create Clusters", value=False)
                    if create_clusters:
                        cluster_iter = st.slider("Clustering Iterations", 1, 50, 20)
                    
                    polynomial_features = st.checkbox("Create Polynomial Features", value=False)
                    if polynomial_features:
                        poly_degree = st.slider("Polynomial Degree", 2, 5, 2)
                    
                    feature_interaction = st.checkbox("Enable Feature Interaction", value=False)
                    feature_ratio = st.checkbox("Enable Feature Ratio", value=False)
                    
                    transform_target = st.checkbox("Transform Target Variable", value=False)
                    if transform_target:
                        transform_target_method = st.selectbox("Target Transform Method",
                                                             ["box-cox", "yeo-johnson"])
            
            # Model Training Button
            if st.button('Run Modelling'): 
                try:
                    with st.spinner('Setting up the model...'):
                        # Create setup dictionary with correct PyCaret parameters
                        setup_dict = {
                            'data': df_processed,
                            'target': chosen_target,
                            'train_size': 1 - test_size,
                            'fold': fold_number,
                            'remove_outliers': remove_outliers,
                            'normalize': normalize,
                            'feature_selection': feature_selection,
                            'remove_multicollinearity': remove_multicollinearity,
                            'feature_interaction': feature_interaction,
                            'feature_ratio': feature_ratio,
                            'transform_target': transform_target,
                            'silent': True,
                            'html': False
                        }
                        
                        # Add conditional parameters
                        if remove_outliers:
                            setup_dict['outliers_threshold'] = outliers_threshold
                        if normalize:
                            setup_dict['normalize_method'] = normalize_method
                        if feature_selection:
                            setup_dict['feature_selection_method'] = feature_selection_method
                        if remove_multicollinearity:
                            setup_dict['multicollinearity_threshold'] = multicollinearity_threshold
                        if create_clusters:
                            setup_dict['create_clusters'] = True
                            setup_dict['cluster_iter'] = cluster_iter
                        if polynomial_features:
                            setup_dict['polynomial_features'] = True
                            setup_dict['polynomial_degree'] = poly_degree
                        if transform_target:
                            setup_dict['transform_target_method'] = transform_target_method
                        
                        # Setup the experiment
                        setup(**setup_dict)
                        setup_df = pull()
                        st.subheader("Setup Summary")
                        setup_str_df = style_to_string_df(setup_df)
                        st.dataframe(setup_str_df)
                    
                    with st.spinner('Training models...'):
                        best_model = compare_models()
                        compare_df = pull()
                        st.subheader("Model Comparison")
                        compare_str_df = style_to_string_df(compare_df)
                        st.dataframe(compare_str_df)
                        save_model(best_model, 'best_model')
                        st.success("Model training completed!")
                        
                        # Display feature importance if available
                        try:
                            st.subheader("Feature Importance")
                            if hasattr(best_model, 'feature_importances_'):
                                # Get the feature names from the PyCaret setup
                                from pycaret.regression import get_feature_names
                                feature_names = get_feature_names()
                                
                                # Create feature importance DataFrame with correct feature names
                                feature_importance = pd.DataFrame({
                                    'importance': best_model.feature_importances_
                                }, index=feature_names)
                                
                                # Sort by importance
                                feature_importance = feature_importance.sort_values('importance', ascending=True)
                                
                                # Plot using Streamlit
                                st.bar_chart(feature_importance)
                                
                                # Also display as a table
                                st.subheader("Feature Importance Table")
                                st.dataframe(feature_importance)
                            else:
                                st.info("Feature importance not available for this model type")
                        except Exception as e:
                            st.warning(f"Could not display feature importance: {str(e)}")
                            # Print more details about the error for debugging
                            st.write("Error details:", str(e))
                            
                except Exception as e:
                    st.error(f"Error during modeling: {str(e)}")
        else:
            st.warning("No numeric columns found in the dataset. Please ensure your data contains numeric features.")
    else:
        st.warning("Please upload a dataset first!")

# Download page
if choice == "Download": 
    st.title("Download Trained Model")
    if os.path.exists('best_model.pkl'):
        with open('best_model.pkl', 'rb') as f: 
            st.download_button(
                label="Download Model",
                data=f,
                file_name="best_model.pkl",
                mime="application/octet-stream"
            )
        st.success("You can now download your trained model!")
    else:
        st.warning("No trained model found. Please train a model first!")
