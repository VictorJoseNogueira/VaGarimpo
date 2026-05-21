# Usando a imagem oficial do Playwright com Python 3.11 pré-instalado
FROM mcr.microsoft.com/playwright/python:v1.60.0-noble

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Caso seu requirements.txt não instale os browsers do playwright, 
# este comando garante que eles (e as dependências de sistema) existam
RUN playwright install chromium

# Copia o restante do código do projeto para o container
COPY . .

# Cria o diretório que será usado para armazenar `projects.json` dentro do container
# (o código agora vive em `src/` no workspace montado em `/app`).
RUN mkdir -p /app/src/data

# Define o comando de execução padrão (pode ser sobrescrito ao rodar)
CMD ["python", "main.py", "--mode", "all"]