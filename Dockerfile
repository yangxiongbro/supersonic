#FROM 192.168.6.126:8098/mutil-agent/chatdata-base:23.474.3
#
#WORKDIR /opt
#
#ADD supersonic/launchers/standalone/target/launchers-standalone-0.9.10-bin.tar.gz .
#
#COPY trino-server/etc/* /opt/trino-server/etc/
#
#COPY pandas-ai /opt/pandas-ai
#WORKDIR /opt/pandas-ai
## RUN python -m venv .myenv && bash -c "source .myenv/bin/activate" && \
##     /opt/pandas-ai/.myenv/bin/pip install --no-cache-dir -r /opt/pandas-ai/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
##     rm -rf /tmp/*
#RUN pip install --no-cache-dir --break-system-packages -r /opt/pandas-ai/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
#    rm -rf /tmp/*
#
#EXPOSE 8081 18080 9080
#
#COPY start.sh /opt/
#RUN chmod +x /opt/start.sh
#CMD ["/opt/start.sh"]

# 从Trino镜像提取必要文件
FROM trinodb/trino:474 AS trino-builder
USER root

RUN mkdir -p /staging && \
    cp -r /usr/lib/trino /staging/trino && \
    cp -r /etc/trino /staging/config && \
    cp -r /usr/lib/jvm /staging/jvm

# 构建最终镜像
FROM python:3.11-slim
WORKDIR /opt

# 复制Java和Trino环境
COPY --from=trino-builder /staging/trino /opt/trino
COPY --from=trino-builder /staging/config /etc/trino
COPY --from=trino-builder /staging/jvm /usr/lib/jvm

# 配置环境变量
ENV JAVA_HOME=/usr/lib/jvm/temurin/jdk-24+36/
ENV PATH="${JAVA_HOME}/bin:${PATH}"
ENV TRINO_HOME=/opt/trino
ENV PATH="${TRINO_HOME}/bin:${PATH}"

# trino
RUN mkdir -p /opt/data/trino && mkdir $TRINO_HOME/etc
ADD trino-server/etc/* $TRINO_HOME/etc/
COPY trino-server/trino-cli-474-executable.jar $TRINO_HOME
RUN chmod +x $TRINO_HOME/trino-cli-474-executable.jar
EXPOSE 18080

# supersonic
ADD supersonic/launchers/standalone/target/launchers-standalone-0.9.10-bin.tar.gz .
EXPOSE 9080

# pandas-ai
COPY pandas-ai /opt/pandas-ai/
RUN pip install --no-cache-dir -r /opt/pandas-ai/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    rm -rf /tmp/*
EXPOSE 8081

# CMD ["tail", "-f", "/dev/null"]

COPY start.sh /opt/
RUN chmod +x /opt/start.sh
# CMD ["tail", "-f", "/dev/null"]
CMD ["bash", "/opt/start.sh"]