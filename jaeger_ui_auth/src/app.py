from flask import Flask, request, redirect, make_response, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from functools import wraps
import requests
from config import CONFIG
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder=None)
JWT_SECRET = CONFIG["jwt_secret"]
JWT_ALGORITHM = CONFIG["jwt_algorithm"]
JAEGER_UI_URL = CONFIG["jaeger_ui_url"]

UI_USERS = {}
for account in CONFIG["ui_accounts"]:
    user_login, user_password = account.split("::")
    UI_USERS[user_login] = generate_password_hash(user_password)


# HTML форма для логина
login_page = """
<form method="POST" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-size: 1.5em;">
  <input name="username" placeholder="Username" style="margin-bottom: 20px; padding: 10px; width: 300px;"><br>
  <input type="password" name="password" placeholder="Password" style="margin-bottom: 20px; padding: 10px; width: 300px;"><br>
  <input type="submit" value="Login" style="padding: 10px 20px; font-size: 1em;">
</form>
"""


# Функция генерации JWT
def generate_token(username):
    payload = {
        "sub": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# Декоратор для проверки JWT
def jwt_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return redirect("/login")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return redirect("/login")
        except jwt.InvalidTokenError:
            return redirect("/login")
        return func(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in UI_USERS and check_password_hash(UI_USERS[username], password):
            token = generate_token(username)
            resp = make_response(redirect("/"))
            resp.set_cookie(
                "access_token", token, httponly=True, secure=True
            )  # Используй secure=True с HTTPS
            return resp
        return "Invalid login", 403
    return render_template_string(login_page)


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie("access_token", "", expires=0)  # Удаление cookie
    return resp


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@jwt_required
def proxy_jaeger(path):
    # Forward the request to Jaeger UI
    jaeger_url = f"{JAEGER_UI_URL}/{path}"

    logging.debug(f"Forwarding request to Jaeger UI: {jaeger_url}")

    headers = {key: value for key, value in request.headers if key.lower() != "host"}
    jaeger_resp = requests.request(
        method=request.method,
        url=jaeger_url,
        headers=headers,
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True,
    )
    # Exclude problematic headers
    excluded_headers = ["content-encoding", "transfer-encoding", "content-length"]
    headers = [
        (key, value)
        for key, value in jaeger_resp.headers.items()
        if key.lower() not in excluded_headers
    ]
    # headers = {key: value for key, value in jaeger_resp.headers.items()}
    # Return the response to the client
    return (jaeger_resp.raw.read(), jaeger_resp.status_code, headers)


@app.route("/static/<path:filename>")
@jwt_required
def serve_static(filename):
    static_url = f"{JAEGER_UI_URL}/static/{filename}"
    jaeger_resp = requests.get(static_url, stream=True, timeout=20)

    if jaeger_resp.status_code == 404:
        logging.error(f"Static file not found: {static_url}")

    excluded_headers = ["content-encoding", "transfer-encoding", "content-length"]
    headers = {
        key: value
        for key, value in jaeger_resp.headers.items()
        if key.lower() not in excluded_headers
    }

    response = make_response(jaeger_resp.content)
    response.status_code = jaeger_resp.status_code

    for key, value in headers.items():
        response.headers[key] = value

    return response


if __name__ == "__main__":
    # Запуск приложения через HTTPS
    app.run(ssl_context=("flask.crt", "flask.key"), port=5000)
