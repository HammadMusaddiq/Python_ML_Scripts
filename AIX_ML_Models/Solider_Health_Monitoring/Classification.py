import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

#Classification Class
class Classification:
    #train test split
    def train_test_split(df):
        X_train, X_test, y_train, y_test = train_test_split(df.drop('Label', axis=1), df['Label'], test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    #KNN Classifier
    def KNN(X_train, X_test, y_train, y_test, neighbors):
        knn = KNeighborsClassifier(n_neighbors=neighbors)
        knn.fit(X_train, y_train)
        knn_pred = knn.predict(X_test)
        return knn, accuracy_score(y_test, knn_pred)
    
    #Random Forest Classifier
    def RandomForest(X_train, X_test, y_train, y_test, estimators):
        rf = RandomForestClassifier(n_estimators=estimators, random_state=42)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)
        return rf, accuracy_score(y_test, rf_pred)
    
    #Decision Tree
    def DecisionTree(X_train, X_test, y_train, y_test):
        dt = DecisionTreeClassifier(random_state=42)
        dt.fit(X_train, y_train)
        dt_pred = dt.predict(X_test)
        return dt, accuracy_score(y_test, dt_pred)