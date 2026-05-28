import streamlit as st
import pandas as pd

st.title("My Data Dashboard")

# Load data (example)
df = pd.read_csv("your_file.csv")

st.subheader("Data Preview")
st.write(df.head())

st.subheader("Summary Stats")
st.write(df.describe())

st.line_chart(df.select_dtypes(include='number'))
 
