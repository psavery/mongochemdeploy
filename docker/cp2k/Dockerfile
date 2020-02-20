FROM ubuntu:18.04

# Install ssh, which is a runtime dep of the ubuntu cp2k package
# (due to its usage of MPI)
RUN apt-get update && \
  apt-get install -y ssh git

# Install cp2k
RUN apt-get update && \
  apt-get install -y cp2k

# Install python
RUN apt-get update && \
  apt-get install -y python3 python3-pip

# Clear the apt lists
RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY src/* /app/

ENTRYPOINT ["python3", "/app/main.py"]
