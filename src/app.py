import streamlit as st
from generators import generators
from sheet import authenticate

def page_init():
    st.set_page_config(
        page_title="TCC Digital Generator Logbook",
        page_icon="😎",
        layout="wide",
        menu_items={
            "Report a bug": "mailto:josephtante05@gmail.com",
        }
    )
    col1, col2 = st.columns([2, 3], gap='medium')
    return (col1, col2)

def main():

    # AUTHENTICATE GOOGLE SERVICE ACCOUNT TO UPDATE GOOGLE SHEET
    if 'sheet' not in st.session_state:
        st.session_state['sheet'] = authenticate()
        print("Google service account authentication success!")

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
            try:
                for gen in options:
                    serial_no = generators[gen]
                    print(f"{gen} log success!")
            
            except Exception as e:
                print(f"Error updating logs: {e}")
    
if __name__ == '__main__':
    main()