import pandas as pd
df = pd.read_csv('/content/drive/MyDrive/MELBOURNE_HOUSE_PRICES_LESS.csv')
df = df.drop_duplicates(subset = ['Suburb','Address','Rooms','CouncilArea','Price'],keep='last')
