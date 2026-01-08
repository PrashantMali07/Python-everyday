

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
import streamlit as st


## Loading all the saved models

model = load_model('churn_model.h5', compile=False)

## Loading scaler model
with open('scaler.pkl','rb') as f:
    scaler = pickle.load(f)

## Loading gender encoder model
with open('encoder_gender.pkl','rb') as f:
    gender_encoder = pickle.load(f)

## Loading Geography encoder model
with open('encoder_geography.pkl','rb') as f:
    geography_encoder = pickle.load(f)


## Initializing the Streamlit App
st.title("Customer Churn Prediction App")
st.write("Enter the customer details to predict churn probability.")

## Getting user input
credit_score = st.number_input('Credit Score', min_value=350, max_value=850)
st.write("Credit Score:", credit_score)
geography = st.selectbox('Geography',geography_encoder.categories_[0])
st.write("Geography:", geography)
gender = st.selectbox('Gender',gender_encoder.classes_)
st.write("Gender:", gender)
age = st.slider('Age',18,92)
st.write("Age:", age)
tenure = st.slider('tenure',0,10)
st.write("Tenure:", tenure)
balance = st.number_input('Balance')
st.write("Balance:", balance)
products_count = st.slider('Number of Products',1,4)
st.write("Number of Products:", products_count)
has_cr_card = 1 if st.selectbox('Has Credit Card', ['Yes', 'No']) == 'Yes' else 0
st.write("Has Credit Card:", has_cr_card)
is_active_member = 1 if st.selectbox('Is Active Member', ['Yes', 'No']) == 'Yes' else 0
st.write("Is Active Member:", is_active_member)
estimated_salary = st.number_input('Estimated Salary')
st.write("Estimated Salary:", estimated_salary)

# Preparing the input data dictionary (use scalar values, not nested lists)
input_data = {
    'CreditScore': credit_score,
    'Geography': geography,
    'Gender': gender,
    'Age': age,
    'Tenure': tenure,
    'Balance': balance,
    'NumOfProducts': products_count,
    'HasCrCard': has_cr_card,
    'IsActiveMember': is_active_member,
    'EstimatedSalary': estimated_salary
}

 ## Convert the data into a DataFrame
input_df = pd.DataFrame([input_data])

## Encode the Gender column (label encoding)
input_df['Gender'] = gender_encoder.transform(input_df['Gender'])

## Encode the Geography data (one-hot)
encoded_geo = geography_encoder.transform(input_df[['Geography']])
if hasattr(encoded_geo, 'toarray'):
    encoded_geo = encoded_geo.toarray()
encoded_geo_df = pd.DataFrame(encoded_geo, columns=geography_encoder.get_feature_names_out(['Geography']))

## Drop the original Geography column and concatenate the encoded columns
final_input_df = pd.concat([input_df.drop('Geography', axis=1).reset_index(drop=True), 
                            encoded_geo_df.reset_index(drop=True)], axis=1)
st.write("Final Input Data for Prediction with shape:", final_input_df.shape)
st.dataframe(final_input_df)

## scale the data
try:
    scaled_input_df = scaler.transform(final_input_df)
except Exception as e:
    st.error(f"Scaler transform failed: {e}")
    st.write("Columns:", final_input_df.columns.tolist())
    st.write("Dtypes:")
    st.dataframe(final_input_df.dtypes.to_frame('dtype'))
    row = final_input_df.iloc[0]
    st.write("Row values:", row.tolist())
    st.write("Value types:", [type(v).__name__ for v in row.tolist()])

    # Attempt safe coercion to numeric and retry
    coerced = final_input_df.apply(pd.to_numeric, errors='coerce')
    st.write("After coercion dtypes:")
    st.dataframe(coerced.dtypes.to_frame('dtype'))
    if coerced.isnull().any().any():
        st.warning("Nulls found after coercion; filling nulls with 0 before scaling.")
        st.write(coerced.isnull().sum())
    coerced = coerced.fillna(0)
    try:
        scaled_input_df = scaler.transform(coerced)
        st.write("Scaled after coercion")
        st.dataframe(pd.DataFrame(scaled_input_df, columns=coerced.columns))
    except Exception as e2:
        st.error(f"Scaler transform still failed after coercion: {e2}")
        raise

## Predict churn
probability = model.predict(np.array(scaled_input_df))
predicted_probability = probability[0][0]

st.write(f"Predicted Churn Probability: {predicted_probability:.3f}")

predicted_probability = float(probability[0][0])
color = "red" if predicted_probability > 0.5 else "green"
st.markdown(f"<p style='color:{color}; font-size:22px; font-weight:700'>Predicted Churn Probability: \
            {predicted_probability:.3f} {"Customer will Churn" if predicted_probability > 0.5 \
                                         else "Customer will Not Churn"}</p>", unsafe_allow_html=True)