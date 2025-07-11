# 源码部署

http://192.168.6.126/network-quality-framework/mutil-agent/chatdata/chatdata-be.git

[Jenkins-chatdata-be1](http://192.168.16.5:30002/view/mutil-agent/job/chatdata-be1/)

[Jenkins-chatdata-fe](http://192.168.16.5:30002/view/mutil-agent/job/chatdata-fe/)

[Rancher-chatdata-be](https://192.168.108.80/p/c-jjmf5:p-p8cgd/workload/deployment:mutil-agent:chatdata-be)

[Rancher-chatdata-fe](https://192.168.108.80/p/c-jjmf5:p-p8cgd/workload/deployment:mutil-agent:chatdata-fe)



## pandas-ai

### 一、pandas-ai依赖下载

```shell
### 创建pandas-ai虚拟环境，下载依赖包
## /home/young/chatdata-be/pandas-ai 这里代码目录替换为实际pandas-ai目录
sudo docker run -itd -v /home/young/chatdata-be/pandas-ai:/opt/app/ --name pandas-ai python:3.11-slim
sudo docker exec -it pandas-ai /bin/bash

python -m venv /opt/app/.venv
source /opt/app/.venv/bin/activate
pip install --no-cache-dir -r /opt/app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
exit
## sudo docker stop pandas-ai && sudo docker rm pandas-ai

### 复制依赖包到挂载卷目录
sudo mv chatdata-be/pandas-ai/.venv/lib/python3.11/site-packages deploy/prod/
```



### 二、pandas-ai代码部署

```shell
### 复制pandas-ai代码进入挂载卷目录
cp -r chatdata-be/pandas-ai deploy/prod/
```



### 三、修改配置

```shell
## 环境变量文件
## vi deploy/prod/pandas-ai/.env.deploy.sh
## 修改数据库连接配置为超音速服务的数据库连接配置
```



## supersonic

### 一、supersonic部署

```shell
### 本地打包后上传到挂载目录并解压到挂载卷
## 第一次部署需要将launchers-standalone-0.9.10-bin.tar.gz整个上传
## 后续部署如果只有超音速的代码有变化，没有新增外部依赖，则可以在本地解压jar包，将超音速的代码包上传更新即可
tar -zxvf supersonic/launchers/standalone/target/launchers-standalone-0.9.10-bin.tar.gz -C deploy/prod/
## 重命名目录为supersonic
mv deploy/prod/launchers-standalone-0.9.10 deploy/prod/supersonic
```



### 二、修改配置

```shell
## 环境变量文件
## vi deploy/prod/supersonic/bin/supersonic-env.sh

## 超音速服务的数据库连接配置
export S2_DB_TYPE=mysql
export S2_DB_HOST=192.168.16.100
export S2_DB_PORT=3306
export S2_DB_USER=root
export S2_DB_PASSWORD=root
export S2_DB_DATABASE=mutil_agent_supersonic

## 启动时是否同步模型信息到pandas-ai、同步数据库信息到trino
export SYNC_DATA_WHEN_START_UP=false

## trino服务连接信息
export TRINO_HOST=127.0.0.1
export TRINO_PORT=18080
export TRINO_USER=demo
export TRINO_PASSWORD=

## pandas-ai服务连接信息
export PANDAS_AI_HOST=127.0.0.1
export PANDAS_AI_PORT=8081
```



## supersonic-fe

源码位于 `supersonic\webapp\packages\supersonic-fe`

本地使用 `supersonic\webapp\start-fe-prod.bat` 或 `supersonic\webapp\start-fe-prod.sh`打包，

打包完成后 `supersonic\webapp`目录下会有一个前端包 `supersonic-webapp.tar.gz`

开发环境部署目录位于`supersonic\webapp\deploy\dev`，更新开发环境前端需要将打好的包放在当前目录后在jenkins更新

注意运行前端、打包之后将运行过程文件删除



## trino-server

### 一、trino-server部署

```shell
### 解压trino的程序包包进入挂载卷目录
## 下载：https://repo1.maven.org/maven2/io/trino/trino-server/474/trino-server-474.tar.gz
## trino的程序包目录替换为实际jar目录
tar -zxvf trino-server-474.tar.gz -C deploy/prod/
mv deploy/prod/trino-server-474 deploy/prod/trino-server
```



### 二、配置

```shell
## 复制配置文件
cp -r chatdata-be/trino-server/etc deploy/prod/trino-server/

## 修改node.properties
vi deploy/prod/trino-server/etc/node.properties
## 修改为以下内容
## node.data-dir=/opt/app/trino-server/data

## 其它配置文件及配置项暂时不需要修改
```



## 构建启动

```shell
## 启动脚本添加执行权限
sudo chmod +x deploy/prod/start.sh
## 创建日志目录
mkdir deploy/prod/log

## 构建镜像
sudo docker build --no-cache -f deploy/prod/Dockerfile -t chatdata-be:2.0 .

## 创建容器
## /home/young/chatdata-be/deploy/prod 挂在目录替换为实际部署目录
sudo docker run -itd \
	-p 18080:18080 -p 8081:8081 -p 9080:9080 \
	-v /home/young/chatdata-be/deploy/prod:/opt/app/ \
	--name chatdata-be-2.0 \
	chatdata-be:2.0

sudo docker logs chatdata-be-2.0

## 进入容器
sudo docker exec -it chatdata-be-2.0 /bin/bash
## sudo docker stop chatdata-be-2.0 && sudo docker rm chatdata-be-2.0
## sudo docker rmi chatdata-be:2.0

## 各个服务的日志
## deploy/prod/log/pandas-ai.log
## deploy/prod/log/trino-server.log
## deploy/prod/log/supersonic.log
## deploy/prod/supersonic/logs

## 前端
sudo docker build --no-cache -f deploy/prod/Dockerfile -t chatdata-fe:2.0 .
sudo docker run -itd -p 9000:9000 --name chatdata-fe-2.0 chatdata-fe:2.0
## 进入容器
sudo docker exec -it chatdata-fe-2.0 /bin/bash
## sudo docker stop chatdata-fe-2.0 && sudo docker rm chatdata-fe-2.0
## sudo docker rmi chatdata-fe:2.0
```



# 从发版库部署

http://192.168.6.126/network-quality-framework/mutil-agent/release/multi_agent_release.git



## 一、文件部署

```shell
tar -zxvf chatdata-2.0.1.tar.gz
cd chatdata-2.0.1/chatdata-be
# trino
tar -zxvf trino-server-474.tar.gz
mv trino-server-474 trino-server
tar -zxvf trino-server.tar.gz
# pandas-ai
tar -zxvf pandas-ai.tar.gz
# pandas-ai依赖包
tar -zxvf site-packages.tar.gz
# 超音速
tar -zxvf launchers-standalone-0.9.10-bin.tar.gz
# 重命名超音速目录为supersonic
mv launchers-standalone-0.9.10 deploy/prod/supersonic

# 启动脚本
# start.sh
sudo chmod +x start.sh

# 创建日志目录
mkdir log
```



## 二、配置

### trino-server

```shell
# 修改node.properties
vi trino-server/etc/node.properties
# 修改为以下内容
# node.data-dir=/opt/app/trino-server/data
```



### pandas-ai

```shell
# 修改环境变量文件
vi pandas-ai/.env.deploy.sh
# 修改数据库连接配置为超音速服务的数据库连接配置
```



### supersonic

```shell
# 环境变量文件
vi supersonic/bin/supersonic-env.sh

# 超音速服务的数据库连接配置
export S2_DB_TYPE=mysql
export S2_DB_HOST=192.168.16.100
export S2_DB_PORT=3306
export S2_DB_USER=账号
export S2_DB_PASSWORD=密码
export S2_DB_DATABASE=mutil_agent_supersonic

# 超音速启动时是否同步模型信息到pandas-ai、同步数据库信息到trino
export SYNC_DATA_WHEN_START_UP=false

# trino服务连接信息
export TRINO_HOST=127.0.0.1
export TRINO_PORT=18080
export TRINO_USER=demo
export TRINO_PASSWORD=

# pandas-ai服务连接信息
export PANDAS_AI_HOST=127.0.0.1
export PANDAS_AI_PORT=8081
```



### supersonic-fe

前端文件位于chatdata-fe目录下

修改nginx.conf代理端口为实际代理ip端口

```shell
 location /api/ {
      proxy_pass http://192.168.16.10:32513/api/;
      ....
 }
```



## 三、启动

```shell
## 问数后端
sudo docker load -i chatdata-be-2.0.tar
# 创建容器
# 挂载目录 /chatdata-2.0.1/chatdata-be/ 目录替换为实际部署目录

# 18080:trino端口
# 8081:pandas-ai端口
# 9080:超音速后端端口
sudo docker run -itd \
	-p 18080:18080 -p 8081:8081 -p 9080:9080 \
	-v /chatdata-2.0.1/chatdata-be/:/opt/app/ \
	--name chatdata-be-2.0 \
	chatdata-be:2.0
	
## 各个服务的日志
# log/pandas-ai.log
# log/trino-server.log
# log/supersonic.log
# supersonic/logs

## 问数前端
cd chatdata-fe
sudo docker build --no-cache -f Dockerfile -t chatdata-fe:2.0 .
sudo docker run -itd -p 9000:9000 --name chatdata-fe-2.0 chatdata-fe:2.0

## trino-cli 连接trino
java -jar chatdata-be/trino-server/trino-cli-474-executable.jar --server http://192.168.5.189:18080
```



# issue

```shell
## 如果trino服务启动时提示如下报错，则检查etc/jvm.config的配置内容是否正确，配置项的值是否合理
ERROR: could not exec java to determine jvm version: exit status 1
## 如果是jvm发生错误，会有jvm的日志文件输出，详细错误信息可以查看jvm的错误日志

## windows 换行符转 linux换行符
## vi script.sh
## :set ff=unix
## :wq

## 开放端口
iptables -I INPUT -p tcp --dport 18081 -j ACCEPT
## 保存规则
iptables-save > /etc/sysconfig/iptables  ## CentOS 7+
```



# 服务更新

后续trino-server、pandas-ai、supersonic代码有更新、只需要更新代码、jar包后重启容器即可

**pandas-ai**

如果依赖有更新则更新site-packages，代码有更新则更新pandas-ai



**supersonic**

如果没有新增依赖，只更新了supersonic的代码，只需要在本地打包后获取如下包更新到 supersonic/lib 下即可

更新配置，将本地配置上传到 supersonic/conf

- auth-api-0.9.10.jar
- auth-authorization-0.9.10.jar
- auth-authentication-0.9.10.jar
- chat-api-0.9.10.jar
- chat-server-0.9.10.jar
- common-0.9.10.jar
- headless-api-0.9.10.jar
- headless-chat-0.9.10.jar
- headless-core-0.9.10.jar
- headless-server-0.9.10.jar
- launchers-common-0.9.10.jar
- launchers-chat-0.9.10.jar
- launchers-headless-0.9.10.jar
- launchers-standalone-0.9.10.jar
- sync_data_common-0.9.10.jar
- sync_data_cs-0.9.10.jar
