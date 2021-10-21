#Importing libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model

#Import database
df = pd.read_csv('MELBOURNE_HOUSE_PRICES_LESS.csv')

#drop duplicate rows which contain duplicated properties
df = df.drop_duplicates(subset = ['Suburb','Address','Rooms','CouncilArea','Price'],keep='last')

#Separation into two dataframes for unknown price and known price
unknown = df[df.isna().any(axis=1)]
known = df.dropna()

#Creating a train and test split on known
feature_cols = list(known.columns)
feature_cols.remove('Price')
X = known[feature_cols].copy()
y = known['Price'].copy()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=69,stratify=X['Regionname'])

#Feature Engineering
one_hot = ['Type','Method','Regionname']

def feature_eng(df):
    df = sm.add_constant(df)

    for x in one_hot:
        df = pd.get_dummies(df, columns = [x], drop_first=True, prefix = x)

    df.drop(inplace = True, columns = ['Address','SellerG','Suburb','CouncilArea','Date','Postcode','Propertycount'])
    return df
  
#Apply Feature Engineering to X_train
X_train_eng = feature_eng(X_train)
#Elastic Net Regression
reg_en = linear_model.ElasticNet(alpha=0.1)
en_results = reg_en.fit(X_train_eng[cols],y_train)
X_train_eng['en_pred'] = en_results.predict(X_train_eng[cols])

#Metric
X_train_eng['Pred-30'] = X_train_eng['en_pred'] *0.7
X_train_eng['Pred+30'] = X_train_eng['en_pred'] *1.3
X_train_eng['Valid'] = 'No'
X_train_eng.loc[(X_train_eng['Pred-30']<=y_train)&(X_train_eng['Pred+30']>=y_train),'Valid'] = 'Valid'
X_train_eng.loc[X_train_eng['Pred-30'] > y_train,'Valid'] = 'Under'
X_train_eng.loc[X_train_eng['Pred+30'] < y_train,'Valid'] = 'Over'

#Apply feature engineering and predict on X_test
X_test_eng = feature_eng(X_test)
X_test_eng['en_pred'] = en_results.predict(X_test_eng[cols])

#Metric on X_test
X_test_eng['Pred-30'] = X_test_eng['en_pred'] *0.7
X_test_eng['Pred+30'] = X_test_eng['en_pred'] *1.3
X_test_eng['Valid'] = 'No'
X_test_eng.loc[(X_test_eng['Pred-30']<=y_test)&(X_test_eng['Pred+30']>=y_test),'Valid'] = 'Valid'
X_test_eng.loc[X_test_eng['Pred-30'] > y_test,'Valid'] = 'Under'
X_test_eng.loc[X_test_eng['Pred+30'] < y_test,'Valid'] = 'Over'

#Apply feature engineering and predict on unknown
unknown_eng = feature_eng(unknown)
unknown['Price'] = en_results.predict(unknown_eng[cols])

#Concat dataframes
frames = [known, unknown]
full = pd.concat(frames)
full.sort_index(axis=0, inplace=True)

#Export
full.to_csv('full.csv', index=False)
