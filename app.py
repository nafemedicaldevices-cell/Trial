import streamlit as st
from data_loader import load_all

model = load_all()

sales = model["sales"]
