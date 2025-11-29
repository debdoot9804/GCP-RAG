import os
from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()


os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("API_VERSION")

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

deployment = os.getenv("OPENAI_EMBED_DEPLOYMENT_NAME")

print(f"Testing embedding deployment: {deployment}")

try:
    response = client.embeddings.create(
        model=deployment,
        input="Hello world from Debdoot"
    )

    print("✅ Connection OK! Sample embedding values:")
    print(response.data[0].embedding[:8])

except Exception as e:
    print("❌ Error connecting to Azure OpenAI:")
    print(e)
