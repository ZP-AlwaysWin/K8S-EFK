# K8S-Fluent
## Kubernetes集群中安装日志中心的收集插件Fluent
##配置文件的标准格式：
{
    "fluent_node":["127.0.0.1","127.0.0.2"]
}

##使用说明：
1. 安装的时候填写Kubernetes集群的想要收集日志的node IP在配置文件fluent.json中
执行 Install-fluent.py脚本中的install_fluent()函数

2. 安装结束后检测集群的健康状态
执行 Install-fluent.py脚本中的check_fluent_health()函数

3. 安装结束后扩充集群的节点数：
修改fluent.json文件中的ip,把想要收集日志的node ip填写进去
执行 Install-fluent.py脚本中的expand_fluent()函数

4. 卸载fluent集群：
执行 Install-fluent.py脚本中的delete_fluent_cluster()函数