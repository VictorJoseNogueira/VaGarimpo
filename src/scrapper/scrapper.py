import json
import os
import random
import re
import time

from playwright.sync_api import sync_playwright
from typing import Callable, Any
from src.core.database import db_connect, db_disconnect
from src.core.logger import logger
from src.services.db_service import post_a_job, read_all_jobs, read_specific_job, update_a_job

DEFAULT_MAX_PAGES = 1
DEFAULT_INITIAL_MAX_PAGES = 1
DEFAULT_PAGE_NUMBER = 1
MILLISECONDS_IN_SECOND = 1000
PLAYWRIGHT_WAIT_MIN_SECONDS = 2.5
PLAYWRIGHT_WAIT_MAX_SECONDS = 5
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

    @staticmethod
    def _project_needs_scraping(info: dict) -> bool:
        pass

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
        clean_title = re.sub(r"\s+", " ", titles).strip()
        ban_title = self._have_a_banned_word(word=clean_title)

        if clean_title and not ban_title:
            try:
                post_a_job({"title": clean_title, "link": complete_url})
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
            while page_number <= self.max_pages:
                page = browser.new_page()
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
                info["descricao"] = "Descrição bloqueada por conteúdo banido"
            else:
                info["descricao"] = description_text.strip()
        except Exception as e:
            logger.warning("Erro ao coletar descrição para %s: %s", title, e)
            info["descricao"] = "Descrição não disponível"

   
    @staticmethod
    def _extract_skills(page, info: dict, title: str) -> None:
        """Extrai habilidades desejadas do projeto da página."""
        try:
            logger.debug("Coletando habilidades para: %s", title)
            skills_locator = page.locator("div.container-habilidades a.habilidade")
            skills_locator.first.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            habilidades = skills_locator.all_inner_texts().lower()
            info[""] = [h.strip() for h in habilidades if h.strip()]
        except Exception as e:
            logger.debug(
                "Sem Habilidades Desejadas para %s ou erro: %s",
                title,
                e,
            )
            info["habilidades"] = []

    @staticmethod
    def _extract_details(page, info: dict, title: str) -> None:
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
                logger.info(f"chave: {chave} - valor: {valor}")
            info["details"] = info_adicionais
        except Exception as e:
            logger.info(
                "Sem Informações adicionais para %s ou erro: %s",
                title,
                e,
            )
            info["details"] = {}

    @staticmethod
    def _extract_user_info(page, info: dict, title: str) -> None:
        """Extrai informações do usuário/cliente do projeto da página."""
        try:
            logger.debug("Coletando nome para: %s", title)
            user_locator = page.locator("div.info-usuario-nome span.name")
            user_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            nome_usuario = user_locator.inner_text().lower().strip()
            info["nome_usuario"] = nome_usuario
        except Exception as e:
            logger.debug("Sem nome de usuário para %s ou erro: %s", title, e)
            info["nome_usuario"] = "Não informado"

    def _process_project_data(self, page, link: str, info: dict) -> None:
        """Processa os dados de um projeto específico."""
        page.goto(link)
        title = info.get("titulo", "Desconhecido")
        logger.debug("Coleta de links Iniciada %s", title)

        self._extract_description(page, info, title)
        self._extract_skills(page, info, title)
        self._extract_details(page, info, title)
        self._extract_user_info(page, info, title)

        page.wait_for_timeout(
            random.uniform(
                PLAYWRIGHT_WAIT_MIN_SECONDS,
                PLAYWRIGHT_WAIT_MAX_SECONDS,
            )
            * MILLISECONDS_IN_SECOND
        )
    @staticmethod
    def _extract_elements(page, element, field_check) -> str:
        if not field_check:
            logger.debug("Campo %s já preenchido, pulando extração", element)
            try:
                element_locator = page.locator(element)
                element_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
                )
                element_text = element_locator.inner_text().lower()
                page.wait_for_timeout(
                random.uniform(
                    PLAYWRIGHT_WAIT_MIN_SECONDS,
                    PLAYWRIGHT_WAIT_MAX_SECONDS,
                )
                * MILLISECONDS_IN_SECOND
                )
                logger.info(element_text)
                
                return element_text.strip()      
            except Exception as e:
                logger.warning("Erro ao coletar elemento %s: %s", element, e)
                return "Elemento não disponível"
        
    
   
    def scrap_page_get_data(self):
        """Orquestra a coleta de dados para todos os projetos."""
        with sync_playwright() as p:
            documents = read_all_jobs()
            start_time = time.time()
            browser = p.chromium.launch(
                headless=True,
                args=PLAYWRIGHT_LAUNCH_ARGS
            )
            page = browser.new_page()
            for doc in documents:
                page.goto(doc.link)
                try:
                    print(f"Coletando dados para: {doc.title}")
                    description = self._extract_elements(page, DESCRIPTION_ELEMENT, doc.description)
                    skills = self._extract_elements(page, SKILLS_ELEMENT, doc.skills)
                    username = self._extract_elements(page, USER_INFO_ELEMENT, doc.userName)
                    details = self._extract_details(page, doc, doc.title)
                    logger.warning(f"Dados coletados para {doc.title}: descrição='{description}', skills='{skills}', username='{username}', details='{details}'")
                    update_a_job(
                        url=doc.link,
                        description=description,
                        skills=skills,
                        username=username,
                        details=details
                    )
                except Exception as e:
                    logger.error(f"Falha ao processar a página {doc.link}: {e}")
            browser.close()
            logger.info("Coleta finalizada em %.2fs", time.time() - start_time)
            return self

    def save_json(self):
        if (
            os.path.exists(self.destiny_json)
            and os.path.getsize(self.destiny_json) > 0
        ):
            with open(self.destiny_json, "r", encoding="utf-8") as f:
                try:
                    current_data = json.load(f)
                except json.JSONDecodeError:
                    current_data = {}

        else:
            current_data = {}

        simulated_data = current_data.copy()
        simulated_data.update(self.projects_links_dict)
        if simulated_data == current_data:
            logger.info("Nenhum Novo dado Detectado")
            return self
        # persistir novos itens
        current_data.update(self.projects_links_dict)
        try:
            with open(self.destiny_json, "w", encoding="utf-8") as f:
                json.dump(
                    current_data,
                    f,
                    indent=JSON_DUMP_INDENT,
                    ensure_ascii=False,
                )
            logger.info(
                "Salvo %s registros em %s",
                len(self.projects_links_dict),
                self.destiny_json,
            )
        except Exception as e:
            logger.error("Falha ao salvar %s: %s", self.destiny_json, e)
        return self


def main():
    freela = r"https://www.99freelas.com.br/projects?categoria=web-mobile-e-software&sub-categorias=banco-de-dados+desenvolvimento-desktop+desenvolvimento-web&niveis-experiencia=iniciante%2Cintermediario&page=4"

    json_path = os.getenv("JSON_PATH", "src/data/projects.json")
    scrapper99Freela(
        link=freela, json_path=json_path, max_pages=1
    ).scrap_page_get_links().scrap_page_get_data().save_json()
    db_disconnect()

if __name__ == "__main__":
    main()
