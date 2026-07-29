import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
from sklearn.compose import ColumnTransformer

# load data

df = pd.read_csv('Teen_Mental_Health.csv')
features = ['addiction_level','stress_level','anxiety_level','sleep_hours','daily_social_media_hours','sleep_quality']
X = df[features].copy()
y = df['mental_health_risk_score']
X['sleep_quality'] = X['sleep_quality'].map({'Poor':0,'Fair':1,'Good':2})

# drop collinear feature
X = X.drop(columns=['sleep_hours'])

numeric_cols = ['addiction_level','stress_level','anxiety_level','daily_social_media_hours']
ord_cols = ['sleep_quality']
pre = ColumnTransformer([
    ('num', StandardScaler(), numeric_cols),
    ('ord', 'passthrough', ord_cols)
], remainder='drop')
X_pre = pre.fit_transform(X)
model = RidgeCV(alphas=np.logspace(-3,3,13), cv=5).fit(X_pre, y)
coef = model.coef_
features_out = numeric_cols + ord_cols
print('Ridge alpha:', model.alpha_)
for name, c in zip(features_out, coef):
    print(f'{name}: {c}')
