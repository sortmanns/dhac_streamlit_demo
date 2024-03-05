from firebase_auth_ui import draw_ui


# Your main app calling function
# For example, here my_app() is the final function which will be called to run the entire app
def my_app():
    print("User Authentication Successful. The app is opening!")


# Set Firebase config
firebase_config = {
    "apiKey": "AIzaSyBbj_45IHvLf6Oh837Xs7kUxs7ZcAjNjXw",
    "authDomain": "dhac-streamlit-demo.firebaseapp.com",
    "projectId": "dhac-streamlit-demo",
    "storageBucket": "dhac-streamlit-demo.appspot.com",
    "messagingSenderId": "902109338782",
    "appId": "1:902109338782:web:d489eefceb0c1f3c116f8f",
    "databaseURL": "",
}

draw_ui.run_authentication(firebase_config, my_app)
