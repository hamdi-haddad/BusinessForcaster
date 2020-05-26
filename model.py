import numpy as np
import pandas
import matplotlib.pyplot as plt
import pickle
from xgboost import XGBRegressor


import pandas as pd
import sklearn

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline



# Read the data
X_full = pd.read_csv('data/sales_train.csv')

# Remove rows with missing target, separate target from predictors
X_full.dropna(axis=0, subset=['item_cnt_day'], inplace=True)
y = X_full.item_cnt_day
X_full.drop(['item_cnt_day'], axis=1, inplace=True)

# Break off validation set from training data
X_train_full, X_valid_full, y_train, y_valid = train_test_split(X_full, y, 
                                                                train_size=0.8, test_size=0.2,
                                                                random_state=0)
X_train = X_train_full.copy()
X_valid = X_valid_full.copy()



X_train.drop('date',axis=1, inplace=True)
X_valid.drop('date',axis=1, inplace=True)
X_train2 = X_train.copy()
X_valid2 = X_valid.copy()
X_train2.drop('item_price',axis=1,inplace=True)
X_valid2.drop('item_price',axis=1,inplace=True)




#1-predicting item prices for test data
model1 = Pipeline(steps=[('preprocessor',SimpleImputer()) ,
                                  ('model',XGBRegressor(n_estimators=500
                                                                 ,random_state=0))])
model1.fit(X_train2,X_train.item_price)


# Saving model1 to disk
pickle.dump(model1, open('model1.pkl','wb'))




# predicting item_cnt_month
X_train.columns =['date_block_num', 'shop_id', 'item_id', 'item_price']
model2 = Pipeline(steps=[('preprocessor',SimpleImputer()) ,
                                  ('model',XGBRegressor(n_estimators=500
                                                                 ,random_state=0))])
model2.fit(X_train,y_train)



# Saving model2 to disk
pickle.dump(model2, open('model2.pkl','wb'))



'''

# Loading model to compare the results
loaded_model1 = pickle.load(open('model1.pkl','rb'))
print("price for input: " ,loaded_model1.predict([[34,5,5037]]))


loaded_model2 = pickle.load(open('model2.pkl','rb'))
print("item cnt month for input: " ,loaded_model2.predict([[34,5,5037,999]]))'''


