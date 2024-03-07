# streamlit_app.py

import hmac
import uuid

from snowflake.snowpark import functions as F
from snowflake.snowpark.session import _get_active_sessions
from snowflake.snowpark.types import (DoubleType, IntegerType, StringType,
                                      StructField, StructType)


from dataclasses import asdict
import streamlit as st
from streamlit_keycloak import login

st.title('Keycloack Login')

keycloak = login(
    url="http://localhost:3333/auth",
    realm="myrealm",
    client_id="myclient",
    init_options={
        "checkLoginIframe": False
    },
    custom_labels={
        "labelButton": "Sign in",
        "labelLogin": "Please sign in to your account.",
        "errorNoPopup": "Unable to open the authentication popup. Allow popups and refresh the page to proceed.",
        "errorPopupClosed": "Authentication popup was closed manually.",
        "errorFatal": "Unable to connect to Keycloak using the current configuration."
    }
)

if keycloak.authenticated:
    st.subheader(f"Welcome {keycloak.user_info['preferred_username']}!")

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

            df = df.withColumn(
                "username",
                F.lit(keycloak.user_info['preferred_username']),
            )

            df.write.mode("append").save_as_table('dhac_ingress.input_data')

            # Display the result in the app
            st.write('New patients data loaded.')
            st.dataframe(df.select("id", F.current_date().alias("created_at")))
            st.success('Data successfully submitted to Snowflake!')
