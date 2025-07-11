FROM debian:stable-slim

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Shanghai

WORKDIR /opt

# 安装基础工具和依赖
RUN apt-get update && apt-get install -y \
    bash \
#    curl \
#    wget \
    tar \
    gzip \
    python3.11 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 安装 Java 23
ADD jdk-23.0.2_linux-x64_bin.tar.gz /opt/
RUN ln -s /opt/jdk-23.0.2 /opt/java

#RUN wget https://download.oracle.com/java/23/archive/jdk-23.0.2_linux-x64_bin.tar.gz && \
#    mkdir /opt/jdk-23.0.2 && \
#    tar -xzf jdk-23.0.2_linux-x64_bin.tar.gz -C /opt/jdk-23.0.2 --strip-components=1 && \
#    ln -s /opt/jdk-23.0.2 /opt/java && \
#    rm jdk-23*.tar.gz

# 安装 Python 依赖
#RUN pip3 install --no-cache-dir \
#    pandas \
#    requests
RUN ln -sf python3 /usr/bin/python

# 安装Trino
ADD trino-server-474.tar.gz /opt/
RUN mv /opt/trino-server-474 /opt/trino-server && \
    mkdir -p /opt/trino-server/data /opt/trino-server/etc
COPY trino-server-etc/* /opt/trino-server/etc/

#ENV TRINO_VERSION=474
#RUN mkdir -p /opt/trino && \
#    curl -SL https://repo1.maven.org/maven2/io/trino/trino-server/${TRINO_VERSION}/trino-server-${TRINO_VERSION}.tar.gz | \
#    tar -xzC /opt/trino --strip-components=1 && \
#    mkdir -p /opt/trino/data /opt/trino/etc \

# 配置环境变量
ENV JAVA_HOME=/opt/java
ENV TRINO_HOME=/opt/trino-server
ENV PATH=$JAVA_HOME/bin:$TRINO_HOME/bin:$PATH

# 验证安装
RUN $JAVA_HOME/bin/java -version && \
    python --version
#    trino --version

# 暴露端口
# EXPOSE 18080

# 默认启动Trino
# CMD ["trino", "run"]
# CMD ["trino", "--config", "/opt/trino/etc/config.properties"]
