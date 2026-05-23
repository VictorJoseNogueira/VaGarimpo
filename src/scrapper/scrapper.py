import os
import random
import re
import time

from playwright.sync_api import sync_playwright

from src.core.database import db_connect, db_disconnect
from src.core.logger import logger
from src.database.db_service import post_a_job, read_specific_job

DEFAULT_MAX_PAGES = 1
DEFAULT_INITIAL_MAX_PAGES = 1
DEFAULT_PAGE_NUMBER = 1
MILLISECONDS_IN_SECOND = 1000
PLAYWRIGHT_WAIT_MIN_SECONDS = 1
PLAYWRIGHT_WAIT_MAX_SECONDS = 3
PLAYWRIGHT_WAIT_TIMEOUT_MS = 5000
PLAYWRIGHT_LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]
JSON_DUMP_INDENT = 4
DESCRIPTION_ELEMENT = "div[class*='project-description']"
SKILLS_ELEMENT = "div.container-habilidades a.habilidade"
USER_INFO_ELEMENT = "div.info-usuario-nome span.name"
MAPING_KEYS = {
    "categoria": "category",
    "subcategoria": "subcategory",
    "orçamento": "budget",
    "nível de experiência": "experience_level",
    "visibilidade": "visibility",
    "propostas": "proposals",
    "interessados": "interested",
    "propostas excluídas": "exclude_proposals",
    "tempo restante": "time_remaining",
    "valor mínimo": "minimum_value",
}


class scrapper99Freela:
    def __init__(
        self, link: str, json_path: str, max_pages: int = DEFAULT_MAX_PAGES
    ):
        self.link = link.rstrip("/")
        self.destiny_json = json_path
        self.projects_links_dict = {}
        self.page_number = 1
        self.max_pages = max_pages
        self.banned_words = [
            "php",
            "laravel",
            "symfony",
            "codeigniter",
            "cakephp",
            "laminas",
            "wordpress",
            "joomla",
            "drupal",
            "ghost",
            "elementor",
            "e-commerce",
            "comércio eletrônico",
            "loja virtual",
            "magento",
            "market",
            "marketplace",
            "woocommerce",
            "prestashop",
            "opencart",
            "shopify",
            "vtex",
            "nuvemshop",
            "tray",
            "loja integrada",
            "linx",
            "wix",
            "squarespace",
            "webflow",
            "bubble",
            "outsystems",
            "mendix",
            "no-code",
            "low-code",
            "jquery",
            "extjs",
            "mootools",
            "ruby",
            "ruby on rails",
            "c#",
            "asp.net",
            ".net",
            "elixir",
            "phoenix",
        ]
        db_connect()

    def _have_a_banned_word(self, word: str):
        have_banned_word = any(
            banned_word in word for banned_word in self.banned_words
        )
        return have_banned_word

    @staticmethod
    def _get_links_and_titles(page) -> list[str]:
        page.wait_for_selector("a[href*='/project/']")
        projects_links = page.locator("a[href*='/project/']").all()
        links_locator = page.locator("a[href*='/project/']")
        links_locator.first.wait_for(state="visible")
        projects_links = links_locator.all()
        return projects_links

    def _generate_target_url(self, page_number: int) -> str:
        if "page=" in self.link:
            return re.sub(r"page=\d+", f"page={page_number}", self.link)

        if "?" in self.link:
            return f"{self.link}&page={page_number}"

        return f"{self.link}?page={page_number}"

    @staticmethod
    def _is_valid_project_link(relative_url: str) -> bool:
        if not relative_url:
            return False

        return not (
            relative_url.endswith("/project/new") or "/project/new?" in relative_url
        )

    @staticmethod
    def _normalize_project_url(relative_url: str) -> str:
        if relative_url.startswith("/"):
            return f"https://www.99freelas.com.br{relative_url}"
        return relative_url

    def _process_project_link(self, locator) -> None:
        titles = locator.inner_text().lower()
        relative_url = locator.get_attribute("href")
        if not self._is_valid_project_link(relative_url):
            return

        complete_url = self._normalize_project_url(relative_url)
        if read_specific_job(complete_url):
            logger.debug(
                "Projeto já existe no banco e será ignorado: %s", complete_url
            )
            return

        clean_title = re.sub(r"\s+", " ", titles).strip()
        ban_title = self._have_a_banned_word(word=clean_title)

        if clean_title and not ban_title:
            self.projects_links_dict[complete_url] = {
                "title": clean_title,
                "link": complete_url,
            }
            try:
                logger.debug("Coletado: %s", clean_title)
            except Exception as e:
                logger.error("Erro ao coletar projeto: %s", e)

    def _collect_project_links(self, page) -> None:
        projects_links = self._get_links_and_titles(page)
        for locator in projects_links:
            self._process_project_link(locator)

    def scrap_page_get_links(self):
        with sync_playwright() as p:
            start_time = time.time()
            logger.info("Iniciando coleta de links (max_pages=%s)", self.max_pages)
            random_time = random.uniform(
                PLAYWRIGHT_WAIT_MIN_SECONDS, PLAYWRIGHT_WAIT_MAX_SECONDS
            )
            page_number = DEFAULT_PAGE_NUMBER
            browser = p.chromium.launch(
                headless=True,
                args=PLAYWRIGHT_LAUNCH_ARGS,
            )
            page = browser.new_page()
            while page_number <= self.max_pages:
                target_url = self._generate_target_url(page_number)
                page.goto(target_url)

                # Aguarda e captura os links dos projetos
                self._collect_project_links(page)

                page_number += 1
                page.wait_for_timeout(random_time * MILLISECONDS_IN_SECOND)
            browser.close()
            elapsed = time.time() - start_time
            logger.info(
                "Coleta de links finalizada. %s links coletados em %.2fs",
                len(self.projects_links_dict),
                elapsed,
            )
            return self

    def _extract_description(self, page, info: dict, title: str) -> None:
        """Extrai descrição do projeto da página."""
        try:
            logger.debug(
                "Coletando descrição para: %s",
                title,
            )
            description_locator = page.locator("div[class*='project-description']")
            description_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            description_text = description_locator.inner_text().lower()
            ban_description = self._have_a_banned_word(word=description_text)
            if ban_description:
                logger.warning(
                    "Descrição de %s bloqueada por conteúdo banido",
                    title,
                )
                info["descricao"] = "Descrição bloqueada por conteúdo banido"
            else:
                info["descricao"] = description_text.strip()
        except Exception as e:
            logger.warning("Erro ao coletar descrição para %s: %s", title, e)
            info["descricao"] = "Descrição não disponível"

    def _extract_details(self, page, doc: dict, title: str) -> dict:
        """Extrai tabela de detalhes do projeto da página."""
        try:
            logger.debug("Coletando detalhes para: %s", title)
            table_locator = page.locator("div.info-adicionais table")
            table_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            rows = table_locator.locator("tr").all()
            info_adicionais = {}
            for row in rows:
                chave = row.locator("th").inner_text().strip(" :").lower()
                valor = row.locator("td").inner_text().strip().lower()
                info_adicionais[chave] = valor
                logger.debug(f"chave: {chave} - valor: {valor}")
            doc["details"] = info_adicionais
            clean_data = self._format_brute_data(doc=info_adicionais)
            return clean_data
        except Exception as e:
            logger.warning(
                "Sem informações adicionais ou erro para %s: %s",
                title,
                e,
            )
            doc["details"] = {}
            return {}

    @staticmethod
    def _format_brute_data(doc: dict) -> dict:
        correct_data = {}
        for key, value in doc.items():
            clean_key = key.strip().lower()
            if clean_key in MAPING_KEYS:
                new_key = MAPING_KEYS[clean_key]
                correct_data[new_key] = value
            else:
                correct_data[clean_key] = value
        return correct_data

    @staticmethod
    def _extract_elements(page, element) -> str:
        try:
            element_locator = page.locator(element)
            element_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            element_text = element_locator.inner_text().lower()
            logger.debug(
                "Elemento extraído %s com %s caracteres",
                element,
                len(element_text),
            )

            return element_text.strip()
        except Exception as e:
            logger.warning("Erro ao coletar elemento %s: %s", element, e)
            return "Elemento não disponível"

    @staticmethod
    def _extract_list_elements(page, element) -> list[str]:
        try:
            element_locator = page.locator(element)
            # Aguarda o primeiro elemento correspondente ficar visível
            element_locator.first.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )

            elements_text = element_locator.all_inner_texts()
            # Remove espaços em branco e padroniza para minúsculas
            return [text.strip().lower() for text in elements_text if text.strip()]
        except Exception as e:
            logger.warning("Erro ao coletar lista de elementos %s: %s", element, e)
            return []

    def scrap_page_get_data(self):
        """Orquestra a coleta de dados para todos os projetos."""
        with sync_playwright() as p:
            start_time = time.time()
            browser = p.chromium.launch(headless=True, args=PLAYWRIGHT_LAUNCH_ARGS)
            page = browser.new_page()
            total_links = len(self.projects_links_dict)
            count = 1
            for doc in self.projects_links_dict.values():
                logger.info(
                    "Processando projeto %s/%s: %s",
                    count,
                    total_links,
                    doc["title"],
                )
                page.goto(doc["link"])
                try:
                    logger.info("Coletando dados para %s", doc["title"])
                    doc["description"] = self._extract_elements(
                        page=page, element=DESCRIPTION_ELEMENT
                    )
                    doc["skills"] = self._extract_list_elements(
                        page=page, element=SKILLS_ELEMENT
                    )
                    doc["userName"] = self._extract_elements(
                        page=page, element=USER_INFO_ELEMENT
                    )
                    doc["details"] = self._extract_details(
                        page=page, doc=doc, title=doc["title"]
                    )
                except Exception as e:
                    logger.error(f"Falha ao processar a página {doc['link']}: {e}")
                finally:
                    count += 1
                    page.wait_for_timeout(
                        random.uniform(
                            PLAYWRIGHT_WAIT_MIN_SECONDS,
                            PLAYWRIGHT_WAIT_MAX_SECONDS,
                        )
                        * MILLISECONDS_IN_SECOND
                    )
            browser.close()
            logger.info("Coleta finalizada em %.2fs", time.time() - start_time)
            return self

    def save_mongodb(self) -> None:
        for key, value in self.projects_links_dict.items():
            logger.debug(f"Salvando no MongoDB - {key}: {value}")
            post_a_job(self.projects_links_dict[key])
        return self


def main():
    freela = r"https://www.99freelas.com.br/projects?categoria=web-mobile-e-software&sub-categorias=banco-de-dados+desenvolvimento-desktop+desenvolvimento-web&niveis-experiencia=iniciante%2Cintermediario&page=4"

    json_path = os.getenv("JSON_PATH", "src/data/projects.json")
    scrapper99Freela(
        link=freela, json_path=json_path, max_pages=10
    ).scrap_page_get_links().scrap_page_get_data().save_mongodb()
    db_disconnect()


if __name__ == "__main__":
    main()
