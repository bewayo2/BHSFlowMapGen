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
3.  **Summarization**: Summarize each process step into a concise 2-4 word description for node labels. DO NOT use full sentences.
4.  **Orientation**: The diagram MUST have a vertical layout. Ensure `rankdir=TB;` is at the top of the DOT code.
5.  **Node Shapes**: Use appropriate shapes for different process elements:
    -   Start/End steps → ellipse
    -   Regular process steps → rectangle
    -   Decision points → diamond
    -   Data/documents → parallelogram
    -   Connectors/references → circle

## Styling and Layout
6.  **Spacing**: Use `nodesep=0.4` and `ranksep=0.6` for optimal readability.
7.  **Font**: Set `fontsize=10` and `fontname=\"Arial\"`.
8.  **Colors**: Assign a unique fill color to each distinct 'Responsible' role. Use a soft, professional color palette.
9.  **Node Labels**: The main `label` inside each node should ONLY contain the summarized process step description (2-4 words).
10. **External Role Labels**: The 'Responsible' role MUST be placed **outside** the node as an external label. Use the `xlabel` attribute for this, containing ONLY the role's name (e.g., `xlabel=\"Role Name\"`).
11. **Edges**: **Only label arrows that represent decision points (e.g., Yes/No).** All other arrows MUST NOT have a label. Remove all other edge descriptions.

## Process Analysis
12. **No Legend**: You MUST NOT create a legend subgraph. All role information will be attached to the nodes themselves using `xlabel`.

## Quality Standards
13. **Syntax**: Generate only valid DOT code that will render without errors.
14. **Clarity**: Make diagrams easy to read and understand.
15. **Completeness**: Include all process steps mentioned in the input.
16. **Professional**: Use consistent, business-appropriate styling.

# Output Format
Return your response in this exact format:
```dot
[your DOT code here]
```

# Example Structure
```dot
digraph ProcessFlow {{
    rankdir=TB;
    node [shape=box, style=filled, fontname=\"Arial\", fontsize=10];
    edge [fontname=\"Arial\", fontsize=10];
    nodesep=0.4;
    ranksep=0.6;
    
    // Process nodes - role is an external label (xlabel), and there is no legend.
    "start" [shape=ellipse, fillcolor=\"#e6f3ff\", label=\"Start Process\"];
    "decision1" [shape=diamond, fillcolor=\"#ffe6e6\", label=\"Decision Point\", xlabel=\"Role A\"];
    "step2" [fillcolor=\"#e6ffe6\", label=\"Another Step\", xlabel=\"Role B\"];
    "step3" [fillcolor=\"#e6ffe6\", label=\"Other Step\", xlabel=\"Role C\"];
    
    // Edges: Only decision points have labels
    "start" -> "decision1";
    "decision1" -> "step2" [label=\"Yes\"];
    "decision1" -> "step3" [label=\"No\"];
}}
```

# Process Input
–––––
{user_input}
–––––

Now generate the DOT code following all the above instructions. Think step by step:
1.  Read the process input and identify all steps.
2.  For each step, identify the 'Responsible' role and IGNORE all others (like 'Accountable').
3.  **Summarize each step's description into 2-4 words.**
4.  Assign a unique color to each 'Responsible' role.
5.  Create the DOT code for each node. The `label` has the summarized description, and the `xlabel` has ONLY the role name.
6.  Map the flow, connecting steps with arrows. **Only label arrows for decision points (e.g., Yes/No).**
7.  DO NOT create a legend.
8.  Final review to ensure all instructions were followed and syntax is valid.

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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0,
            max_tokens=2048,
        )

        response_content = completion.choices[0].message.content
        
        # Log the raw response for debugging
        print("--- OpenAI Raw Response ---")
        print(response_content)
        print("---------------------------")

        # Extract DOT code from markdown code block
        dot_code = ""
        if "```dot" in response_content:
            # Standard case: ```dot ... ```
            dot_code = response_content.split("```dot")[1].split("```")[0].strip()
        elif "```" in response_content:
            # Fallback for plain ``` ... ```
            potential_code = response_content.split("```")[1].strip()
            # Check if it looks like DOT code
            if potential_code.lower().startswith('digraph'):
                dot_code = potential_code
            else:
                # If it starts with 'dot', strip it
                dot_code = potential_code.lstrip('dot').strip()
        else:
            # If no markdown block is found, assume the whole response is the code
            dot_code = response_content.strip()

        # Final check to ensure it's a valid digraph
        if not dot_code.lower().strip().startswith('digraph'):
            raise ValueError("Failed to extract valid DOT code from the model's response.")
            
        print("--- Extracted DOT Code ---")
        print(dot_code)
        print("--------------------------")

        return jsonify({"dot": dot_code})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract-steps-roles-types', methods=['POST'])
def extract_steps_roles_types():
    try:
        data = request.get_json()
        user_input = data.get('text')
        if not user_input:
            return jsonify({"error": "No text provided"}), 400

        prompt = (
            "Extract the process steps from the following description. "
            "For each step, return a JSON object with 'description', 'role', and 'node_type' (rectangle, diamond, ellipse, etc.). "
            "Example: [{\"description\": \"Fill Report\", \"role\": \"Employee\", \"node_type\": \"rectangle\"}, ...]\n"
            "Description:\n" + user_input
        )

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=512,
        )
        import json
        import re
        response_content = completion.choices[0].message.content
        json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
        if json_match:
            steps_roles_types = json.loads(json_match.group(0))
        else:
            steps_roles_types = []
        return jsonify({"steps_roles_types": steps_roles_types})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract-process-structure', methods=['POST'])
def extract_process_structure():
    try:
        data = request.get_json()
        user_input = data.get('text')
        if not user_input:
            return jsonify({"error": "No text provided"}), 400

        prompt = (
            "Extract the process structure from the following description. "
            "Return a JSON object with two arrays: 'nodes' and 'edges'. "
            "Each node must have a unique 'id', a concise 'description' (2-4 words), a 'role' (Responsible only), and a 'node_type' (ellipse, rectangle, diamond, parallelogram, or circle). "
            "Each edge must have 'from' and 'to' (node ids), and an optional 'label' (for decision branches only, e.g., Yes/No). "
            "Example: {\"nodes\": [{\"id\": \"start\", \"description\": \"Start\", \"role\": \"User\", \"node_type\": \"ellipse\"}], \"edges\": [{\"from\": \"start\", \"to\": \"decision1\"}, {\"from\": \"decision1\", \"to\": \"step2\", \"label\": \"Yes\"}]}\n"
            "Description:\n" + user_input
        )

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=1024,
        )
        import json
        import re
        response_content = completion.choices[0].message.content
        print("--- OpenAI Raw Structure Response ---")
        print(response_content)
        print("-------------------------------------")
        json_match = re.search(r'\{[\s\S]*\}', response_content)
        if json_match:
            structure = json.loads(json_match.group(0))
        else:
            structure = {"nodes": [], "edges": []}
        return jsonify({"structure": structure})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-dot-from-structure', methods=['POST'])
def generate_dot_from_structure():
    try:
        data = request.get_json()
        structure = data.get('structure')
        if not structure:
            return jsonify({"error": "No structure provided"}), 400
        import json
        title = structure.get('title', '').strip() if isinstance(structure, dict) else ''
        title_instruction = ''
        if title:
            title_instruction = f"\n# Chart Title\nThe chart title is: '{title}'. Use this as the graph label (e.g., label=\"{title}\"; labelloc=\"t\"; labeljust=\"c\")."
        json_edit_instruction = ("\n# IMPORTANT: Use the provided node descriptions and roles exactly as given in the JSON below. "
            "Do not re-summarize, re-label, or reinterpret them. Only use the values from the JSON for node labels and roles.\n")
        prompt = (
            SYSTEM_PROMPT +
            title_instruction +
            json_edit_instruction +
            "\n# Process Structure (JSON)\n" +
            json.dumps(structure, indent=2) +
            "\n\nNow generate the DOT code following all the above instructions."
        )
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=2048,
        )
        response_content = completion.choices[0].message.content
        print("--- OpenAI DOT from Structure Response ---")
        print(response_content)
        print("------------------------------------------")
        dot_code = ""
        if "```dot" in response_content:
            dot_code = response_content.split("```dot")[1].split("```", 1)[0].strip()
        elif "```" in response_content:
            potential_code = response_content.split("```", 1)[1].strip()
            if potential_code.lower().startswith('digraph'):
                dot_code = potential_code
            else:
                dot_code = potential_code.lstrip('dot').strip()
        else:
            dot_code = response_content.strip()
        if not dot_code.lower().strip().startswith('digraph'):
            raise ValueError("Failed to extract valid DOT code from the model's response.")
        return jsonify({"dot": dot_code})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)