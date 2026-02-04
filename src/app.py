import streamlit as st
from autofill import autofill, confirm_autofill
from footer import footer
from generators import generators, params
from sheet import authenticate, Sheet

def load_sheet(sheet_container: st.container, gen: str):

    gen = st.session_state.selected_gen
    sheet = Sheet(st.session_state['sheet'], gen)
    df = sheet.get_sheet_as_df()

    with sheet_container:
        st.dataframe(df, hide_index=True)

    print(f"Succesfully displayed sheet for gen {gen}")

def page_init():

    st.title("TCC Generator Logbook Tool", anchor=False)
    st.subheader("[How to Use](https://github.com/hpesoj5/tcc-genlog?tab=readme-ov-file#usage)", anchor=False)
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

    col1, col2 = st.columns([1, 4], gap='large')

    return (col1, col2)

def display_gen_selection_panel(logger):

    with logger:

        container = st.container()

        select_all = st.checkbox("Select all")
        if select_all:
            options = container.multiselect(
                "Generators",
                list(generators.values()),
                list(generators.values()),
                placeholder="Choose generators...",
            )

        else:
            options = container.multiselect(
                "Generators",
                list(generators.values()),
                placeholder="Choose generators...",
            )

        end_val = st.number_input(label="Final generator reading (if applicable)", value=None, placeholder="Enter a reading...")
        end_date = st.date_input(label="Date to autofill logs until", value="today", format="DD/MM/YYYY")

        if st.button("Autofill Logsheets", width='stretch'):
            confirm_autofill()

        if st.session_state['autofill']:
            autofill(options, st.session_state['name'], end_date, end_val)
            st.session_state['name'] = ""

def display_view_panel(viewer):

    with viewer:

        gen = st.selectbox(
            label="Generator",
            options=list(generators.values()),
            index=None,
            key='selected_gen',
            placeholder="Choose a generator log to view...",
            width=400,
        )

        sheet_container = st.container()

        if gen is not None:

            load_sheet(sheet_container, gen)

            st.link_button(
                label="Open Sheet",
                url=f"https://docs.google.com/spreadsheets/d/14vNYY24YcFoJ7-aKJCqSyJboYIX7ZlmY4S_0SS2gFTY/edit?usp=sharing&gid={params[gen]}",
                type="primary",
            )

        else:

            st.link_button(
                label="Open Sheet",
                url="https://docs.google.com/spreadsheets/d/14vNYY24YcFoJ7-aKJCqSyJboYIX7ZlmY4S_0SS2gFTY/edit?usp=sharing",
                type="primary",
            )

def main():

    # authenticate google service account
    if 'sheet' not in st.session_state:
        st.session_state['sheet'] = authenticate()

    logger, viewer = page_init()

    display_gen_selection_panel(logger)
    display_view_panel(viewer)
    footer()

if __name__ == '__main__':
    main()
