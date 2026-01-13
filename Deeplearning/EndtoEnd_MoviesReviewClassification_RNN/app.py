import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
import streamlit as st

## Initializing streamlit app title
st.title("IMDB Review Sentiment Prediction App.")
st.write("Enter your Movie-review to predict Score & Sentiment")
st.markdown(f"<p style='color:red; font-size:10px; font-weight:300'>Note: Please press Ctrl+Enter, when new review entered after each prediction.</p>", unsafe_allow_html=True)

## Load model and dataset
imdb_index = imdb.get_word_index()
sentence_dict = {value: key for key, value in imdb_index.items()}

model = load_model('/home/prashant/Documents/ML-DL/Deeplearning/EndtoEnd_MoviesReviewClassification_RNN/rnn_imdb_ac9901.h5',compile=False)

## Function to preprocess user input
def preprocess_user_input(review, word_index=imdb_index):
    words = review.lower().split()
    review_vec = [word_index.get(word,2)+3 for word in words]
    padded_review = sequence.pad_sequences([review_vec],maxlen=500)
    return padded_review

## Function to predict the user input
def predict_review(review):
    preprocessed_input = preprocess_user_input(review)

    prediction = model.predict(preprocessed_input)

    review_sentiment = 'Negetive' if prediction[0][0] < 0.5 else 'Positive'

    return prediction[0][0], review_sentiment

## Get user review
user_review = f"{st.text_area('Enter Review here 👇',max_chars=500)}"
st.write("User Input: ",user_review)

if st.button('Classify'):
    ## Prediction function
    score, sentiment = predict_review(user_review)

    st.write(f"Score: {score}")
    st.write(f"Sentiment: {sentiment}")
else:
    st.write("Please enter a movie review.")