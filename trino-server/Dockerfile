FROM trinodb/trino:474

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Shanghai

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
#     && echo $TZ > /etc/timezone \

USER root

RUN mkdir -p /opt/trino-server/data

WORKDIR /opt/app
ADD etc/* /etc/trino/
COPY trino-cli-474-executable.jar /opt/app/
RUN chmod +x /opt/app/trino-cli-474-executable.jar

EXPOSE 18080

