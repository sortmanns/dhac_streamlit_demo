# streamlit_app.py

import hmac
import uuid

import streamlit as st
from snowflake.snowpark import functions as F
from snowflake.snowpark.session import _get_active_sessions
from snowflake.snowpark.types import (DoubleType, IntegerType, StringType,
                                      StructField, StructType)


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# Main Streamlit app starts here
# Connect to Snowflake
conn = st.connection('snowflake')
session = conn.session()

st.title('Input Form')

# Form fields arranged in three columns
col1, col2 = st.columns(2)

# Column 1
with col1:
    geschlecht = st.selectbox('Geschlecht', ['Male', 'Female'])
with col2:
    alter = st.selectbox('Alter', [x for x in range(0, 100)])

# Customizing the Submit button inside st.form
with st.form(key='my_form'):
    submit_button = st.form_submit_button('Submit', help='Click to submit the form')

    # Check if the form is submitted
    if submit_button:
        # Get form data
        form_data = {
            'geschlecht': geschlecht,
            'alter': alter,
        }

        schema = StructType([
            StructField('geschlecht', StringType()),
            StructField('alter', IntegerType()),
        ])

        df = session.createDataFrame(data=[form_data], schema=schema)


        @F.udf(session=_get_active_sessions().pop())
        def _random_id() -> str:
            id = uuid.uuid4()
            return str(id)


        # id_udf = F.udf(_random_id, return_type=StringType())
        df = df.withColumn(
            "id",
            _random_id(),
        )

        df.write.mode("append").save_as_table('dhac_ingress.input_data')

        # Display the result in the app
        st.write('New patients data loaded.')
        st.dataframe(df.select("id", F.current_date().alias("created_at")))
        st.success('Data successfully submitted to Snowflake!')
