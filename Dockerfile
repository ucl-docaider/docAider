FROM python:3.10

# Install dependencies
RUN apt-get update && apt-get install -y git graphviz

WORKDIR /docAider

COPY . /docAider

RUN pip install -r requirements.txt

CMD ["tail", "-f", "/dev/null"]