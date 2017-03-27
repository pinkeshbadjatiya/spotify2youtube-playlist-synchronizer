#!/usr/bin/python
import json

settings = None

class dotdict(dict):
    """ dot.notation access to dictionary attributes
        Does only for 1 level.
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def Recursive_dotdict(dic):
    """ As the name suggests :P 
    """
    dic = dotdict(dic)
    for k, v in dic.items():
        if type(dic[k]) == type({}):    # if child is a dict
            dic[k] = Recursive_dotdict(dic[k])
    return dic

#class DottableDict(dict):
#    def __init__(self, *args, **kwargs):
#        dict.__init__(self, *args, **kwargs)
#        self.__dict__ = self
#    def allowDotting(self, state=True):
#        if state:
#            self.__dict__ = self
#        else:
#            self.__dict__ = dict()

def load_config():
    global settings
    with open('./configs/config.json') as json_data_file:
        data = json.load(json_data_file)
        settings = Recursive_dotdict(data)
        #settings = dotdict(data)
	#settings = DottableDict(data)

