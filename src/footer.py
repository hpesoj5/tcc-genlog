import streamlit as st
from htbuilder import HtmlElement, div, a, p, img, styles
from htbuilder.units import percent, px

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
