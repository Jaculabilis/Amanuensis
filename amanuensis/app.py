from flask import Flask, render_template

import config

app = Flask("amanuensis")
app.secret_key = bytes.fromhex(config.get('secret_key'))

@app.route("/")
def root():
	return render_template("admin.html", username="guest")
