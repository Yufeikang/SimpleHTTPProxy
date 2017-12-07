#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: kang
@license: Apache Licence
@contact: kyf0722@gmail.com
@site: http://blog.kangyufei.net
@software: PyCharm
@file: config.py
@time: 4/13/17 8:20 AM
"""
import os
import json


config = None


class Conf:
    def __init__(self, init_txt=None):
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists('/config/'):
            config_file = os.path.join('/config/', "config.json")
        try:
            self.config_dict = json.load(open(config_file, 'r'))
        except:
            if init_txt:
                json.dump(init_txt, open(config_file, 'w'))
                self.config_dict = json.load(open(config_file, 'r'))
            else:
                raise Exception("没有配置文件")

    def __getattr__(self, item):
        class get_class(dict):
            def __init__(self, p_item):
                super(get_class, self).__init__(p_item)
                self.p_item = p_item

            def __getattr__(self, _item):
                if isinstance(self.p_item.get(_item, None), dict):
                    return get_class(self.p_item.get(_item, None))
                return self.p_item.get(_item, None)
        if isinstance(self.config_dict.get(item, None), dict):
            return get_class(self.config_dict.get(item, None))
        return self.config_dict.get(item, None)

    def get(self, item):
        return self.__getattr__(item)


def get_conf(init_text=None):
    global config
    if config is None:
        config = Conf(init_text)
    return config
