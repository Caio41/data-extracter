from config.openai_setup import client


setup_prompt = """Seu objetivo é corrigir textos com erros de reconhecimento óptico de caracteres (OCR).
                  Você receberá uma frase ou um parágrafo contendo possíveis inconsistências, como:
                    - Números no lugar de letras (c0rret0 → correto)
                    - Símbolos aleatórios misturados ao texto (t#exto → texto)
                    - Palavras distorcidas que ainda podem ser interpretadas (h0je é um d1a b0m → hoje é um dia bom)

                  Instruções importantes:
                    - Corrija apenas erros evidentes de OCR, sem mudar o significado do texto.
                    - Não reescreva frases, apenas corrija os erros.
                    - Sua resposta deve conter apenas o texto corrigido, sem explicações ou comentários.
                    - Caso nenhum texto seja recebido, não retorne nada.

                  Exemplo:
                  Entrada: "E1e est@va n0 1ugar ceRto na h0ra c3rta."
                  Saída esperada: "Ele estava no lugar certo na hora certa."""


def corrigir_texto(prompt: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {
                "role": "system",
                "content": setup_prompt,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return completion.choices[0].message.content
