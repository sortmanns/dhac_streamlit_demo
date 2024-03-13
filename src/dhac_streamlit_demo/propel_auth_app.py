import uuid

import numpy as np
import requests
import streamlit as st
import yaml
from propelauth_py import UnauthorizedException, init_base_auth
from snowflake.snowpark.session import _get_active_sessions
from snowflake.snowpark.types import StructType, StructField, StringType, IntegerType, DoubleType
from streamlit.web.server.websocket_headers import _get_websocket_headers
from snowflake.snowpark import functions as F


# Load the YAML file
with open('/src/.secrets_2/propelAuthKey.yaml', 'r') as file:
    data = yaml.safe_load(file)

api_key = data['api_key']


class Auth:
    def __init__(self, auth_url, integration_api_key):
        self.auth = init_base_auth(auth_url, integration_api_key)
        self.auth_url = auth_url
        self.integration_api_key = integration_api_key

    def get_user(self):
        access_token = get_access_token()

        if not access_token:
            return None

        try:
            return self.auth.validate_access_token_and_get_user("Bearer " + access_token)
        except UnauthorizedException as err:
            print("Error validating access token", err)
            return None

    def get_account_url(self):
        return self.auth_url + "/account"

    def logout(self):
        refresh_token = get_refresh_token()
        if not refresh_token:
            return False

        logout_body = {"refresh_token": refresh_token}
        url = f"{self.auth_url}/api/backend/v1/logout"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.integration_api_key,
        }

        response = requests.post(url, json=logout_body, headers=headers)

        return response.ok


def get_access_token():
    return get_cookie("__pa_at")


def get_refresh_token():
    return get_cookie("__pa_rt")


def get_cookie(cookie_name):
    headers = _get_websocket_headers()
    if headers is None:
        return None

    cookies = headers.get("Cookie") or headers.get("cookie") or ""
    for cookie in cookies.split(";"):
        split_cookie = cookie.split("=")
        if len(split_cookie) == 2 and split_cookie[0].strip() == cookie_name:
            return split_cookie[1].strip()

    return None


auth = Auth(
    "https://560282212.propelauthtest.com",
    api_key,
)

user = auth.get_user()
if user is None:
    st.error("Unauthorized")
    st.stop()

    # Main Streamlit app starts here
    # Connect to Snowflake
conn = st.connection('snowflake')
session = conn.session()

st.title('ICL Sizing Input Form')

# Form fields arranged in three columns
col1, col2 = st.columns(2)

# Column 1
with col1:
    geschlecht = st.selectbox('Geschlecht', ['Male', 'Female'])
    alter = st.selectbox('Alter', [x for x in range(0, 100)])
    auge = st.selectbox('Auge', ['OS', 'OD'])
    implant_size = st.selectbox('Implantat_Größe', [x for x in np.arange(11.25, 14, 0.25)])
    ACD = st.number_input('ACD', min_value=2.0, max_value=4.0, value=3.0, step=0.001, format="%0.3f")
    ACA_nasal = st.number_input('ACA_nasal', min_value=20.0, max_value=60.0, value=35.0, step=0.001, format="%0.3f")
    ACA_temporal = st.number_input('ACA_temporal', min_value=20.0, max_value=60.0, value=35.0, step=0.001,
                                   format="%0.3f")
    AtA = st.number_input('AtA', min_value=10.0, max_value=14.0, value=12.0, step=0.001, format="%0.3f")
    ACW = st.number_input('ACW', min_value=10.0, max_value=14.0, value=11.0, step=0.001, format="%0.3f")
    ARtAR_LR = st.number_input('ARtAR_LR', min_value=0, max_value=1000, value=250, step=1)

# Column 2
with col2:
    StS = st.number_input('StS', min_value=10.0, max_value=14.0, value=11.0, step=0.001, format="%0.3f")
    StS_LR = st.number_input('StS_LR', min_value=0, max_value=1000, value=250, step=1)
    CBID = st.number_input('CBID', min_value=10.0, max_value=14.0, value=11.0, step=0.001, format="%0.3f")
    CBID_LR = st.number_input('CBID_LR', min_value=500, max_value=2000, value=1000, step=1)
    mPupil = st.number_input('mPupil', min_value=3.0, max_value=9.0, value=6.0, step=0.01)

    WtW_MS_39 = st.number_input('WtW_MS_39', min_value=10.0, max_value=13.0, value=11.0, step=0.01)
    WtW_IOL_Master = st.number_input('WtW_IOL_Master', min_value=10.0, max_value=13.0, value=11.0, step=0.1,
                                     format="%0.1f")
    Sphaere = st.number_input('Sphäre', min_value=-25.0, max_value=0.0, value=-3.0, step=0.01, format="%0.2f")

    Zylinder = st.number_input('Zylinder', min_value=-5.0, max_value=0.0, value=-0.5, step=0.25, format="%0.2f")
    Achse = st.number_input('Achse', min_value=0, max_value=180, value=90, step=1)

# Customizing the Submit button inside st.form
with st.form(key='my_form'):
    submit_button = st.form_submit_button('Submit', help='Click to submit the form')

    # Check if the form is submitted
    if submit_button:
        # Get form data
        form_data = {
            'geschlecht': geschlecht,
            'alter': alter,
            'auge': auge,
            'implant_size': implant_size,
            'ACD': ACD,
            'ACA_nasal': ACA_nasal,
            'ACA_temporal': ACA_temporal,
            'AtA': AtA,
            'ACW': ACW,
            'ARtAR_LR': ARtAR_LR,
            'StS': StS,
            'StS_LR': StS_LR,
            'CBID': CBID,
            'CBID_LR': CBID_LR,
            'mPupil': mPupil,
            'WtW_MS_39': WtW_MS_39,
            'WtW_IOL_Master': WtW_IOL_Master,
            'Sphaere': Sphaere,
            'Zylinder': Zylinder,
            'Achse': Achse
        }

        schema = StructType([
            StructField('geschlecht', StringType()),
            StructField('alter', IntegerType()),
            StructField('auge', StringType()),
            StructField('implant_size', DoubleType()),
            StructField('ACD', DoubleType()),
            StructField('ACA_nasal', DoubleType()),
            StructField('ACA_temporal', DoubleType()),
            StructField('AtA', DoubleType()),
            StructField('ACW', DoubleType()),
            StructField('ARtAR_LR', IntegerType()),
            StructField('StS', DoubleType()),
            StructField('StS_LR', IntegerType()),
            StructField('CBID', DoubleType()),
            StructField('CBID_LR', IntegerType()),
            StructField('mPupil', DoubleType()),
            StructField('WtW_MS_39', DoubleType()),
            StructField('WtW_IOL_Master', DoubleType()),
            StructField('Sphaere', DoubleType()),
            StructField('Zylinder', DoubleType()),
            StructField('Achse', IntegerType())
        ])

        df = session.createDataFrame(data=[form_data], schema=schema)


        @F.udf(session=_get_active_sessions().pop())
        def _random_id() -> str:
            id = uuid.uuid4()
            return str(id)


        # id_udf = F.udf(_random_id, return_type=StringType())
        df = df.withColumn(
            "patient_id",
            _random_id(),
        )

        df = df.withColumn(
            "user_id",
            F.lit(user.user_id),
        )

        df.write.mode("append").save_as_table('app_ingress.input_data')

        df = df.withColumn(
            "sts_cbid_implS",
            (F.col("StS") + F.col("CBID")) / 2 - F.col("implant_size")
        )
        df = df.withColumn(
            "sts_cbid_lr",
            (F.col("StS_LR") + F.col("CBID_LR")) / 2
        )
        df = df.withColumn(
            "vault",
            1615.0711983535798 - 63.88600034 * F.col("AtA") - 162.8446239 * F.col(
                "sts_cbid_implS") - 0.63335823 * F.col("sts_cbid_lr")
        )



        result_df = df.select("user_id", "patient_id", 'sts_cbid_implS', 'sts_cbid_lr', 'vault', F.current_date().alias("created_at"))
        result_df.write.mode("append").save_as_table('model_results.model_v1')

        # Display the result in the app
        st.write(f'Predicted Vault for implant size: {implant_size}:')
        st.dataframe(df.select("user_id", "patient_id", "vault", F.current_date().alias("created_at")))
        st.success('Data successfully submitted to Snowflake!')
