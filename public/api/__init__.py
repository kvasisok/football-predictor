from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Football Predictor on Vercel!"

if __name__ == '__main__':
    app.run()
