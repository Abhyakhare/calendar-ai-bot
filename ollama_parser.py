import ollama
import json

def parse_command_with_ollama(prompt):
    full_prompt = f"""
You are a smart assistant that extracts structured meeting details from natural language input.

Your job is to extract and return a JSON object with the following fields:
- "To": list of names who are in TO
- "Cc": list of names who are in CC
- "Date": meeting date
- "Time": meeting time
- "Agenda": purpose of the meeting

🟡 Rules:
- If a name is mentioned "in TO", include it only in the "To" list.
- If a name is mentioned "in CC", include it only in the "Cc" list.
- Do not put the same person in both To and Cc.
- If no "TO" or "CC" is mentioned for a name, default them to "To".
- Always return a valid JSON object (not plain text or explanation).
- If no CC recipients are found, return "Cc": [].
- Keep the original natural casing (e.g. "Abhya Khare").

🟢 Format strictly as:
{{
  "To": [...],
  "Cc": [...],
  "Date": "...",
  "Time": "...",
  "Agenda": "..."
}}

### 🧪 Example 1:
Input: "Book a meeting with John Smith in TO and Jane Doe in CC on July 10 at 2 PM for product planning"
Output:
{{
  "To": ["John Smith"],
  "Cc": ["Jane Doe"],
  "Date": "July 10",
  "Time": "2 PM",
  "Agenda": "product planning"
}}

### 🧪 Example 2:
Input: "Schedule a meeting with Alice Brown and Bob White at 11 AM on June 20 for Q2 roadmap"
Output:
{{
  "To": ["Alice Brown", "Bob White"],
  "Cc": [],
  "Date": "June 20",
  "Time": "11 AM",
  "Agenda": "Q2 roadmap"
}}

### 🔍 Now parse this:
Input: "{prompt}"
Output:
"""

    # Run prompt through Ollama
    response = ollama.chat(
        model='mistral',  # or 'llama3', 'phi3', etc.
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )

    # Print raw response for debugging
    print("\n📩 Raw model response:\n", response['message']['content'])

    # Parse JSON safely
    try:
        json_output = json.loads(response['message']['content'])
        return json_output
    except json.JSONDecodeError as e:
        print("\n❌ Failed to parse JSON:", str(e))
        return None

if __name__ == "__main__":
    user_input = input("Enter command: ")
    parsed = parse_command_with_ollama(user_input)

    if parsed:
        print("\n✅ Parsed:", parsed)
    else:
        print("\n⚠️ Could not parse the input into structured JSON.")

