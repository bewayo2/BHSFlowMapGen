import os
import openai
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please create a .env file with this key.")
client = openai.OpenAI()

SYSTEM_PROMPT = """You are an expert Graphviz diagram generator specializing in process flow charts. Your task is to convert process descriptions into clean, well-structured DOT code that renders as professional flowcharts.

# Role and Objective
- Convert process descriptions into DOT code for vertical flowcharts.
- Your primary focus is on accurately representing the process flow and **only the responsible roles**.
- Generate only valid DOT syntax that can be rendered immediately.

# Instructions

## Core Requirements
1.  **Output Format**: Return ONLY valid DOT code between triple backticks (```dot ... ```).
2.  **RACI Filtering**: From the input, extract ONLY the 'Responsible' role for each step. All other roles (e.g., Accountable, Consulted, Informed) MUST be completely ignored and EXCLUDED.
3.  **Orientation**: Always use vertical layout with `rankdir=TB`.
4.  **Node Shapes**: Use appropriate shapes for different process elements:
    -   Start/End steps → ellipse
    -   Regular process steps → rectangle
    -   Decision points → diamond
    -   Data/documents → parallelogram
    -   Connectors/references → circle

## Styling and Layout
5.  **Spacing**: Use `nodesep=0.4` and `ranksep=0.6` for optimal readability.
6.  **Font**: Set `fontsize=10` and `fontname="Arial"`.
7.  **Colors**: Assign a unique fill color to each distinct 'Responsible' role. Use a soft, professional color palette.
8.  **Node Labels**: The main `label` inside each node should ONLY contain the process step description (wrap long text with `\\n`).
9.  **External Role Labels**: The 'Responsible' role MUST be placed **outside** the node as an external label. Use the `xlabel` attribute for this, containing ONLY the role's name (e.g., `xlabel="Role Name"`).
10. **Edges**: Include descriptive labels on all arrows showing conditions or outputs.

## Process Analysis
11. **No Legend**: You MUST NOT create a legend subgraph. All role information will be attached to the nodes themselves using `xlabel`.

## Quality Standards
12. **Syntax**: Generate only valid DOT code that will render without errors.
13. **Clarity**: Make diagrams easy to read and understand.
14. **Completeness**: Include all process steps mentioned in the input.
15. **Professional**: Use consistent, business-appropriate styling.

# Output Format
Return your response in this exact format:
```dot
[your DOT code here]
```

# Example Structure
```dot
digraph ProcessFlow {{
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=10];
    nodesep=0.4;
    ranksep=0.6;
    
    // Process nodes - role is an external label (xlabel), and there is no legend.
    "start" [shape=ellipse, fillcolor="#e6f3ff", label="Start Process"];
    "step1" [fillcolor="#ffe6e6", label="Step 1 Description", xlabel="Role A"];
    "step2" [fillcolor="#e6ffe6", label="Step 2 Description", xlabel="Role B"];
    
    // Edges with labels
    "start" -> "step1" [label="Trigger"];
    "step1" -> "step2" [label="Output"];
}}
```

# Process Input
–––––
{user_input}
–––––

Now generate the DOT code following all the above instructions. Think step by step:
1.  Read the process input and identify all steps.
2.  For each step, identify the 'Responsible' role and IGNORE all others (like 'Accountable').
3.  Assign a unique color to each 'Responsible' role.
4.  Create the DOT code for each node. The `label` has the description, and the `xlabel` has ONLY the role name.
5.  Map the flow, connecting steps with arrows and labels.
6.  DO NOT create a legend.
7.  Final review to ensure all instructions were followed and syntax is valid.

Return only the DOT code between triple backticks."""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-dot', methods=['POST'])
def generate_dot():
    try:
        data = request.get_json()
        user_input = data.get('text')

        if not user_input:
            return jsonify({"error": "No text provided"}), 400

        prompt = SYSTEM_PROMPT.format(user_input=user_input)

        completion = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0,
            max_tokens=2048,
        )

        response_content = completion.choices[0].message.content
        
        # Extract DOT code from markdown code block
        if "```dot" in response_content:
            dot_code = response_content.split("```dot")[1].split("```")[0].strip()
        elif "```" in response_content:
            dot_code = response_content.split("```")[1].strip()
            if dot_code.startswith('dot'):
                dot_code = dot_code[3:].strip()
        else:
            dot_code = response_content.strip()

        return jsonify({"dot": dot_code})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 