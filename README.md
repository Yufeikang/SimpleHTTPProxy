# python proxy https代理

# run

## python2

```python SSLBumpProxy.py```

## docker

```docker build -t pyproxy github.com/Yufeikang/SimpleHTTPProxy```

run:
``` docker run --name pyproxy -p 8080:8080 -v $PWD/config/:/config --rm  pyproxy```

# config

edit config.json
```{"hackUrl": {"https://m.baidu.com/": "/config/data.txt"}}```
