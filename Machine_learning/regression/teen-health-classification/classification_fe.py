from sklearn.feature_selection import f_classif
from scipy.stats import chi2_contingency

# 2. Define our target and split features by data type
target = 'depression_label'

# Numerical inputs
numeric_features = [
    'age', 'daily_social_media_hours', 'sleep_hours', 
    'screen_time_before_sleep', 'academic_performance', 
    'physical_activity', 'stress_level', 'anxiety_level', 'addiction_level'
]

# Categorical inputs (including ordinal metrics text)
categorical_features = [
    'gender', 'platform_usage', 'social_interaction_level', 'sleep_quality'
]

# ==========================================
# STEP 1: ANOVA F-Test for Numerical Features
# ==========================================
X_num = df[numeric_features]
y = df[target]

# f_classif computes the ANOVA F-value and its corresponding p-value
f_scores, anova_p_values = f_classif(X_num, y)

anova_summary = pd.DataFrame({
    'Numerical Feature': numeric_features,
    'F-Score': f_scores,
    'p-value': anova_p_values
}).sort_values(by='F-Score', ascending=False).reset_index(drop=True)


# ==========================================
# STEP 2: Chi-Square Test for Categorical Features
# ==========================================
chi2_results = []

for col in categorical_features:
    # Construct a contingency table (cross-tabulation) between the feature and target
    contingency_table = pd.crosstab(df[col], df[target])
    
    # Compute the chi-square statistics
    chi2_stat, p_val, dof, expected = chi2_contingency(contingency_table)
    
    chi2_results.append({
        'Categorical Feature': col,
        'Chi-Square Stat': chi2_stat,
        'p-value': p_val
    })

chi2_summary = pd.DataFrame(chi2_results).sort_values(by='Chi-Square Stat', ascending=False).reset_index(drop=True)


# ==========================================
# STEP 3: Display the Formatted Summaries
# ==========================================
# Helper formatting for clean decimal/scientific notations
def format_p_value(val):
    return f"{val:.4e}" if val < 0.0001 else f"{val:.4f}"

anova_summary['p-value'] = anova_summary['p-value'].apply(format_p_value)
chi2_summary['p-value'] = chi2_summary['p-value'].apply(format_p_value)

print("--- 1. ANOVA F-TEST RESULTS (Numerical Inputs) ---")
print(anova_summary.to_string())

print("\n--- 2. CHI-SQUARE TEST RESULTS (Categorical Inputs) ---")
print(chi2_summary.to_string())