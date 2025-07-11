FROM openjdk:21

WORKDIR /opt/app

ADD launchers/standalone/target/launchers-standalone-0.9.10-bin.tar.gz .
WORKDIR /opt/app/launchers-standalone-0.9.10/
COPY start.sh ./

EXPOSE 9080

RUN chmod +x ./start.sh
CMD ["./start.sh"]
