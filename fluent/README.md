# K8S-Fluent
## `Kubernetes`集群中安装日志中心的收集插件`Fluent`
## 配置文件的标准格式：

```
{
"fluent_node":["127.0.0.1","127.0.0.2"]
}
```

## 使用说明：

1. 安装的时候填写`Kubernetes`集群的想要收集日志的`node IP`在配置文件`fluent.json`中
执行 `Install-fluent.py`脚本中的`install_fluent()`函数

2. 安装结束后检测集群的健康状态
执行 `Install-fluent.py`脚本中的`check_fluent_health()`函数

3. 安装结束后扩充集群的节点数：
修改`fluent.json`文件中的`ip`,把想要收集日志的`node ip`填写进去
执行 `Install-fluent.py`脚本中的`expand_fluent()`函数

4. 卸载`fluent`集群：
执行 `Install-fluent.py`脚本中的`delete_fluent_cluster()`函数
