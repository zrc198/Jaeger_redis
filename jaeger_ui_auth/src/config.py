import os
import sys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("config_jaeger_ui_auth.env"))

try:
    CONFIG = {
        "jwt_secret": os.environ["JWT_SECRET"],
        "jwt_algorithm": os.environ["JWT_ALGORITHM"],
        "ui_accounts": os.environ["UI_ACCOUNTS"].split(","),
        "jaeger_ui_url": os.environ["JAEGER_UI_URL"],
    }
except KeyError as error:
    print("KeyError: {}".format(error))
    sys.exit(-1)
