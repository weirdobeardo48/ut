FROM python:3.8

RUN pip install scapy click

RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
	&& rm -rf /var/lib/apt/lists/*

COPY hide_my_mac.py /app/hide_my_mac.py

WORKDIR /app

ENTRYPOINT ["python3", "hide_my_mac.py"]
