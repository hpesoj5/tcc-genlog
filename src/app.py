import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
from generators import generators, params
from sheet import authenticate, Sheet
import time
from datetime import date

def image(src_str, **style):
    return img(src=src_str, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="blank", style=styles(**style))(text)

def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="white",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        "Made by ",
        link("https://github.com/hpesoj5", "hpesoj5"),
        " with ",
        link("https://streamlit.io", "Streamlit"),
        " ",
        image("https://global.discourse-cdn.com/streamlit/original/3X/c/f/cf4c2ee0d938358f82448c5fe4b9c3c91d7ce19c.svg", width=px(20), height=px(20)),
    ]
    layout(*myargs)

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
    col1, col2 = st.columns([1, 4], gap='large')
    return (col1, col2)

@st.dialog("Autofill in progress...", dismissible=False)
def autofill(gens, name: str="", end_date: date=date.today()):
    success = 0
    error_container = st.container()
    with st.empty():
        for gen in gens:
            try:
                serial_no = gen
                st.write(f"Updating sheet {serial_no}...")

                # UPDATE GOOGLE SHEET
                sheet = Sheet(st.session_state["sheet"], gen)
                sheet.autofill(gen, name, end_date)

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
        st.session_state['name'] = name
        # print("YES")
        st.rerun()
    elif no:
        st.session_state['autofill'] = False
        st.rerun()

def load_sheet(sheet_container: st.container, gen: str):
    gen = st.session_state.selected_gen
    sheet = Sheet(st.session_state['sheet'], gen)
    df = sheet.get_sheet_as_df()
    with sheet_container:
        st.dataframe(df, hide_index=True)
    print(f"Succesfully displayed sheet for gen {gen}")

def main():

    # AUTHENTICATE GOOGLE SERVICE ACCOUNT TO UPDATE GOOGLE SHEET
    if 'sheet' not in st.session_state:
        st.session_state['sheet'] = authenticate()

    # INIT PAGE
    st.title("TCC Generator Logbook Tool", anchor=False)
    st.subheader("[How to Use](https://github.com/hpesoj5/tcc-genlog?tab=readme-ov-file#usage)", anchor=False)
    logger, viewer = page_init()

    # GENERATOR SELECTION WIDGET
    with logger:
        container = st.container()

        select_all = st.checkbox("Select all")

        if select_all:
            options = container.multiselect(
                "Generators",
                list(generators.values()),
                list(generators.values()),
                placeholder="Choose generators...",
                # label_visibility='collapsed',
            )
        else:
            options = container.multiselect(
                "Generators",
                list(generators.values()),
                placeholder="Choose generators...",
                # label_visibility='collapsed',
            )

        end_date = st.date_input(label="Date to autofill logs until", value="today", format="DD/MM/YYYY")
        if st.button("Autofill Logsheets", width='stretch'):
            confirm_autofill()

        if st.session_state['autofill']:
            autofill(options, st.session_state['name'], end_date)
            st.session_state['name'] = ""

    # LOGGING TOOLS
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
        if gen != None:
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

    footer()

if __name__ == '__main__':
    main()
