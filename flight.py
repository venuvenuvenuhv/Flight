from flask import Flask, render_template, request
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

df = pd.read_excel("C:/Users/Personal/Downloads/Data_Train (1).xlsx") 
df.dropna(inplace=True)

df["Journey_Day"] = pd.to_datetime(df["Date_of_Journey"], format="%d/%m/%Y").dt.day
df["Journey_Month"] = pd.to_datetime(df["Date_of_Journey"], format="%d/%m/%Y").dt.month
df["Dep_Hour"] = pd.to_datetime(df["Dep_Time"]).dt.hour
df["Dep_Minute"] = pd.to_datetime(df["Dep_Time"]).dt.minute

df = df[["Source", "Destination", "Journey_Day", "Journey_Month", "Dep_Hour", "Dep_Minute", "Price"]]

le_source = LabelEncoder()
le_dest = LabelEncoder()

df["Source"] = le_source.fit_transform(df["Source"])
df["Destination"] = le_dest.fit_transform(df["Destination"])

X = df.drop("Price", axis=1)
y = df["Price"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

@app.route("/", methods=["GET", "POST"])
def home():
    price = None
    sources = le_source.classes_
    destinations = le_dest.classes_
    error = None

    if request.method == "POST":
        source_input = request.form["Source"]
        destination_input = request.form["Destination"]

        try:
            source = le_source.transform([source_input])[0]
            destination = le_dest.transform([destination_input])[0]
        except:
            error = "Please select valid Source & Destination from the list."
            return render_template("index.html", price=None, sources=sources, destinations=destinations, error=error)

        date = request.form["Date"]
        time = request.form["Time"]

        journey_day = pd.to_datetime(date, format="%Y-%m-%d").day
        journey_month = pd.to_datetime(date, format="%Y-%m-%d").month
        dep_hour = int(time.split(":")[0])
        dep_minute = int(time.split(":")[1])

        input_data = pd.DataFrame({
            "Source": [source],
            "Destination": [destination],
            "Journey_Day": [journey_day],
            "Journey_Month": [journey_month],
            "Dep_Hour": [dep_hour],
            "Dep_Minute": [dep_minute]
        })

        price = round(model.predict(input_data)[0], 2)

    return render_template("index.html", price=price, sources=sources, destinations=destinations, error=error)


if __name__ == "__main__":
    app.run(debug=True)
