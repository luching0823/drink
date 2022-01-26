import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1txZGNLtjcwqaHyQBC-CDgEyvg_Ko7JEFVKs3lXpBQ_s"
SHEET_NAME = "Drink"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# 連到 Google Sheet
@st.experimental_singleton()
def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def get_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )


st.set_page_config(page_title="Drink!", page_icon="🍻", layout="centered")

st.title("🍻 Let's drink!")

gsheet_connector = connect_to_gsheet()

# st.sidebar.write(
#     f"This app shows how a Streamlit app can interact easily with a [Google Sheet]({GSHEET_URL}) to read or store data."
# )

# st.sidebar.write(
#     f"[Read more](https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet) about connecting your Streamlit app to Google Sheets."
# )

setForm = st.form(key="setOptions")

with setForm:
    cols = st.columns(2)
    author = cols.selectbox( "Name", ["Pulin","Coody","Ken","Irene"] )
    drink = cols.selectbox(
        "drink name:", ["紅", "綠", "奶", "烏"], index=2
    )
    comment = cols.text_area("Comment:")
    submitted = st.form_submit_button(label="Submit")


if submitted:
    add_row_to_gsheet(
        gsheet_connector, [[author, drink, comment]]
    )
    # 綠色提示框
    st.success("Thanks! Your bug was recorded.")
    # 氣球動畫效果
    st.balloons()

expander = st.expander("See all records")
with expander:
    st.write(f"Open original [Google Sheet]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector))
