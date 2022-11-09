from flask import Flask


app = Flask(__name__)


@app.route('/healthcare')
def healthcare():
    return 'Hello World'


@app.route('/')
def index():
    return '/healthcare for checking'


if __name__ == "__main__":
    app.run()
