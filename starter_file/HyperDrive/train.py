from sklearn.linear_model import LogisticRegression
import argparse
import os
import numpy as np
from sklearn.metrics import mean_squared_error
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
from azureml.core.run import Run
from azureml.data.dataset_factory import TabularDatasetFactory
import joblib
from sklearn.metrics import confusion_matrix


def preprocess_data(data):
    x_df = data.to_pandas_dataframe()
    y_df = x_df.pop("DEATH_EVENT")
    return (x_df, y_df)


def main():
    # Add arguments to script
    parser = argparse.ArgumentParser()

    parser.add_argument('--C', type=float, default=1.0, help="Inverse of regularization strength. Smaller values cause stronger regularization")
    parser.add_argument('--max_iter', type=int, default=100, help="Maximum number of iterations to converge")

    args = parser.parse_args()
    
    run = Run.get_context()

    run.log("Regularization Strength:", np.float(args.C))
    run.log("Max iterations:", np.int(args.max_iter))
    
    # Create TabularDataset using TabularDatasetFactory
    # Data is located at:
    # "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv"
    dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00519/heart_failure_clinical_records_dataset.csv"
    dataset = TabularDatasetFactory.from_delimited_files(path=dataset_url)
    data_df = dataset.to_pandas_dataframe()
    
    data_df.describe()
    data_df.head()

    # Split data to features and labels dataframe
    x, y = preprocess_data(data_df)

    # Split data into train and test sets.
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
    
    x_train.take(5).to_pandas_dataframe()

    model = LogisticRegression(C=args.C, max_iter=args.max_iter).fit(x_train, y_train)

    # Test the model and create a confusion matrix
    ypred = model.predict(x_test)
    cmatrix = confusion_matrix(y_test, ypred)

    # Visualize the confusion matrix
    pd.DataFrame(cmatrix).style.background_gradient(cmap='Blues', low=0, high=0.9)
    
    accuracy = model.score(x_test, y_test)
    run.log("Accuracy", np.float(accuracy))
    
    os.makedirs('outputs', exist_ok=True)
    joblib.dump(model, 'outputs/model.joblib')

if __name__ == '__main__':
    main()
