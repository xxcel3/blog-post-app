# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.2
FROM nginx

ENV HOME /root
WORKDIR /root

COPY . .
RUN pip3 install -r requirements.txt
RUN pip3 install pymongo
RUN pip3 install Flask --user

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u app.py
