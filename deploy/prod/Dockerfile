# 从java镜像提取必要文件
FROM openjdk:23 AS jdk-base

ENV JDK_PATH=/usr/java/openjdk-23

# 构建最终镜像
FROM python:3.11-slim
WORKDIR /opt

# 复制Java环境
COPY --from=jdk-base /usr/java/openjdk-23 /usr/java/openjdk-23

# 配置 JDK 环境变量
ENV JAVA_HOME=/usr/java/openjdk-23
ENV PATH="$JAVA_HOME/bin:$PATH"

# CMD ["tail", "-f", "/dev/null"]
CMD ["bash", "/opt/app/start.sh"]