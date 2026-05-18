# Usando a imagem oficial do Playwright com Python 3.11 pré-instalado
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

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

# Cria o diretório de dados caso não exista
RUN mkdir -p app/data

# Define o comando de execução padrão (pode ser sobrescrito ao rodar)
CMD ["python", "main.py", "--mode", "all"]