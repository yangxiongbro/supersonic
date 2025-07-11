FROM python:3.11-slim

RUN mkdir -p /opt/app/pandas-ai
WORKDIR /opt/app/pandas-ai

COPY . .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8081

RUN chmod +x ./start.sh
CMD ["./start.sh"]
