from flask import Flask, render_template
from modules.environment import PI_API_KEY
app = Flask(__name__)

header = {
    'Authorization': f"Key {PI_API_KEY}"
}


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port="5173"        
)