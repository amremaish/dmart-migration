FROM registry.fedoraproject.org/fedora:latest

COPY . /app
RUN dnf update -y
RUN dnf install libaio libnsl python-pip gcc python3-devel -y
RUN dnf install https://download.oracle.com/otn_software/linux/instantclient/218000/oracle-instantclient-basic-21.8.0.0.0-1.el8.x86_64.rpm -y
RUN dnf clean all 
RUN pip install -r /app/requirements.txt 

WORKDIR /app/src

ENTRYPOINT [ "/usr/bin/python3.11", "main.py" ]