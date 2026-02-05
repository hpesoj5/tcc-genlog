import time
import streamlit as st
from datetime import date
from sheet import Sheet

@st.dialog("Autofill in progress...", dismissible=False)
def autofill(gens, name: str="", end_date: date=date.today(), end_val: int | None = None):

    successes = 0 # this will store the number of sheets updated successfully

    error_container = st.container()

    with st.empty():

        for gen in gens:

            try:
                serial_no = gen
                st.write(f"Updating sheet {serial_no}...")      # display text

                sheet = Sheet(st.session_state["sheet"], gen)   # actually update sheet
                sheet.autofill(gen, name, end_date, end_val)

                successes += 1

            except Exception as e:
                error_container.write(f"Error updating log for {gen}: {e}")
                print(f"Error updating log for {gen}: {e}")     # debug text

        st.write(f"Updated {successes} sheets, could not update {len(gens) - successes} sheets.")
        print(f"Updated {successes} sheets, could not update {len(gens) - successes} sheets.")

    st.session_state['autofill'] = False
    time.sleep(1)   # to leave the dialog on display for a second
    st.rerun()      # reload

@st.dialog("Update the selected generators?")
def confirm_autofill(num_options):

    st.write(f"{num_options} generators selected")
    name = st.text_input(label="Name", label_visibility='collapsed', width='stretch', placeholder='Enter name of authorising person (optional)')
    col1, col2 = st.columns(2)
    with col1:
        no = st.button("No", width='stretch')
    with col2:
        yes = st.button("Yes", width='stretch', type='primary')

    if yes:
        st.session_state['autofill'] = True
        st.session_state['name'] = name
        st.rerun()

    elif no:
        st.session_state['autofill'] = False
        st.rerun()
