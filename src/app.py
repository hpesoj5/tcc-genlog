import streamlit as st
from generators import generators
from sheet import authenticate
import time

def page_init():
    st.set_page_config(
        page_title="TCC Digital Generator Logbook",
        page_icon="😎",
        layout="wide",
        menu_items={
            "Report a bug": "mailto:josephtante05@gmail.com",
        }
    )
    if 'autofill' not in st.session_state:
        st.session_state['autofill'] = False
    col1, col2 = st.columns([2, 3], gap='medium')
    return (col1, col2)
        
@st.dialog("Autofill in progress...", dismissible=False)
def autofill(gens):
    success = 0
    error_container = st.container()
    with st.empty():
        for gen in gens:
            try:
                serial_no = generators[gen]
                st.write(f"Updating sheet {serial_no}...")
                    
                # UPDATE GOOGLE SHEET   
                    
                print(f"{gen} log success!")
                success += 1
        
            except Exception as e:
                error_container.write(f"Error updating log for {gen}: {e}")
                print(f"Error updating log for {gen}: {e}")
        
        st.write(f"Updated {success} sheets, could not update {len(gens) - success} sheets.")
        
    print(f"Updated {success} sheets, could not update {len(gens) - success} sheets.")
    
    st.session_state['autofill'] = False
    time.sleep(1)
    st.rerun()

@st.dialog("Do you want to update the selected generators?")
def confirm_autofill():
    name = st.text_input(label="Name", label_visibility='hidden', width='stretch', placeholder='Enter name of authorising person')
    no = st.button("No", width='stretch')
    yes = st.button("Yes", width='stretch', type='primary')
    if yes:
        st.session_state['autofill'] = True
        print("YES")
        st.rerun()
    elif no:
        st.session_state['autofill'] = False
        st.rerun()

def main():

    # AUTHENTICATE GOOGLE SERVICE ACCOUNT TO UPDATE GOOGLE SHEET
    if 'sheet' not in st.session_state:
        st.session_state['sheet'] = authenticate()

    # INIT PAGE
    col1, col2 = page_init()

    # GENERATOR SELECTION WIDGET
    with col1:
        container = st.container()

        select_all = st.checkbox("Select all")

        if select_all:
            options = container.multiselect(
                "Generators",
                list(generators.keys()),
                list(generators.keys()),
                placeholder="Choose generators...",
                label_visibility='collapsed',
            )
        else:
            options = container.multiselect(
                "Generators",
                list(generators.keys()),
                placeholder="Choose generators...",
                label_visibility='collapsed',
            )

    # LOGGING TOOLS
    with col2:
        if st.button("Autofill Logsheets", width='stretch'):
            confirm_autofill()
        
        if st.session_state['autofill']:
            autofill(options)
                        
        st.subheader("Add Manual Entry")
        
        # entry_df = # TODO
        
        if st.button("Top up POL", width='stretch'):
            pass # TODO
    
if __name__ == '__main__':
    main()