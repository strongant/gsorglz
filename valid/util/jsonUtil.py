# _*_ coding: UTF-8 _*_
import json


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        # convert object to a dict
        d = {}
        # d['__class__'] = obj.__class__.__name__
        # d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d


class MyDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict2object)

    def dict2object(self, d):
        # convert dict to object
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items())  # get args
            inst = class_(**args)  # create new instance
        else:
            inst = d
        return inst


def class_to_dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            # 把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict


def convert_to_builtin_type(obj):
    d = {}
    d.update(obj.__dict__)
    return d




class MyObj(object):

    def __init__(self,s):
        self.s = s

    def __repr__(self):
        return "<MyObj(%s)>" % self.s

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        print 'default(', repr(obj), ')'
        # Convert objects to a dictionary of their representation
        d = { '__class__':obj.__class__.__name__,
              '__module__':obj.__module__,
              }
        d.update(obj.__dict__)
        return d


