# End-to-End Movie Review Classification (RNN)

Short description
- Small end-to-end project that trains a Simple RNN on the IMDB dataset to classify movie reviews as positive or negative and exposes a Streamlit app for inference.

Project structure
- [app.py](app.py) — Streamlit app for live inference; contains preprocessing and inference helpers such as [`preprocess_user_input`](app.py) and [`predict_review`](app.py).
- [RNN_Model.ipynb](RNN_Model.ipynb) — Notebook with model design and training (Embedding, SimpleRNN, Dense layers, callbacks, training loop, `model.save`).
- [embedding.ipynb](embedding.ipynb) — Experiments and notes about Embedding layer configuration and embedding vector dimension.
- [prediction.ipynb](prediction.ipynb) — Inference examples and demonstration of loading the saved model and running predictions.
- [rnn_imdb_ac9901.h5](rnn_imdb_ac9901.h5) — Saved trained model artifact (HDF5 format).

Topics covered
- IMDB dataset loading and token index usage
- Text preprocessing: token mapping and sequence padding
- Embedding layer usage and experiments
- RNN architecture (SimpleRNN), Dense classification head
- Training utilities: EarlyStopping, validation split, model checkpoint/save
- Model export to HDF5 and loading for inference
- Streamlit-based UI for entering reviews and returning score + sentiment

What the project does
- Trains an RNN-based sentiment classifier on IMDB reviews and provides a lightweight Streamlit interface to input a review and receive a predicted score and sentiment label.

Required libraries (suggested)
- Python: 3.8 — 3.10
- tensorflow >= 2.10 (includes Keras)
- streamlit >= 1.10
- numpy >= 1.22
- h5py >= 3.1 (for .h5 model load/save)
- (optional) matplotlib, scikit-learn for analysis/visualization

Typical tasks performed
1. Data loading and token index creation (IMDB).
2. Preprocessing: convert text -> word indices -> padded sequences (`preprocess_user_input`).
3. Model building: Embedding + SimpleRNN + Dense classifier (`RNN_Model.ipynb`).
4. Training with validation split and callbacks (EarlyStopping).
5. Save trained model to [rnn_imdb_ac9901.h5](rnn_imdb_ac9901.h5).
6. Load model and run inference from notebook ([prediction.ipynb](prediction.ipynb)) or via Streamlit app ([app.py](app.py)).

Quick run (local)
1. pip install -r requirements.txt (create with the listed packages)
2. To run UI: streamlit run app.py
3. To reproduce training: open and run cells in [RNN_Model.ipynb](RNN_Model.ipynb)

References
- Uses the built-in Keras IMDB dataset and standard Keras layers (Embedding, SimpleRNN, Dense).