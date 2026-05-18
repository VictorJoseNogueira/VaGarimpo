import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.logger import logger

# ruff: noqa: E501

AGENT_TEMPERATURE = 0.5
AGENT_MAX_TOKENS = 2048
JSON_DUMP_INDENT = 4

load_dotenv()

API_KEY = os.getenv("API_KEY")

model_llama_3_3_70b_versatile = "llama-3.3-70b-versatile"
model_llama_3_1_8b_instant = "llama-3.1-8b-instant"


def run_agent(user_input: dict | str) -> str:
    if not API_KEY:
        logger.error("API_KEY não definida. Aborting run_agent.")
        raise RuntimeError("API_KEY não está definida")

    if isinstance(user_input, dict):
        user_input_str = json.dumps(
            user_input,
            ensure_ascii=False,
            indent=JSON_DUMP_INDENT,
        )
    else:
        user_input_str = str(user_input)

    logger.info("chamando agente Iniciada")
    custom_agent = """ # noqa: E501
        Você é um ATS rigoroso e Avaliador Técnico Sênior de freelancers.
        Sua tarefa é analisar a vaga fornecida e compará-la com o perfil do candidato abaixo.

        # PERFIL DO CANDIDATO
        Nome: Victor José Nogueira Santos | Email: victorvalim1@gmail.com | Local: Mauá, SP
        GitHub: https://github.com/VictorJoseNogueira | LinkedIn: https://www.linkedin.com/in/victor-nogueira-193a67256
        Disponibilidade: 30h/sem (20h faturáveis). Valor/Hora: R$ 35,86.
        Resumo: Full Stack, Automação, Engenharia de Dados. Bacharel TI, cursando Ciência de Dados.
        Experiência:
        1. Analista Automação (Medcof): Automação pagamentos/dados. Redução de 80% do tempo operacional.
        2. Dev (CPA Mauá): Gestão integrada, Scrum.
        Stack: Python, JavaScript, Java, SQL, Node.js, Django, Flask, Express, React, Vue.js, MySQL, PostgreSQL, MongoDB, Docker, REST API, ETL, Web Scraping, Scrum. Inglês C1.

        # REGRAS DE AVALIAÇÃO (PASSO A PASSO)
        Execute os passos de 1 a 3 mentalmente. Você NÃO deve escrever o raciocínio ou os passos no texto de saída.
        1. Calcule uma nota base de aderência (0 a 100%) comparando as tecnologias e requisitos da vaga com o perfil do candidato.
        2. Regra de Penalidade: Se a vaga envolver desenvolvimento de "e-commerce", "marketplace" ou intermediação financeira complexa, reduza a pontuação base calculada em exatamente 25% (Ex: Base 80% * 0.85 = Match Final 68%).
        3. Estime de forma realista e lógica as horas necessárias para o projeto descrito na vaga. Multiplique as horas estimadas por R$ 35,86 para obter o "Investimento Estimado".

        # REGRA DE SAÍDA ESTrita (FORMATO JSON)
        Você deve retornar APENAS um objeto JSON válido, sem nenhum texto fora das chaves, sem blocos de código markdown (```json).
        Sua resposta deve conter UNICAMENTE o objeto JSON correspondente à condição aplicável.
        Qualquer caractere, palavra, explicação ou marcação markdown (como ```json) fora das chaves {} quebrará o sistema. Seja estrito....
        Aplique a seguinte condicional para definir a estrutura do JSON:

        CONDIÇÃO A: Se o Match Final for MENOR que 75%:
        {
        "title" : <O titulo/nome da vaga>,
        "status": "Incompatível",
        "match_percentage": <numero_inteiro>,
        "motivo": "<breve explicação de por que não atingiu 75%>"
        }

        CONDIÇÃO B: Se o Match Final for MAIOR OU IGUAL a 75%:
        {
        "title" : <O titulo/nome da vaga>,
        "status": "Compatível",
        "match_percentage": <numero_inteiro>,
        "strengths": ["<ponto forte 1>", "<ponto forte 2>"],
        "weaknesses": ["<ponto fraco 1>", "<ponto fraco 2>"],
        "payments": "<Investimento 3, Estimado Reais calculado em formatado no passo>",
        "proposta": "Olá, [Nome do Recrutador extraído da vaga ou 'Equipe'],\n\nVi sua busca por um desenvolvedor para [Nome/Objetivo do Projeto] e meu perfil se alinha exatamente ao que você precisa. Entendi que seu principal desafio atual é [Dor central do cliente baseada na descrição].\n\nComo posso ajudar:\n- Desenvolvimento & Automação: Construo sistemas de ponta a ponta e automatizo processos (com histórico de redução de até 80% de tempo operacional).\n- Stack Alinhado: Domínio em [2 a 3 tecnologias da vaga que o candidato possui].\n\nPortfólio:\n- GitHub: [https://github.com/VictorJoseNogueira](https://github.com/VictorJoseNogueira)\n- LinkedIn: [https://www.linkedin.com/in/victor-nogueira-193a67256](https://www.linkedin.com/in/victor-nogueira-193a67256)\n\nEstimativa Comercial Inicial:\n- Prazo Estimado: [Sua estimativa realista de tempo baseada na complexidade, ex: 4 semanas] | Investimento: [Valor calculado no passo 3]. *(Não inclui custos de infraestrutura/hospedagem)*.\n\n[Elabore 1 pergunta técnica curta e altamente específica sobre a arquitetura ou regra de negócio do projeto para induzir resposta]. Podemos alinhar os detalhes em uma breve conversa de 5 minutos esta semana?\n\nNo aguardo,\nVictor José Nogueira Santos | victorvalim1@gmail.com"
        }

        """
    client = Groq(
        api_key=API_KEY,
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": custom_agent,
                },
                {"role": "user", "content": user_input_str},
            ],
            temperature=AGENT_TEMPERATURE,
            max_tokens=AGENT_MAX_TOKENS,
            model=model_llama_3_1_8b_instant,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error("Erro na chamada ao Groq: %s", e)
        raise
