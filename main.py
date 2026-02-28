import streamlit as st
from utils import *


# Set page config
st.set_page_config(
    page_title="Animals Data Sphere",
    page_icon="🐕",
    layout="wide"
)

# Custom CSS theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap');
    /* Main background */
    *, *::before, *::after {
        font-family: "Lato", "sans-serif";
    }
    
    div[data-testid="stColumn"] {
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
    }

    .stApp {
        //background: linear-gradient(135deg, #13063c 0%, #160846 100%);
        background: linear-gradient(135deg, #3128b4 0%, #3613a8 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.2) 0%, rgba(78, 67, 228, 0.85) 70%, rgba(255, 255, 255, 0.2) 95%);
    }

    /* Headers */
    h1, h2, h3 {
        color: #f8f9fa !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    /* Text */
    p, span, div {
        color: #f8f9fa !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #e94e39;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 36px;
        font-weight: 600;
        transition: ease-in-out 0.5s;
    }

    .stButton>button:hover {
        background-color: #e94e39;
        transform: scale(1.02);
        opacity: 0.95;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Radios */
    # .stRadio {
    #     margin: .5rem;
    #     font-weight: 900 !important;
    #     font-size: 2.1rem !important;
    # }

    .stb3>label {
        margin-top: .5rem;
    }

    /* Text inputs */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid #756bff;
        border-radius: 8px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
    }

    /* Cards/containers */
    .element-container {
        # background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Navigation Bar


def welcome():
    st.text("Welcome")

    st.markdown("---")

    st.write("""
            <h3>About: </h3>
            <h4>This App is shipped with the following functionalities:</h4>
            <ol>
                <li>Scraping & Displaying Animals Data from CoinAfrique</li>
                <li>Visualizing and Downloading Animals Data already scraped from CoinAfrique.</li>
                <li>Getting Insight from Animals Data already scraped from CoinAfrique.</li>
                <li>Reviewing the application (To help us improve it).</li>
            </ol>""", unsafe_allow_html=True)

    dependencies_col, data_sources_col = st.columns(2)
    with dependencies_col:
        st.write("""

                <h4>Some of the dependencies that were used are:</h4>
                <ul>
                    <li>Selenium</li>
                    <li>BeautifoulSoup v4</li>
                    <li>Pandas</li>
                    <li>SQLite3</li>
                </ul> """, unsafe_allow_html=True)
    with data_sources_col:
        st.write("""
                <h4>Data is scraped form the following links:</h4>
                <ul>
                    <li><a href="https://sn.coinafrique.com/categorie/chiens">Dogs</a></li>
                    <li><a href="https://sn.coinafrique.com/categorie/moutons">Goats</a></li>
                    <li><a href="https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons">Chickens, Rabbits and Pigeons</a></li>
                    <li><a href="https://sn.coinafrique.com/categorie/autres-animaux">Other Animals</a></li>
                </ul>
                """, unsafe_allow_html=True)


def scrap_data():
    st.text("Scrap data with Selenium & bs4")

    st.markdown("---")

    pages = st.slider(
        "Please select the number of page to be scraped", 1, 10, 1)
    st.subheader(
        f"By clicking on one of this buttons you will scrape {pages} page{"s" if pages > 1 else ""}.")

    for page in ROOT_PAGE_LIST:

        if st.button(page['title'].replace("_", " ").title(), width=480):
            scrap_clean_save_data(page_to_scrap=page, number_of_page=pages)
            data = read_from_db(table_name=page["title"])

            st.write(
                f"Number of Rows : {data.shape[0]} \t| Number of Columns : {data.shape[1]}")
            st.dataframe(data)


def explore_and_download():
    st.text("Explore & Download Scraped Data")

    st.markdown("---")

    st.subheader(
        "By clicking on one of this buttons, you will display the related Data.")

    raw_data_tuple = read_raw_data()
    for title, data in raw_data_tuple:
        if st.button(f"Display Raw {title} data", width=480):
            st.write(
                f"Number of Rows : {data.shape[0]} \t| Number of Columns : {data.shape[1]}")
            st.dataframe(data, width="stretch")


def dashboard():
    st.text("Get Insight from Data (Dashboard)")

    st.markdown("---")

    cleaned_data_tuple = read_cleaned_data()

    st.subheader(
        "By clicking on one of this buttons, you will display diagrams related to the Data.")

    for title, data in cleaned_data_tuple:
        index_col = tuple(set(data.columns.tolist()) & {"nom", "details"})[0]

        if st.button(f"Diagram for {title} data", width=480):
            _, centered_col, _ = st.columns([1, 22, 1])
            with centered_col:
                left_centered_col, right_centered_col = st.columns(2)
                with left_centered_col:
                    st.write("### Distribution")
                    st.bar_chart(
                        data[[index_col, "prix"]].set_index(index_col), x_label=index_col)
                    st.write("Maximum price: ", data["prix"].max())
                with right_centered_col:
                    st.write("### Evolution")
                    st.line_chart(data["prix"].sort_values(), y_label="prix")
                    st.write("Minimum price: ", data["prix"].min())


def evaluation():
    st.text("Evaluate the Application")

    st.markdown("---")

    st.write("""
    Help us to improve the application for you and everyone else using it, by leaving a review:
    
    You can choose one the options below (We recommend the Kobo Form -- The one on le left) 
    """)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.link_button("Kobo Toolbox Form", "https://ee.kobotoolbox.org/single/I0Rqs497",
                           width="stretch")
        with col_b:
            st.link_button("Google Forms", "https://forms.gle/t9UwMipezXjR47da7",
                           width="stretch")


# Main content
st.title("[🐕] - Animals Data Sphere")

# Setting up Pages
p1 = st.Page(welcome, title="Welcome")
p2 = st.Page(scrap_data, title="Scrap data with Selenium & bs4")
p3 = st.Page(explore_and_download, title="Explore & Download Scraped Data")
p4 = st.Page(dashboard, title="Get Insight from Data (Dashboard)")
p5 = st.Page(evaluation, title="Evaluate the Application")

pg = st.navigation([p1, p2, p3, p4, p5])
pg.run()

# Footer
st.markdown("---")
st.write("""
         <p>Made with Streamlit by: <a href="https://www.linkedin.com/in/fabeklou/">Fabrice EKLOU</a> </p>
         """, unsafe_allow_html=True)
