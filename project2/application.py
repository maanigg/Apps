import os

from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from loginn import login_required

from collections import deque

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

usersLogged = []

my_messages = []

channels = []

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        if username not in usersLogged:
            usersLogged.append(username)
            session['username'] = username
            session.permanent = True
            return render_template('home.html', channels = channels)
        else:
            return render_template('login.html',message="User aldready Exists")
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass
    session.clear()
    return redirect("/")

@socketio.on("channel_creation")
def channel_creation(channel):
	# channel name is taken
	if channel in channels:
		emit("channel_error", "This name is already taken!")
	# success
	else:
		# add channel to the list of channels
		channels.append(channel)
		my_messages[channel] = []
		# add user to the channel
		join_room(channel)
		current_channel = channel
		data = {"channel": channel, "messages": my_messages[channel]}
		emit("join_channel", data)
