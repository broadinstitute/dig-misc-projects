
# imports
import openai
import os

# Set your API key
KEY_CHAT = os.getenv('CHAT_KEY')
KEY_GPT_ID = os.getenv('CHAT_TRANSLATEUR_ID')
openai.api_key = KEY_CHAT


# Set your deployment ID or CustomGPT model name
# custom_model = "your-custom-gpt-id"  # Replace with your CustomGPT deployment ID
custom_model = KEY_GPT_ID  # Replace with your CustomGPT deployment ID

chat_query = '''
what are common biological pathways between type 2 diabetes and alzheimer's disease?
'''

response = openai.ChatCompletion.create(
    model=custom_model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": chat_query}
    ]
)

# Extract and print the response
print(response['choices'][0]['message']['content'])

