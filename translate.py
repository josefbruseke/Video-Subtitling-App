import os
from openai import OpenAI
from dotenv import load_dotenv

def create_openai_client():
    """Create an OpenAI client using the provided API key."""
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    return OpenAI(api_key=OPENAI_API_KEY)

def traduzir_texto(texto, idioma_entrada, idioma_destino):
    print('traduzir tester')
    client = create_openai_client()
    mensagem = f"Translate this text from {idioma_entrada} to {idioma_destino} maintaining cohesion and continuity between the sentences as if translating a continuous dialogue: {texto}"
    response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": mensagem},
        ],
        n=1,
        stop=None,
        temperature=0.3)
    traducao = response.choices[0].message.content.strip()
    return traducao


