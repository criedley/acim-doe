# streamlit_app.py
import pandas as pd
import numpy as np
import streamlit as st
from build_report import report

df = pd.DataFrame(
    {
        "cycle": [1, 2, 1, 2, 3],
        "cycle type": ["stability", "stability", "DOE", "DOE", "DOE"],
        "start weight": [0.0, 0.0, 0.0, 0.0, 0.0],
        "end weight": [0.0, 0.0, 0.0, 0.0, 0.0],
    },
    index=["stab1", "stab2", "doe1", "doe2", "doe3"],
)

# Initialize the session state with the dataframe
if "df" not in st.session_state:
    st.session_state['df'] = df
elif len(st.session_state['df']) == len(df):
    st.session_state['df'].index = df.index
else:
    st.session_state['df'].index = st.session_state['df'].index.map(str)

st.session_state['df']['harvest weight'] = st.session_state['df']["end weight"] - st.session_state['df']["start weight"]
previous_weight = st.session_state['df']['harvest weight'].shift(1)
average_weight = (st.session_state['df']['harvest weight'] + previous_weight) / 2
st.session_state['df']['percent change'] = (np.absolute(st.session_state['df']['harvest weight'] - previous_weight) / average_weight) * 100

def on_change():
    # Update the dataframe in session state with the edited values
    edited_rows = st.session_state['data_editor']['edited_rows']
    for index, row in edited_rows.items():
        for col, value in row.items():
            if col in st.session_state['df'].columns:
                if col == "cycle":
                    # Ensure the cycle value is an integer
                    if value is None or not float(value).is_integer():
                        st.warning("Cycle must be a whole number.")
                        continue
                    value = int(value)
                # Allow mixed index types by using .iat for positional indexing
                column_position = st.session_state['df'].columns.get_loc(col)
                st.session_state['df'].iat[index, column_position] = value
            else:
                 st.warning(f"Column {col} does not exist in the dataframe.")
            
st.data_editor(
    st.session_state['df'], 
    column_config={
        "cycle": st.column_config.NumberColumn(
            min_value=1,
            step=1,
            format="%d",
            required=True,
        ),
        "cycle type": st.column_config.SelectboxColumn(
            options=["stability", "DOE"],
            required=True,
        ),
        "start weight": st.column_config.NumberColumn(
            min_value=0.0,
            format="%.3f",
            step=0.001,
            required=True,
        ),
        "end weight": st.column_config.NumberColumn(
            min_value=0.0,
            format="%.3f",
            step=0.001,
            required=True,
        ),
        "percent change": st.column_config.NumberColumn(
            format="%.2f %%",
            step=0.01,
            disabled=True,
        ),
    },
    disabled = ['harvest weight'],
    key="data_editor",
    on_change=on_change,
    # num_rows="dynamic",
    hide_index=True,
    placeholder=""
)

if st.button("Build report"):
    report_df, doe_summary_df = report(st.session_state["df"])
    st.dataframe(report_df)
    st.dataframe(doe_summary_df)