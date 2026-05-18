import json
import os
import random
import re
import time

from playwright.sync_api import sync_playwright

from app.logger import logger

DEFAULT_MAX_PAGES = 1
DEFAULT_INITIAL_MAX_PAGES = 5
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


class scrapper_99_freela:
    def __init__(
        self, link: str, json_path: str, max_pages: int = DEFAULT_MAX_PAGES
    ):
        self.link = link.rstrip("/")
        self.projects_links_dict = {}
        self.destiny_json = json_path
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

    def have_a_banned_word(self, word: str):
        have_banned_word = any(
            banned_word in word for banned_word in self.banned_words
        )
        return have_banned_word

    def scrap_page_get_links(self):
        with sync_playwright() as p:
            start_time = time.time()
            logger.info("Iniciando coleta de links (max_pages=%s)", self.max_pages)
            random_time = random.uniform(
                PLAYWRIGHT_WAIT_MIN_SECONDS, PLAYWRIGHT_WAIT_MAX_SECONDS
            )
            page_number = DEFAULT_PAGE_NUMBER
            while page_number <= self.max_pages:
                browser = p.chromium.launch(
                    headless=True,
                    args=PLAYWRIGHT_LAUNCH_ARGS,
                )
                page = browser.new_page()
                if "page=" in self.link:
                    target_url = re.sub(
                        r"page=\d+", f"page={page_number}", self.link
                    )

                elif "?" in self.link:
                    target_url = f"{self.link}&page={page_number}"
                else:
                    target_url = f"{self.link}?page={page_number}"

                page.goto(target_url)

                # Aguarda e captura os links dos projetos
                page.wait_for_selector("a[href*='/project/']")
                projects_links = page.locator("a[href*='/project/']").all()

                links_locator = page.locator("a[href*='/project/']")
                links_locator.first.wait_for(state="visible")
                projects_links = links_locator.all()

                for locator in projects_links:
                    titles = locator.inner_text()
                    relative_url = locator.get_attribute("href")

                    if not relative_url:
                        continue

                    # 1. FILTRO: Ignora botões globais de criar novo projeto
                    if (
                        relative_url.endswith("/project/new")
                        or "/project/new?" in relative_url
                    ):
                        continue

                    complete_url = (
                        f"https://www.99freelas.com.br{relative_url}"
                        if relative_url.startswith("/")
                        else relative_url
                    )
                    clean_title = re.sub(r"\s+", " ", titles).strip()
                    ban_title = self.have_a_banned_word(word=clean_title)

                    if (
                        clean_title
                        and not ban_title
                        and complete_url not in self.projects_links_dict
                    ):
                        self.projects_links_dict[complete_url] = {
                            "titulo": clean_title
                        }
                        logger.debug("Coletado: %s", clean_title)
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
        if info.get("descricao"):
            logger.debug(
                "Descrição já existente para %s, pulando coleta.",
                title,
            )
            return

        try:
            logger.debug(
                "Coletando descrição para: %s",
                title,
            )
            description_locator = page.locator("div[class*='project-description']")
            description_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            description_text = description_locator.inner_text()
            ban_description = self.have_a_banned_word(word=description_text)
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
        if info.get("habilidades"):
            logger.debug(
                "Habilidades já existentes para %s, pulando coleta.",
                title,
            )
            return

        try:
            logger.debug("Coletando habilidades para: %s", title)
            skills_locator = page.locator("div.container-habilidades a.habilidade")
            skills_locator.first.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            habilidades = skills_locator.all_inner_texts()
            info["habilidades"] = [h.strip() for h in habilidades if h.strip()]
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
        if info.get("detalhes"):
            logger.debug(
                "Detalhes já existentes para %s, pulando coleta.",
                title,
            )
            return

        try:
            logger.debug("Coletando detalhes para: %s", title)
            table_locator = page.locator("div.info-adicionais table")
            table_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            rows = table_locator.locator("tr").all()
            info_adicionais = {}
            for row in rows:
                chave = row.locator("th").inner_text().strip(" :")
                valor = row.locator("td").inner_text().strip()
                info_adicionais[chave] = valor
            info["detalhes"] = info_adicionais
        except Exception as e:
            logger.debug(
                "Sem Informações adicionais para %s ou erro: %s",
                title,
                e,
            )
            info["detalhes"] = {}

    @staticmethod
    def _extract_user_info(page, info: dict, title: str) -> None:
        """Extrai informações do usuário/cliente do projeto da página."""
        if info.get("nome_usuario"):
            logger.debug(
                "Nome de usuário já existente para %s, pulando coleta.",
                title,
            )
            return

        try:
            logger.debug("Coletando nome para: %s", title)
            user_locator = page.locator("div.info-usuario-nome span.name")
            user_locator.wait_for(
                state="visible", timeout=PLAYWRIGHT_WAIT_TIMEOUT_MS
            )
            nome_usuario = user_locator.inner_text().strip()
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
        scrapper_99_freela._extract_skills(page, info, title)
        scrapper_99_freela._extract_details(page, info, title)
        scrapper_99_freela._extract_user_info(page, info, title)

        page.wait_for_timeout(
            random.uniform(
                PLAYWRIGHT_WAIT_MIN_SECONDS,
                PLAYWRIGHT_WAIT_MAX_SECONDS,
            )
            * MILLISECONDS_IN_SECOND
        )

    def scrap_page_get_data(self):
        """Orquestra a coleta de dados para todos os projetos."""
        with sync_playwright() as p:
            start_time = time.time()
            logger.info(
                "Iniciando coleta de dados para %s projetos",
                len(self.projects_links_dict),
            )
            browser = p.chromium.launch(
                headless=True,
                args=PLAYWRIGHT_LAUNCH_ARGS,
            )
            page = browser.new_page()

            for link, info in self.projects_links_dict.items():
                self._process_project_data(page, link, info)

            browser.close()
            elapsed = time.time() - start_time
            logger.info("Coleta de dados finalizada em %.2fs", elapsed)

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


freela = "https://www.99freelas.com.br/projects?categoria=web-mobile-e-software&sub-categorias=banco-de-dados+desenvolvimento-desktop+desenvolvimento-web&niveis-experiencia=intermediario%2Ciniciante"

scrapper_99_freela(
    link=freela,
    json_path="app/data/projects.json",
    max_pages=DEFAULT_INITIAL_MAX_PAGES,
).scrap_page_get_links().scrap_page_get_data().save_json()
