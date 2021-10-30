
import numpy as np
import pandas as pd
import streamlit as st
import time


'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.0001)

'...and now we\'re done!'

# import requests
#     # r = requests.get('https://api.opensea.io/api/v1/events', params=params)
# params = {
#     'collection' : 'body-language-2021',
#     'limit': 1
# }
# r = requests.get("https://api.opensea.io/api/v1/assets",params=params)
# print(r.json())