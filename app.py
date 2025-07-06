from flask import Flask, render_template, request
from utils.flight_data import fetch_and_process_flights

app = Flask(__name__)

@app.route('/')
def index():
    from_airport = request.args.get('from')
    to_airport = request.args.get('to')

    df, route_data, trend_data = fetch_and_process_flights(from_airport, to_airport)

    return render_template("index.html", routes=route_data, trends=trend_data)

if __name__ == "__main__":
    app.run(debug=True)
