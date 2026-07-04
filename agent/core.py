import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from agent.tools import TOOLS, TOOL_FUNCTIONS
from agent.prompts import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MODEL = "gemini-2.5-flash"
MAX_TURNS = 10  # safety fuse: never loop forever


def run_agent(messages: list) -> list:
    """
    Drive the tool-calling loop until the model gives a final answer.
    Takes the full conversation history and returns the updated history
    (including the assistant's final reply).
    """

    for turn in range(MAX_TURNS):
        # STEP 1: send the current conversation + tool definitions to the model.
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message

        # STEP 2: if the model did NOT request a tool, it's the final answer. Stop.
        if not msg.tool_calls:
            messages.append(msg)      # record the assistant's final reply
            return messages           # return the FULL updated conversation

        # STEP 3: the model wants tools. Record its request in the conversation.
        messages.append(msg)

        # STEP 4: run each requested tool and feed the result back.
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)  # JSON string -> dict

            # Trace what the model decided — this is how you debug an agent.
            print(f"  [trace] model called {name}({args})")

            func = TOOL_FUNCTIONS[name]   # dispatch: name -> real function
            result = func(**args)         # actually execute it

            # Tool results are sent back as TEXT, so serialize to a JSON string.
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
        # Loop back to STEP 1: the model now sees the results and decides next.

    # STEP 5 (safety): if we hit MAX_TURNS, stop instead of looping forever.
    return "Sorry, I couldn't finish within the allowed number of steps."


if __name__ == "__main__":
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Plan me a short afternoon in Kyoto."},
    ]
    conversation = run_agent(conversation)
    print("\n=== ITINERARY ===")
    print(conversation[-1].content)   # the last message is the assistant's reply