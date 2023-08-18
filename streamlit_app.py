import json
import requests
from datetime import datetime
from datetime import datetime, timezone, timedelta
import streamlit as st
from annotated_text import annotated_text
import app.utils

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)


def convert_utc_to_local_datetime(utc_datetime_string):
    # Convert UTC datetime string to datetime object
    utc_datetime = datetime.strptime(utc_datetime_string, '%Y-%m-%dT%H:%M:%SZ')

    # Convert to local time (assuming your local timezone is UTC+0)
    local_datetime = utc_datetime.strftime('%a, %b %d, %Y')

    return local_datetime


def convert_to_epoch_time(utc_datetime_string):
    # Convert UTC datetime string to datetime object
    utc_datetime = datetime.strptime(utc_datetime_string, '%Y-%m-%dT%H:%M:%SZ')

    # Convert to epoch time (UNIX timestamp)
    epoch_time = (utc_datetime - datetime(1970, 1, 1)).total_seconds()
    return epoch_time


def todays_date_in_epoch_time():
    # Get today's date
    today = datetime.today()

    # Convert to epoch time (UNIX timestamp)
    epoch_time = (today - datetime(1970, 1, 1)).total_seconds()
    return epoch_time


def how_long_ago(utc_datetime_string):
    t0 = convert_to_epoch_time(utc_datetime_string)
    t1 = todays_date_in_epoch_time()
    t_diff = t1 - t0

    d = int(t_diff / (3600 * 24))
    h = int(t_diff / 3600)
    m = int(t_diff % 3600)

    if d > 0:
        phrase = f"{d}d ago"
    elif h > 0:
        phrase = f"{h}h ago"
    else:
        phrase = f"{m}m ago"

    return phrase


def todays_date():
    today = datetime.today()
    formatted_date = today.strftime('%a, %b %d, %Y')

    return formatted_date


API_KEY = st.secrets['API_KEY']
COUNTRY_CODE = "us"

sources = [
    "associated-press",
    "the-wall-street-journal",
    "fortune",
    "bbc-news",
    "reuters",
    "abc-news",
    "bloomberg",
    "financial-post",
    "breitbart-news",
    "buzzfeed",
    "business-insider",
    "cbs-news",
    "cnn",
    "espn"
]

# URL = f"https://newsapi.org/v2/top-headlines?sources={','.join(sources)}&apiKey={API_KEY}"
# URL=f"https://newsapi.org/v2/top-headlines/sources?category=business&apiKey={API_KEY}"

URL_SOURCES = f"https://newsapi.org/v2/top-headlines/sources?country=usapiKey={API_KEY}"


class URLs:
    EVERYTHING = "https://newsapi.org/v2/everything?q={0}&sortBy=popularity&apiKey={1}"
    TOP_HEADLINES = f"https://newsapi.org/v2/top-headlines?country={COUNTRY_CODE}&apiKey={API_KEY}"


@st.cache_data(ttl=14_000, show_spinner="Thinking...")
def fetch(category):
    print("fetch")

    url = URLs.TOP_HEADLINES + f"&category={category}"

    response = requests.get(url)

    data = {}

    if response.status_code == 200:
        # st.write(response.json())
        data = response.json()
    else:
        # TODO Raise/Throw Exception
        st.error(f"status_code: {response.status_code}")

    return data


def display(article):
    left_col, mid_col, right_col = st.columns([2, 1, 5])

    with left_col:
        if article['urlToImage'] is not None:
            st.image(article['urlToImage'])
        st.write(how_long_ago(article['publishedAt']))

    with right_col:
        if st.session_state['show_named_entities']:
            prepared = app.utils.prepare_text(article['title'])
            annotated_text(prepared)
        else:
            st.markdown(f"[{article['title']}]({article['url']})")

        if article['description'] is not None:
            if st.session_state['show_named_entities']:
                prepared = app.utils.prepare_text(article['description'])
                pp.pprint(prepared)
                annotated_text(prepared)
            else:
                # st.write(article['description'])
                st.markdown(f"<p>{article['description']}</p>", unsafe_allow_html=True)


def search_form():
    with st.form("search_form"):
        search_criteria = st.text_input("Search")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Process query")
            print("search criteria", search_criteria)
            url = URLs.EVERYTHING.format(search_criteria, API_KEY)
            print("url:", url)
            fetched_data = fetch(url)
            print("fetched data")
            pp.pprint(fetched_data)


def simple_view(category, articles):
    count = len(articles)

    st.title(f"{category} Headlines ({count})")
    st.write(todays_date())

    # st.divider()
    # search_form()

    st.divider()

    for article in articles:
        display(article)
        st.divider()


def view(articles):
    print("redraw")

    count = len(articles)

    st.title(f"Headlines ({count})")
    st.write(todays_date())

    for article in articles:
        left_col, right_col = st.columns([2, 6])

        with left_col:
            local_datetime = convert_utc_to_local_datetime(article['publishedAt'])
            st.write(local_datetime)

        with right_col:
            st.markdown(f"### { article['title']}")

            if article['urlToImage'] is not None:
                st.image(article['urlToImage'])

            if article['description'] is not None:
                st.write(article['description'])

            st.markdown(f"[{article['source']['name']}]({article['url']})")
        st.divider()


EMOJI_NEWSPAPER = "\U0001F4F0"

categories = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology",
]

dict_of_categories = {category.title(): category for category in categories}


def main():
    print("main")

    st.set_page_config("Headlines", page_icon=EMOJI_NEWSPAPER)

    if "show_named_entities" not in st.session_state:
        st.session_state["show_named_entities"] = False

    with st.sidebar:
        category_display_name = st.radio("Categories:", dict_of_categories.keys(), index=4, key="categories")
        category_key = dict_of_categories[category_display_name]

        show_entities = st.checkbox('Show Named Entities')
        st.session_state["show_named_entities"] = show_entities

    data = fetch(category_key)

    if 'articles' in data:
        simple_view(category_display_name, data['articles'])
    else:
        print("No articles returned")


if __name__ == "__main__":
    main()
