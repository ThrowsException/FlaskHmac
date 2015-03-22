import base64
import random
import hashlib
import hmac
from flask import Flask, request, render_template
from flask_login import LoginManager, login_required, UserMixin
from flask.ext.pymongo import PyMongo
from flask.ext.bcrypt import Bcrypt
from bson.json_util import dumps

app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
app.secret_key = 'monorailthecosmicballetgoeson'


@app.route("/login", methods=["GET", "POST"])
def login():
    '''user logs in with username and password sent as a form post'''
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            bits = random.getrandbits(256)
            key = base64.b64encode(hashlib.sha256(str(bits)).digest())
            mongo.db.keys.insert({'username': username, 'key': key})
            return key
        else:
            return "Not Authorized", 401
    else:
        return render_template("index.html")


@app.route("/user", methods=["GET", "POST"])
def user():
    '''create a test user to create an access code for'''
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if mongo.db.users.find_one({'username': username}):
            return "CONFLICT", 409

        password = bcrypt.generate_password_hash(password)
        user = mongo.db.users.insert({
            'username': username, 'password': password
        })
        return dumps({'user': user})

    return render_template("user.html")


@app.route("/test", methods=["GET"])
def test():
    return render_template("test.html")


@app.route("/api/test", methods=["GET"])
@login_required
def api_test():
    return "Worked"


@login_manager.header_loader
def load_user_from_header(header_val):
    '''see if this user sent the correct username and hashed message'''
    header_val = header_val.replace('Basic ', '', 1)
    val = header_val.split(':')
    if len(val) == 2:
        user = mongo.db.users.find_one({'username': val[0]})
        if user:
            key = mongo.db.keys.find_one({'username': val[0]})
            if check_signature(
                    key,
                    val[1],
                    request.method,
                    request.get_data()):
                return UserMixin()
    else:
        return "Not Authorized", 401


def check_signature(key, signature, verb, data):
    md5data = hashlib.md5(data).hexdigest()
    sig = hmac.new(
        str(key["key"]),
        ''.join([verb, md5data]),
        hashlib.sha256).digest()

    base64sig = base64.b64encode(sig)
    return base64sig == signature

if __name__ == "__main__":
    app.run("0.0.0.0")
