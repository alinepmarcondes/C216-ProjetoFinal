# Usando uma imagem base do Python
FROM python:3.10-slim

# Instalando dependências
RUN pip install fastapi uvicorn asyncpg

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando o código para o container
COPY main.py .
COPY ./db ./db

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]