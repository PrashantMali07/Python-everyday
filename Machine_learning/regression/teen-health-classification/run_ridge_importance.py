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
X = X.drop(columns=['sleep_hours'])

numeric_cols = ['addiction_level','stress_level','anxiety_level','daily_social_media_hours']
ord_cols = ['sleep_quality']
pre = ColumnTransformer([
    ('num', StandardScaler(), numeric_cols),
    ('ord', 'passthrough', ord_cols)
], remainder='drop')
X_pre = pre.fit_transform(X)
model = RidgeCV(alphas=np.logspace(-3,3,13), cv=5).fit(X_pre, y)

print('Intercept:', model.intercept_)
feature_names = numeric_cols + ord_cols
coef = model.coef_
std_importances = np.abs(coef)
for name, c, imp in zip(feature_names, coef, std_importances):
    print(f'{name}: coef={c}, standardized importance={imp}')

print('\nSorted standardized importances:')
for name, imp in sorted(zip(feature_names, std_importances), key=lambda x: -x[1]):
    print(f'{name}: {imp}')
