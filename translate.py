import os   
from openai import OpenAI
from dotenv import load_dotenv

def create_openai_client():
    """Create an OpenAI client using the provided API key."""
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    return OpenAI(api_key=OPENAI_API_KEY)

def define_prompt(idioma_destino, texto):
    prompt = f"The dictionary below contains the index of a timestamp and the corresponding text. Return a dictionary with the translation of the text to {idioma_destino} with its associated index: {texto}"
    return prompt


def traduzir_texto(texto, idioma_destino):
    print('Tradução iniciada')
    client = create_openai_client()
    message = define_prompt(idioma_destino, texto)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": message},
        ],
        n=1,
        stop=None,
        temperature=0.2
    )
    traducao = response.choices[0].message.content.strip()
    print('Tradução finalizada')
    return traducao


