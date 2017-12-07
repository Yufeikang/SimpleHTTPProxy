# python proxy https代理

# run

## python2

```python SSLBumpProxy.py```

## docker

```docker build -t pyproxy github.com/Yufeikang/httpsHack```

run:
``` docker run --name pyproxy -p 8080:8080 -v $PWD/config/:/config --rm  pyproxy```

## set http proxy 
## install ca crt
 Enter http://proxy.test/ install ca crt 
# config

edit config.json
```{"hackUrl": {"https://m.baidu.com/": "/config/data.txt"}}```
