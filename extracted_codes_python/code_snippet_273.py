from sklearn.datasets import load_files 
from sklearn.model_selection import train_test_split, GridSearchCV
import numpy as np
from mlp import MLPClassifier
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# Define a function to extract the person label from the file name
def extract_person_label(file_name): # extract label from the file name and adjust it to 0
    return int(file_name.split('.')[0].replace('subject', '')) - 1  # Subtract 1 to make labels start from 0

yale_dataset_path = "./archive1" # the path to the dataset 

data = []  # List to store image data
labels = []  # List to store labels

for file_name in os.listdir(yale_dataset_path): #list all of the files in the directory
    try:    #passing an exception where .DS_Store is bypassed
        img = plt.imread(os.path.join(yale_dataset_path, file_name)) #loads an image file at the specified path and assigns the resulting image data at the specified file path
    except (IOError, OSError):
        continue

    #print(img)
    data.append(img.flatten())  # Flatten image into a 1D array
    labels.append(extract_person_label(file_name)) #appending the image data to labels

data = np.array(data) # converting the data extracted to numpy.array 
labels = np.array(labels) # # converting the labels extracted to numpy.array


# Split the dataset into training and testing sets
# training size = 0.8
# test_size = 0.2
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
output_labels = len(np.unique(labels))

# reshaping the array to match dimension complexity
y_train = y_train.reshape(-1,1)

# calling the constructor for mlp
mlp = MLPClassifier(input_size=X_train.shape[1], hidden_layers=[128, 64], output_size=output_labels)

# Train the model
mlp.fit(X_train, y_train, learning_rate = 0.1, epochs = 20)

# Obtain predictions
y_pred_encoded = mlp.predict(X_test)

# Obtain predictions
y_pred = mlp.predict(X_test)

# Compute accuracy
accuracy = accuracy_score(y_test, y_pred)

# Compute precision
precision = precision_score(y_test, y_pred, average='micro')

# Compute recall
recall = recall_score(y_test, y_pred, average='micro')

# Compute F1-score
f1 = f1_score(y_test, y_pred, average='micro')

#printing the obtained score
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)
