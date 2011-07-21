Simple Storing
==============

Simplestoring is a package for easy to use but still efficient persistent JSON
storage. You can request a Store anywhere in the a multidimensional dictionary
tree with the 'path' parameter. Regardless how many Store instances are used
all are working on the most current data model. All modification to the model
with the available methods of the Store class are instantly written to the file
the store is coupled with. When requesting a store staticly from the 'Stores'
class, you have to provide the filename to be used. You can either provide a
path directly or request the substore from the returend Store instance.

[Simple Storing](http://github.com/samuelspiza/simplestoring) is hosted on
Github.