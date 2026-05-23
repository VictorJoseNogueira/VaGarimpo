import json

import spacy

from src.core.logger import logger

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

    logger.debug(
        "preprocess_text: texto original com %s tokens filtrados",
        len(tokens),
    )
    return " ".join(tokens)


def process_json(path: str = json_path) -> None:
    logger.info("Iniciando processamento de stop words em %s", path)
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

            logger.debug(
                "process_json: %s | título len=%s | descrição len=%s | habilidades=%s",
                title[:50],
                len(lem_title),
                len(lem_description),
                len(lem_skills),
            )

    logger.info("Processamento de stop words concluído em %s", path)
