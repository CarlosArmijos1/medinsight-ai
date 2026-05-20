import re

def clean_text(text: str) -> str:
    # Elimina lineas vacias multiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Elimina espacios extra
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()