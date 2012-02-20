import hou
# we import this module for the _addMethod function. very cool.
import houpythonportion as addToHom


def getIdx(node):
    """
Get the set index. if there is no attribute _idx we asume you want
input 0. (first connector) this means that if you changed the input 
you will need to change it back to input_one ones you done with a 
other connector.
    """

    idx = 0
    # check if we have the attribute
    if hasattr(node, "_idx") and node._idx:
        idx = node._idx

    return idx


@addToHom._addMethod(hou.Node)
def __neg__(self):
    """
return the parent of the current node.

@warning: This currently will not evaluate correctly in the python shell because of the method
of evaluation in the introspect module. (around line 30 there doing a eval and it's not returning
the correct value)

@attention: You have to store the evaluated object to be able to use it. doing something like.
--myNode.name() Will produces a error where as node = --myNode; node.name() will work.
    """
    return self.parent()


@addToHom._addMethod(hou.Node)
def __getitem__(self, idx):
    """ index start at 1 to the max amount of inputs. """
    # make sure the passed index is a integer
    if isinstance(idx, int):
        self._idx = idx

    # return the same node with the new internal value
    return self


@addToHom._addMethod(hou.Node)
def __getattr__(self, name):
    """
__getattr__(self, name) -> hou.Node, hou.Parm or hou.ParmTuple

 Easily get the children or parameters of the node without calling
extra methods on the node. A useful convenience function.
Examples:
    node = hou.node('/obj')
    node.geo1 # will return hou.node('/obj/geo1')
    node.tx # will return node.parm('tx')
    """

    # Check and see if we can find a child node with that name
    childNode = self.node(name)
    # Check and see if there is a parm with that name.
    parm = self.parm(name)
    parmTuple = None
    # if there is no parm with that name we check for a parm tuple.
    if not parm:
        parmTuple = self.parmTuple(name)

    # if we find one in any of the 3 types we will return it.
    attribs = [x for x in (childNode, parm, parmTuple) if x]
    # if we have 0 or more then 1 we return with nothing.
    if len(attribs) == 0 or len(attribs) > 1:
        return
        # otherwise we return the attribute.
    return attribs[0]


@addToHom._addMethod(hou.Node)
def __setattr__(self, name, value):
    """
This implementation of setattr enables setting of parameters using the
= (equals) operator. Usually, you'd set a parm value like this:
    node.parm('tx').set(50)
With this implementation, we can do this:
    node.tx = 50

For example, it should be obvious that this won't work:
    my_tx = node.tx
    my_tx = 50
Or this:
    tx = node.parm('tx')
    tx = 50
    """
    # if where looking to set a attribute called _idx just set it on the node
    if name == '_idx':
        object.__setattr__(self, name, value)

    else:
        # try and find a attribute with the name.
        attr = self.__getattr__(name)
        # if we don't find anything just return
        if not attr: return
        # let's check and see if it's a hou.Parm or a hou.ParmTuple
        if isinstance(attr, hou.Parm) or isinstance(attr, hou.ParmTuple):
            # set the value on the parameter
            attr.set(value)


@addToHom._addMethod(hou.Node)
def __rshift__(self, otherNode):
    """
connect node's output to node2's input
node >> node2
    """
    # take the input number we want to connect to and
    # connect the node it
    otherNode.setInput(getIdx(otherNode), self)
    otherNode._idx = 0


@addToHom._addMethod(hou.Node)
def __lshift__(self, otherNode):
    """
connect node's input to node2's output 
node << node2
    """
    # take the input number we want to connect to and
    # connect the other node
    self.setInput(getIdx(self), otherNode)
    self._idx = 0


@addToHom._addMethod(hou.Node)
def __floordiv__(self, otherNode):
    """
Disconnect two nodes:
>>> node = hou.node('/obj/geo1')
>>> node2 = hou.node('/obj/geo2')
>>> node >> node2 # connect them
>>> node // node2 # disconnect them
    """
    # check object's input connections
    selectedIdx = None
    # in the case of a node not having the requested inputs. will
    # catch it and pass without a error.
    try:
        # get the input we want to disconnect from.
        conn = otherNode.inputConnectors()[getIdx(otherNode)][0]
        # if the input node from this output node is the same as the
        # connected node (confusing i know). we can take the index to 
        # do a disconnection on.
        if conn.inputNode() == self:
            selectedIdx = conn.inputIndex()

        if selectedIdx != None:
            # disconnect a index that we found.
            otherNode.setInput(selectedIdx, None)
    # incase the user tried to disconnect a input that's doesn't exists
    except IndexError:
        pass


@addToHom._addMethod(hou.Node)
def ancestor(self, n):
    """ Return n't of parent of the current node. """
    p = self.node("../" * n)
    return p

##==============================
## Functions related to ParmTuple
##==============================

@addToHom._addMethod(hou.ParmTuple)
def __neg__(self):
    """
__neg__(self)

return the node of the current ParmTuple.

@warning: This currently will not evaluate correctly in the python shell because of the method
of evaluation in the introspect module. (around line 30 there doing a eval and it's not returning
the correct value)
    """
    return self.node()


@addToHom._addMethod(hou.ParmTuple)
def __rshift__(self, otherParmTuple):
    """
right shift function for houdini parm Tuples.
allowing you to connect 2 parm tuples.

node.t >> node2.t
    """

    # this will take 2 tuples and zip them together and perform 
    # a __rshift__ between 2 parms. this allows us to link objects
    # like "t" which consistent of tx, ty, tx with a other tuple.
    map(hou.Parm.__rshift__, tuple(self), tuple(otherParmTuple))


@addToHom._addMethod(hou.ParmTuple)
def __str__(self):
    """
Returns the value of the parameter instead of the object reference.
Thus, typing `print node.t` will return the value of the `hou.ParmTuple`.
    """
    return str(self.eval())


##==============================
## Functions related to Parameters
##==============================

@addToHom._addMethod(hou.Parm)
def __neg__(self):
    """
__neg__(self)

return the node of the current parameter.

@warning: This currently will not evaluate correctly in the python shell because of the method
of evaluation in the introspect module. (around line 30 there doing a eval and it's not returning
the correct value). 
    """
    return self.node()


@addToHom._addMethod(hou.Parm)
def __rshift__(self, otherParm):
    """
Uses the `>>` operator to connect the left side's __output__ to the
right side's __input__.
Example:
    camera >> sphere

is the same as calling: `sphere.setInput('0', camera)`
    """

    connectParms(self, otherParm)


@addToHom._addMethod(hou.Parm)
def __lshift__(self, otherParm):
    """
Uses the `<<` operator to connect the left side's __input__ to the
right side's __output__.
Example:
camera << sphere

is the same as calling: `camera.setInput('0', sphere)`
    """
    connectParms(otherParm, self)


@addToHom._addMethod(hou.Parm)
def __str__(self):
    """
Returns the value of the parameter instead of the object reference.
Thus, typing `print node.tx` will return the value of the `hou.Parm`.
    """
    return str(self.eval())


def connectParms(fromParm, toParm):
    """
Creates a reference between `from_parm` to `to_parm`. This method is
used by `__lshift__` and `__rshift__` to enable quick referencing of
`hou.Parm` objects.
    """
    # from the current parm return the node instance
    cur_node = fromParm.node()
    # same for the other node
    to_node = toParm.node()
    # we need to determine the relative path between the 2
    rel_path = cur_node.relativePathTo(to_node)

    # The expression function that gets called to evaluate the reference is
    # different based on the target parameter's type:
    #
    # - `ch()` for floats, ints
    # - `chs()` for generic strings
    # - `chsop()` for node paths

    parm_template = toParm.parmTemplate()
    # if the other parm is a string type
    if parm_template.type().name() == 'String':
        # we want to check if it's a node reference.
        # if so we need to changed the node expression to using chsop
        if parm_template.stringType().name() == 'NodeReference':
            expr_func = 'chsop'
        else:
            expr_func = 'chs'
    else:
        expr_func = 'ch'
        # create the expression
    rel_reference = '%s("%s/%s")' % (expr_func, rel_path, toParm.name())
    # If the expression is for `chs()` or `chsop()`, it needs to be wrapped
    # with backticks: `` `chsop("foo")` ``
    if expr_func.startswith('chs'):
        rel_reference = '`' + rel_reference + '`'
        fromParm.deleteAllKeyframes()
        fromParm.set(rel_reference)
    else:
        # set the expression
        fromParm.setExpression(rel_reference)


## Python introspection override to allow for nicer and more fluid typing
import introspect

def getAutoCompleteList(command = '', locals = None, includeMagic = 1,
                        includeSingle = 1, includeDouble = 1):
    """
Return list of auto-completion options for command.
The list of options will be based on the locals namespace.
    """
    attributes = []
    # Get the proper chunk of code from the command.
    root = introspect.getRoot(command, terminator = '.')
    try:
        if locals is not None:
            object = eval(root, locals)
        else:
            object = eval(root)
    except:
        pass
    else:
        attributes = introspect.getAttributeNames(object, includeMagic,
                                                  includeSingle, includeDouble)

    def createlist(obj):
        return [s.name() for s in obj if s.name() not in attributes]

    if hasattr(object, "children"):
        attributes.extend(createlist(object.children()))

    if hasattr(object, "parms"):
        attributes.extend(createlist(object.parms()))

    if hasattr(object, "parmTuples"):
        attributes.extend(createlist(object.parmTuples()))

    return attributes

introspect.getAutoCompleteList = getAutoCompleteList

