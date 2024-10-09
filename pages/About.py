import streamlit as st

# Page Config
# Configure and render Streamlit page
st.set_page_config(
    page_title="RhinoFolio",
    page_icon="🎞️",
    #layout="wide",
    initial_sidebar_state="auto"

)

# Set the page title and a welcome message
st.title("About")

#st.sidebar.markdown("# About")
#st.markdown("# About")

st.subheader("💡 Why RhinoFolio?")
st.markdown('''One of the hardest parts of building and growing a business is marketing. So, why not make use of every platform possible to spotlight your work?

That's why I turned my latest idea into a side project, and launched **RhinoFolio**, a social media banner creator designed to help you spotlight your latest investment analysis across multiple social media platforms, such as Twitter, LinkedIn, and Substack.
''')

st.write("")
st.write("➡️ Follow **RhinoInsight** on Twitter for more and to stay up to date with the latest products and services👇")
st.write("")

c1, c2, c3 = st.columns(3)
with c1:
    st.info('**RhinoInsight Twitter: [@RhinoInsight](https://twitter.com/RhinoInsight)**', icon="🐦")
with c2:
    st.info('**RhinoInsight Substack: [@RhinoInsight](https://rhinoinsight.substack.com/)**', icon="🗞️")
with c3:
    st.info('**RhinoInvestory - A Directory of 1000+ Stock Analysis: [RhinoInvestory](https://RhinoInvestory.com/)**', icon="🗂️")
