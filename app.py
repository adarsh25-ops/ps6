from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzywuzzy import process

# Load CSV dataset
df = pd.read_csv("food_data.csv")
foods_list = df['food'].unique().tolist()
diseases_list = df['disease'].unique().tolist()

# Chatbot function
def free_chat_bot(user_input):
    user_input_lower = user_input.lower()
    
    # Detect food using fuzzy matching
    food_match = process.extractOne(user_input_lower, foods_list)
    food = food_match[0] if food_match and food_match[1] > 60 else None
    
    # Detect disease using fuzzy matching
    disease_match = process.extractOne(user_input_lower, diseases_list)
    disease = disease_match[0] if disease_match and disease_match[1] > 60 else None
    
    # Lookup in CSV
    if food and disease:
        result = df[(df['food'] == food) & (df['disease'] == disease)]
        if not result.empty:
            rec = result.iloc[0]['recommendation']
            expl = result.iloc[0]['explanation']
            return f"{food.title()} ({rec}): {expl}"
        else:
            return "Sorry, no info available for this food and disease."
    else:
        missing = []
        if not food: missing.append("food")
        if not disease: missing.append("disease")
        return f"Couldn't identify: {', '.join(missing)}. Please mention them clearly."

# Create Flask app
app = Flask(__name__)
CORS(app)

# API endpoint
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("query", "")
    response = free_chat_bot(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
