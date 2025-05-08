import json
import os
import time

import dotenv
import requests
from blackhole_daily import DailyCall

dotenv.load_dotenv()


def create_web_call(api_url, api_key, payload):
    url = f"{api_url}/call/web"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if response.status_code == 201:
        call_id = data.get("id")
        web_call_url = data.get("webCallUrl")
        return call_id, web_call_url
    else:
        raise Exception(f"Error: {data['message']}")


class Vapi:
    def __init__(self, *, api_key, api_url="https://api.vapi.ai"):
        self.api_key = api_key
        self.api_url = api_url

    def start(
        self,
        *,
        assistant_id=None,
        assistant=None,
        assistant_overrides=None,
        squad_id=None,
        squad=None,
    ):
        # Start a new call
        if assistant_id:
            payload = {
                "assistantId": assistant_id,
                "assistantOverrides": assistant_overrides,
            }
        elif assistant:
            payload = {
                "assistant": assistant,
                "assistantOverrides": assistant_overrides,
            }
        elif squad_id:
            payload = {"squadId": squad_id}
        elif squad:
            payload = {"squad": squad}
        else:
            raise Exception("Error: No assistant specified.")

        call_id, web_call_url = create_web_call(self.api_url, self.api_key, payload)

        if not web_call_url:
            raise Exception("Error: Unable to create call.")

        print("Joining call... " + call_id)

        self.__client = DailyCall()
        self.__client.join(web_call_url)

    def stop(self):
        self.__client.leave()
        self.__client = None

    def send(self, message):
        """
        Send a generic message to the assistant.

        :param message: A dictionary containing the message type and content.
        """
        if not self.__client:
            raise Exception("Call not started. Please start the call first.")

        # Check message format here instead of serialization
        if not isinstance(message, dict) or "type" not in message:
            raise ValueError("Invalid message format.")

        try:
            self.__client.send_app_message(message)  # Send dictionary directly
        except Exception as e:
            print(f"Failed to send message: {e}")

    def add_message(self, role, content):
        """
        method to send text messages with specific parameters.
        """
        message = {"type": "add-message", "message": {"role": role, "content": content}}
        self.send(message)


def main():
    """Main function to demonstrate the BlackHole integration with Vapi"""

    api_key = os.getenv("VAPI_PUBLIC_KEY")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")

    # Create Vapi instance
    vapi = Vapi(api_key=api_key)

    # Load the assistant overrides from config.json
    assistant_overrides = json.load(open("config.json"))
    # Load the functions from functions_config.json
    assistant_overrides["model"]["tools"] = json.load(open("functions_config.json"))

    try:
        # Start the assistant (replace with your actual assistant ID)
        print("Starting assistant...")
        vapi.start(assistant_id=assistant_id, assistant_overrides=assistant_overrides)
        print("\nAudio is now being routed between BlackHole and Vapi assistant")
        print(
            "Speak into an application that outputs to BlackHole to talk to the assistant"
        )
        print(
            "The assistant's responses will be sent to BlackHole for other applications to use"
        )
        print("\nPress Ctrl+C to stop...")

        # Keep the program running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Clean up
        vapi.stop()
        print("Session ended")


if __name__ == "__main__":
    main()
