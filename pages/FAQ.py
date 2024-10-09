import streamlit as st

# Page Config
# Configure and render Streamlit page
st.set_page_config(
    page_title="RhinoFolio",
    page_icon="🎞️",
    #layout="wide",
    initial_sidebar_state="auto"
)

#st.sidebar.markdown("# FAQ")

st.title("FAQ")
st.write("")

with st.expander("**What is RhinoFolio and what does it do?**"):
    st.write(
        "RhinoFolio is a tool that helps you create social media banners featuring stock write-ups and logos of the companies you're analyzing. "
        "It allows you to select stock names, generate banners with logos, and customize them for platforms like Twitter, LinkedIn, and Substack."
    )

with st.expander("**How do I create a banner using RhinoFolio?**"):
    st.markdown('''To create a banner, simply search your for your user handle from the list provided. After that, select a banner template, click 'Create Banner,'
and RhinoFolio will generate a banner featuring the logos and stock names associated with the username.
                
***Note: Currently, RhinoFolio is customized for the finance and investment community. So, you should have submitted at least one stock analysis on [RhinoInvestory](https://rhinoinvestory.com) before using RhinoFolio and creating your customized banner.***
    
    ''')

with st.expander("**How many banners can I generate for free?**"):
    st.write(
        "For now, you can generate as many banners you want. It's all FREE."
    )

with st.expander("**What happens if a stock logo is missing or doesn’t display correctly?**"):
    st.write(
        "If a stock logo doesn't load, it might be due to an issue with the logo URL or the stock information. Just reach out to me at [RhinoInsight](https://x.com/RhinoInsight) and I will fix it."
    )

with st.expander("**Any plans to add more platforms in the future?**"):
    st.write(
        "Yes! RhinoFolio plans to add additional platforms like **Buy Me A Coffee**, **Facebook**, and many others soon."
    )