#!/usr/bin/env python3
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>
#
"""Simple Storing

Simplestoring is a package for easy to use but still efficient persistent JSON
storage. You can request a Store anywhere in the a multidimensional dictionary
tree with the 'path' parameter. Regardless how many Store instances are used
all are working on the most current data model. All modification to the model
with the available methods of the Store class are instantly written to the file
the store is coupled with. When requesting a store staticly from the 'Stores'
class, you have to provide the filename to be used. You can either provide a
path directly or request the substore from the returend Store instance.
"""

__author__ = "Samuel Spiza <sam.spiza@gmail.com>"
__version__ = "0.1.2"
__all__ = ["Stores","Store","SubStore","ListStore","ListSubStore"]

import os
import json
import codecs

class Stores:
    _stores = {}

    @staticmethod
    def getStore(fileName, path=[]):
        if fileName not in Stores._stores:
            Stores._stores[fileName] = Store(fileName=fileName)
        if 0 < len(path):
            return Stores._stores[fileName].getStore(path)
        else:
            return Stores._stores[fileName]

    @staticmethod
    def getListStore(fileName, path=[]):
        if fileName not in Stores._stores:
            if 0 < len(path):
                Stores._stores[fileName] = Store(fileName=fileName)
            else:
                Stores._stores[fileName] = ListStore(fileName=fileName)
        if 0 < len(path):
            return Stores._stores[fileName].getListStore(path)
        else:
            return Stores._stores[fileName]

class StoreSkelleton:
    def __init__(self, key):
        self._subs = {}
        self.key = key

    def getStore(self, path=[]):
        if path[0] not in self._subs:
            self._subs[path[0]] = SubStore(self, path[0])
        if 1 < len(path):
            return self._subs[path[0]].getStore(path[1:])
        else:
            return self._subs[path[0]]

    def getListStore(self, path=[]):
        if path[0] not in self._subs:
            if 1 < len(path):
                self._subs[path[0]] = SubStore(self, path[0])
            else:
                self._subs[path[0]] = ListSubStore(self, path[0])
        if 1 < len(path):
            return self._subs[path[0]].getListStore(path[1:])
        else:
            return self._subs[path[0]]

class DictStoreSkelleton:
    def __init__(self):
        self._baseStructure = {}

class ListStoreSkelleton:
    def __init__(self):
        self._baseStructure = []

class BaseStoreSkelleton:
    def __init__(self):
        if os.path.exists(self.key):
            self._read()
        else:
            self._value = self._baseStructure
            self._write()

    def get(self, key=None, path=[]):
        if key is None:
            ret = self._value
            for key in path:
                ret = ret[key]
        else:
            self.get(path=[key])
        return ret

    def set(self, key=None, value=None, path=[]):
        if key is None:
            tmp = self._value
            for key in path[:-1]:
                tmp = tmp[key]
            tmp[path[-1]] = value
            self._write()
        else:
            self.set(value=value, path=[key])

    def delete(self, key=None, path=[]):
        if key is None:
            tmp = self._value
            for key in path[:-1]:
                tmp = tmp[key]
            del tmp[path[-1]]
            self._write()
        else:
            self.delete(path=[key])

    def append(self, value, path=[]):
        tmp = self._value
        for key in path:
            tmp = tmp[key]
        tmp.append(value)
        self._write()

    def contains(self, value, path=[]):
        tmp = self._value
        for key in path:
            tmp = tmp[key]
        return value in tmp

    def _read(self):
        with codecs.open(self.key, "r", "utf-8") as fp:
            self._value = json.load(fp)

    def _write(self):
        with codecs.open(self.key, "w", "utf-8") as fp:
            json.dump(self._value, fp, sort_keys=True, indent=4)

class SubStoreSkelleton:
    def __init__(self, parent):
        self.parent = parent
        if not self.parent.contains(value=self.key):
            self.parent.set(value=self._baseStructure, path=[self.key])

    def get(self, key=None, path=[]):
        if key is None:
            return self.parent.get(path=[self.key]+path)
        else:
            return self.parent.get(path=[self.key]+[key])

    def set(self, key=None, value=None, path=[]):
        if key is None:
            return self.parent.set(value=value, path=[self.key]+path)
        else:
            return self.parent.set(value=value, path=[self.key]+[key])

    def delete(self, key=None, path=[]):
        if key is None:
            return self.parent.delete(path=[self.key]+path)
        else:
            return self.parent.delete(path=[self.key]+[key])

    def append(self, value=None, path=[]):
        return self.parent.append(value=value, path=[self.key]+path)

    def contains(self, value=None, path=[]):
        return self.parent.contains(value=value, path=[self.key]+path)

class Store(StoreSkelleton, DictStoreSkelleton, BaseStoreSkelleton):
    def __init__(self, fileName):
        StoreSkelleton.__init__(self, fileName)
        DictStoreSkelleton.__init__(self)
        BaseStoreSkelleton.__init__(self)

class SubStore(StoreSkelleton, DictStoreSkelleton, SubStoreSkelleton):
    def __init__(self, parent, key):
        StoreSkelleton.__init__(self, key)
        DictStoreSkelleton.__init__(self)
        SubStoreSkelleton.__init__(self, parent)

class ListStore(StoreSkelleton, ListStoreSkelleton, BaseStoreSkelleton):
    def __init__(self, fileName):
        StoreSkelleton.__init__(self, fileName)
        ListStoreSkelleton.__init__(self)
        BaseStoreSkelleton.__init__(self)

class ListSubStore(StoreSkelleton, ListStoreSkelleton, SubStoreSkelleton):
    def __init__(self, parent, key):
        StoreSkelleton.__init__(self, key)
        ListStoreSkelleton.__init__(self)
        SubStoreSkelleton.__init__(self, parent)
