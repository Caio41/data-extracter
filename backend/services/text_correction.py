from services.openai_setup import client


def corrigir_texto(prompt: str):
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
      {'role': 'system', 'content': 'Seu objetivo é corrigir textos. Você irá receber uma frase ou um parágrafo que pode conter inconsistências como: Números no lugar de letras, símbolos aleatórios ou até mesmo palavras que não fazem sentido. Você deve corrigir essa frase e retornar APENAS a frase original corrigida.'},
      {"role": "user", "content": prompt}
    ]
  )

  return completion.choices[0].message.content


