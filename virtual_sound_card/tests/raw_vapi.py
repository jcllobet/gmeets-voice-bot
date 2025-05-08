import os
import time
from vapi_python import Vapi
import dotenv

dotenv.load_dotenv()

def main():
    """Main function to demonstrate the BlackHole integration with Vapi"""
    
    api_key = os.getenv("VAPI_PUBLIC_KEY")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")

    # Create Vapi instance
    vapi = Vapi(api_key=api_key)
    
    try:
        # Start the assistant (replace with your actual assistant ID)
        print("Starting assistant...")
        vapi.start(assistant_id=assistant_id)
        
        print("\nAudio is now being routed between BlackHole and Vapi assistant")
        print("Speak into an application that outputs to BlackHole to talk to the assistant")
        print("The assistant's responses will be sent to BlackHole for other applications to use")
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