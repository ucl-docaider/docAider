FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y git graphviz

WORKDIR /repo-copilot

COPY . /repo-copilot

RUN pip install -r requirements.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]