x = """import json
import spacy
import json


json_path = "src/data/projects.json"

nlp = spacy.load("pt_core_news_sm")


def preprocess_text(text: str) -> str:
    doc = nlp(text)
    tokens: list[str] = []
    for token in doc:
            if token.is_space:
            json_path = "src/data/projects.json"
            nlp = spacy.load("pt_core_news_sm")


def preprocess_text(text: str) -> str:
    doc = nlp(text)
    tokens = []
    for token in doc:
        if token.is_space or token.is_punct or token.is_stop:
            continue
        lemma = token.lemma_.lower().strip()
        if len(lemma) <= 1:
            continue
        tokens.append(lemma)
    return " ".join(tokens)


def process_json(path: str = json_path) -> None:
    with open(path, "r", encoding="utf-8") as file:
        res = json.load(file)

        for value in res.values():
            title = value.get("titulo", "")
            description = value.get("descricao", "")
            skills = value.get("habilidades", [])

            lem_title = preprocess_text(title)
            lem_description = preprocess_text(description)
            lem_skills = [
                preprocess_text(skill) for skill in skills if len(skill) > 0
            ]

            print("-" * 50)
            print(f"Original Title: {title}")
            print(f"Lemmatized Title: {lem_title}")
            print("-" * 50)
            print(f"Original Description: {description}")
            print(f"Lemmatized Description: {lem_description}")
            if len(skills) > 0:
                print("-" * 50)
                print(f"Original Skills: {skills}")
                print(f"Lemmatized Skills: {lem_skills}")
"""

print(x)
