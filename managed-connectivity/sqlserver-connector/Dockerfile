FROM mcr.microsoft.com/mssql/server:2019-latest

ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=yourStrong(!)Password
ENV MSSQL_PID=Developer

RUN apt-get update && apt-get install -y curl gnupg
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && apt-get install -y msodbcsql18
RUN apt-get update && apt-get install -y unixodbc-dev

RUN apt-get update && apt-get install -y wget procps tini
RUN apt-get install -y python3 python3-pip

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -g 1099 spark
RUN useradd -u 1099 -g 1099 -d /home/spark -m spark
USER spark

# Expose SQL Server port
EXPOSE 1433

