import os  
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "https://cben-m3lqueak-westeurope.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "AhwfzfTZrbxKJ0ssB0QFDBykYmy9AZi6lJAilMfKJqT2Ziu9QuvlJQQJ99AKAC5RqLJXJ3w3AAAAACOG6jvA")  

    # Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# Function to generate a chat completion
def generate_chat_completion(history, user_message, max_tokens=800, temperature=0.7):
    """
    Generate a chat completion using Azure OpenAI with a given history and user message.
    
    :param history: List of previous messages in the chat.
    :param user_message: Current message from the user.
    :param max_tokens: Maximum number of tokens to generate.
    :param temperature: Sampling temperature for the response.
    :return: The generated chat completion.
    """
    # Add the new user message to the history
    history.append({"role": "user", "content": user_message})
    
    # Generate the chat completion
    completion = client.chat.completions.create(
        model=deployment,
        messages=history,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    
    # Add the AI's response to the history
    print(completion)
    ai_response = completion.choices[0].message['content']
    history.append({"role": "assistant", "content": ai_response})
    
    return ai_response, history

# Initialize chat history
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."}  # System message to guide the assistant's behavior
]

# Example usage
if __name__ == "__main__":
    user_input = input("You: ")
    while user_input.lower() != "exit":
        response, chat_history = generate_chat_completion(chat_history, user_input)
        print(f"Assistant: {response}")
        user_input = input("You: ")
