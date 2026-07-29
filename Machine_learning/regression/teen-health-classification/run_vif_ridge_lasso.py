import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV, LassoCV, LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.compose import ColumnTransformer

# load
try:
    df = pd.read_csv('Teen_Mental_Health.csv')
except Exception as e:
    print('Failed to read dataset:', e)
    raise

# selected features
features = ['addiction_level','stress_level','anxiety_level','sleep_hours','daily_social_media_hours','sleep_quality']
missing = set(features) - set(df.columns)
if missing:
    print('Missing features from dataset:', missing)
    raise SystemExit(1)

X = df[features].copy()
y = df['mental_health_risk_score']

# ordinal encode
X['sleep_quality'] = X['sleep_quality'].map({'Poor':0,'Fair':1,'Good':2})

# prepare numeric subset for VIF
X_vif = X.select_dtypes(include=[np.number]).copy()

# compute VIF
try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    def compute_vif(df_):
        X_mat = df_.values
        vifs = [variance_inflation_factor(X_mat, i) for i in range(X_mat.shape[1])]
        return pd.DataFrame({'feature':df_.columns,'VIF':vifs})
    vif_df = compute_vif(X_vif)
except Exception:
    # fallback
    def compute_vif_fallback(df_):
        vifs=[]
        for col in df_.columns:
            X_ = df_.drop(columns=[col])
            y_ = df_[col]
            model = LinearRegression()
            model.fit(X_, y_)
            r2 = model.score(X_, y_)
            vifs.append(1.0/(1.0-r2) if r2 < 0.999 else np.inf)
        return pd.DataFrame({'feature':df_.columns,'VIF':vifs})
    vif_df = compute_vif_fallback(X_vif)

print('\nInitial VIF:')
print(vif_df.to_string(index=False))

# iterative drop >5
X_iter = X_vif.copy()
dropped = []
while True:
    try:
        try:
            vif_curr = compute_vif(X_iter)
        except NameError:
            vif_curr = compute_vif_fallback(X_iter)
    except Exception as e:
        print('Error computing VIF:', e)
        break
    high = vif_curr[vif_curr['VIF']>5]
    if high.empty:
        break
    drop_feat = high.sort_values('VIF',ascending=False).iloc[0]['feature']
    dropped.append(drop_feat)
    X_iter = X_iter.drop(columns=[drop_feat])

print('\nDropped features due to high VIF:', dropped)
print('\nFinal VIF:')
print(vif_curr.to_string(index=False))

# Prepare preprocessing
numeric_cols = [c for c in ['addiction_level','stress_level','anxiety_level','sleep_hours','daily_social_media_hours'] if c in X_iter.columns]
ord_cols = [c for c in ['sleep_quality'] if c in X_iter.columns]

from sklearn.compose import ColumnTransformer
pre = ColumnTransformer([
    ('num', StandardScaler(), numeric_cols),
    ('ord', 'passthrough', ord_cols)
], remainder='drop')

X_pre = pre.fit_transform(X_iter)

# compare models
ridge = RidgeCV(alphas=np.logspace(-3,3,13), cv=5)
lasso = LassoCV(cv=5, max_iter=5000)

ridge_scores = cross_val_score(ridge, X_pre, y, scoring='neg_mean_squared_error', cv=5)
lasso_scores = cross_val_score(lasso, X_pre, y, scoring='neg_mean_squared_error', cv=5)

print('\nRidge CV RMSE:', np.sqrt(-ridge_scores.mean()))
print('Lasso CV RMSE:', np.sqrt(-lasso_scores.mean()))
