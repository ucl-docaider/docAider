FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends git graphviz && rm -rf /var/lib/apt/lists/*

WORKDIR /docAider-gemini

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]