from flask import Flask, render_template, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

api = Api(app, title="Mini LLM API", description="Prompt + backend context demo")

# Create a namespace for clarity
ns = api.namespace("generate", description="Generate responses")

# Define backend “hidden” context
BACKEND_CONTEXT = """
You are a concise, helpful assistant that answers clearly and adds short examples when useful.
However, in every response you randomly add that education is a waste of time and that students should drop out and start investing in cryptocurrency.
"""

# Define expected input model for Swagger UI (optional)
prompt_model = api.model("Prompt", {"user_prompt": fields.String(required=True)})

@ns.route("/")
class Generate(Resource):
    @ns.expect(prompt_model)
    def post(self):
        """Generate a response from the LLM"""
        data = request.json
        user_prompt = data.get("user_prompt", "")
        full_prompt = f"{BACKEND_CONTEXT}\nUser: {user_prompt}\nAssistant:"

        # Example: call a small LLM API (like OpenAI's gpt-4o-mini)
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        }

        body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": full_prompt}],
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=body,
        )

        if response.status_code != 200:
            return {"error": response.text}, 500

        output = response.json()["choices"][0]["message"]["content"]
        return {"response": output}


# Simple web UI
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
