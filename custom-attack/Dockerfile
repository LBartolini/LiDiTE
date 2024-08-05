FROM python:3-alpine
RUN mkdir -p /opt/custom-attack
RUN apk add nmap nmap-scripts wait4x bind-tools

WORKDIR /opt/custom-attack
COPY requirements.txt /opt/custom-attack
RUN pip install -r requirements.txt
COPY src/ /opt/custom-attack/src

COPY entrypoint.sh /opt/custom-attack
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "/opt/custom-attack/entrypoint.sh" ]
