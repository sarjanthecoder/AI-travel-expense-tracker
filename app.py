# app.py
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import json
import re

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyDGgu2atNoJNEl8N92mFE7JqJcApk4vb84"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/plan-trip", methods=["POST"])
def plan_trip():
    data = request.get_json()

    from_place = data.get("from")
    to_place = data.get("to")
    days = int(data.get("days"))
    explore_level = data.get("explore_level")
    people = int(data.get("people"))
    return_flight = data.get("returnFlight", True)

    prompt = f"""
    You are a smart travel cost assistant.

    A user is planning a trip:
    - From: {from_place}
    - To: {to_place}
    - Duration: {days} days
    - People: {people}
    - Exploration level: {explore_level}
    - Return Flight: {'Yes' if return_flight else 'No'}

    Your tasks:
    1. Strictly detect the official currency of `{from_place}` (e.g., Tokyo → JPY, Delhi → INR). Do NOT assume INR or default. Use currency relevant to that location.
    2. Estimate realistic costs **in that currency**:
       - ✈️ Flight cost (per person, one-way or return)
       - 🍽️ Food per day per person
       - 🏨 Stay per night per person
       - 🎉 Entertainment total per person

    3. Analyze the weather/climate of the destination `{to_place}` and suggest:
       - 2–3 items to carry (like sweater, umbrella, sunscreen, etc.)
       - Add a short reason and rough cost for each in the same currency

    Format your output exactly like this:
    Currency: <currency code>
    Flight: <number>
    Food: <number>
    Stay: <number>
    Entertainment: <number>
    Suggestions:
    - <Item1>: <reason> (~<cost>)
    - <Item2>: <reason> (~<cost>)
    - <Item3>: <reason> (~<cost>)
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        currency_match = re.search(r"Currency:\s*(\w+)", text)
        flight_match = re.search(r"Flight:\s*(\d+)", text)
        food_match = re.search(r"Food:\s*(\d+)", text)
        stay_match = re.search(r"Stay:\s*(\d+)", text)
        entertainment_match = re.search(r"Entertainment:\s*(\d+)", text)
        suggestions_match = re.findall(r"-\s*(.+?)\n", text[text.find("Suggestions:"):])

        currency = currency_match.group(1) if currency_match else "INR"
        flight = int(flight_match.group(1)) if flight_match else 0
        food = int(food_match.group(1)) if food_match else 0
        stay = int(stay_match.group(1)) if stay_match else 0
        entertainment = int(entertainment_match.group(1)) if entertainment_match else 0

        total_cost = (flight * (2 if return_flight else 1) + food * days + stay * days + entertainment) * people
        per_person = total_cost // people

        return jsonify({
            "currency": currency,
            "flight": flight,
            "food": food,
            "stay": stay,
            "entertainment": entertainment,
            "total_cost": total_cost,
            "per_person": per_person,
            "suggestions": suggestions_match
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)