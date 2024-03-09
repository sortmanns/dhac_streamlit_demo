# streamlit_app.py

import hmac
import os
import uuid
import streamlit as st
from snowflake.snowpark import functions as F
from snowflake.snowpark.session import _get_active_sessions
from snowflake.snowpark.types import (DoubleType, IntegerType, StringType,
                                      StructField, StructType)


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate(os.environ.get('serviceAccountKey.json'))
firebase_admin.initialize_app(cred)

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
            F.lit("Firebase"),
        )

        df.write.mode("append").save_as_table('dhac_ingress.input_data')

        # Display the result in the app
        st.write('New patients data loaded.')
        st.dataframe(df.select("id", F.current_date().alias("created_at")))
        st.success('Data successfully submitted to Snowflake!')
