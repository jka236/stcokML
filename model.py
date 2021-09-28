from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

def transformFit(spyKeyData):
    y = spyKeyData['outPerform']
    X = spyKeyData.drop(
        columns=['outPerform', 'symbol', 'date', 'forward_date', 'tickerP', 'spyP', 'tickerC', 'spyC', 'eq', 'diff'])

    categorical_cols = ['industry', 'sector']
    numerical_cols = list(set(X.columns.to_list()) - set(categorical_cols))

    # Preprocessing for numerical data
    numerical_transformer = SimpleImputer(strategy='constant')

    # Preprocessing for categorical data
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])

    rf_stock_model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=5)

    my_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                  ('model', rf_stock_model)
                                  ])

    # spilt data
    X_train, X_valid, y_train, y_valid = train_test_split(X, y)

    # Preprocessing of training data, fit model
    my_pipeline.fit(X_train, y_train)

    return my_pipeline