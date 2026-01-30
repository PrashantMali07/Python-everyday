import numpy as np
from tensorflow.keras.models import load_model
import streamlit as st
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
import warnings
warnings.filterwarnings('ignore')

## Load the trained model
model = load_model('/home/prashant/Documents/ML-DL/Deeplearning/NextWordPrediction_LSTM+Streamlit/next_word_prediction_model.keras')

## Load the tokenizer
with open('/home/prashant/Documents/ML-DL/Deeplearning/NextWordPrediction_LSTM+Streamlit/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

## Defining a function to predict the next word
def predict_next_word(model, tokenizer, text, max_len):
    token_list = tokenizer.texts_to_sequences([text])[0]
    if len(token_list) > max_len:
        token_list = token_list[-(max_len-1):]
    token_list = pad_sequences([token_list], maxlen=max_len-1, padding='pre')
    predicted = model.predict(token_list, verbose=0)
    position = np.argmax(predicted, axis=1)
    
    for word, index in tokenizer.word_index.items():
        if index == position:
            return word
    return None

st.title("Next Word Prediction using LSTM")
input_text = st.text_input("Give an input text:", "Once upon a time")

if st.button("Predict Next Word"):
    max_len = model.input_shape[1]
    next_word = predict_next_word(model, tokenizer, input_text.lower(), max_len)
    st.write(f"The predicted next word is: **{next_word}**")