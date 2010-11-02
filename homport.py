"""
Homport is a helper module to make manipulating nodes with HOM easier in
an interactive Python session

Connect nodes quickly:
node >> node2 -- connects output of 'node' to first input of 'node2'
node >> node2.input_two -- connects output of 'node' to the second input of
                           'node2'

Deal with parameters more easily:
print node.tx does the same as:
print node.parm('tx').eval()

Installation Instructions:
    You will be able to use pip to install it (when I get around to it):
    pip install git://github.com/schworer/homport homport/

    If you don't want to use pip, clone the repo and add it to your path
    manually:
    git clone git://github.com/schworer/homport homport/

    Then, put this in your 123.py or 456.py Houdini startup script:
        import homport
        homport.on()
    or, import it directly in the Python pane within Houdini.
"""

if not 'hou' in globals():
    # import houdini in this module. Ideally, hou should already be in
    # globals, as homport is meant to be run inside a houdini session.
    import hou

def on():
    """
    initialize the current session node wrapper.
    @warning: This monkey patches the hou.node method.
    """

    # move the original function out of the way, we'll call it later
    if not hasattr(hou, "__node"):
        
        hou.__node = hou.node
    
        def _wrap_node(*args, **kwargs):
            """
            This function is used to monkey patch the hou.node method in order to
            make the session module transparent to users. Once monkey patched,
            hou.node will return a NodeWrap object.
            """
            node = hou.__node(*args, **kwargs)
            return NodeWrap(node)
    
        _wrap_node.func_name = 'node'
        _wrap_node.func_doc = hou.node.func_doc
        hou.node = _wrap_node                
            

def off():
    """
    uninitialized the current session node wrapper.
    @warning: remove the monkey patch
    """

    try:
        
        hou.node = hou.__node
        del hou.__node
        
    except AttributeError:
        
        pass



class NodeWrapError(Exception):
    
    pass

    

class NodeWrap(object):
    """
        Wrapper of the hou.Node Object. this will be avaliable on any node after the application of the
        bootstrap function. this will add additional features to the hou.Node object for simpler interaction.
        
    """
    def __init__(self, node):
        """
            stores the node into the wrapper function.
            
            @type node: hou.Node 
            @param node: the houdini node to perform the operation on.
         
            @raise NodeWrapError: if the node is not a valid houdini node.

        """
        
        if not node:
        
            raise NodeWrapError('Invalid node given.')

        self.node = node
        self._idx = 0


    def createNode(self, name):
        """
        Wraps the node created by hou.Node.createNode in a NodeWrap obj
        
            @type name: str 
            @param name: the node name we want to create.
            
            @rtype: str
            @return: returns the NodeWrap of the new node.
         
        """
        
        node = self.node.createNode(name)
        
        return NodeWrap(node)


    def __getattr__(self, name):
        """
            convenience function: allows users to return parms or subChildren
            of the current node.
            
            examples:
            
            >>> node = hou.node('/obj')
            >>> node.geo1
            <Node /obj/geo1 of type geo>
            >>> print node.geo1.tx
            0.0
        
            @type name: str 
            @param name: the node, function or parm we want to return.
        
            @rtype: hou.Parm or hou.Node
            @return: return what matches the name parm.
                
            @raise AttributeError: if we can't find anything.
                
        """

        inputs = ('input_one', 'input_two', 'input_three', 'input_four')
        
        if name in inputs:
            
            self._idx = inputs.index(name)
            
            return self

        # if the attr we're looking for is a method on the hou.Node object
        # return that first without going further.
        # This might cause problems later, we'll see.
        if name in dir(self.node):
            
            return getattr(self.node, name)

        childNode = self.node.node(name)
        
        if childNode:
            
            childNode = NodeWrap(childNode)

        parm = self.node.parm(name)
        
        parmTuple = None
        
        if parm:
            
            parm = ParmWrap(parm)
        
        # we we didn't find a parm we will look for a parmTuple. 
        # houdini will return a parmtuple even on normal parms so we 
        # need to excluded this bit if we found a normal parm initially.
        else: 
            
            parmTuple = self.node.parmTuple(name)
            
            if parmTuple:
            
                parmTuple = ParmTupleWrap(parmTuple)

        try:
            
            attribute = getattr(self.node, name)
            
        except AttributeError:
            
            attribute = None

        # if we find one in any of the 4 types we will return it.

        attribs = [x for x in (childNode, parm, parmTuple, attribute) if x]
        
        if len(attribs) == 0:
            
            msg = "Node object has no Node, parm, parmTuple or python attr called %s" \
                % name
                
            raise AttributeError(msg)

        # if we find more then one we raise a error.
        if len(attribs) > 1:
            
            attribs = [a.name() for a in attribs]
            msg = "%s is an ambiguous name, it could be one of %s" \
                % (name, attribs)

            raise AttributeError(msg)

        return attribs[0]


    def __setattr__(self, name, value):
        """
            This implementation of setattr enables setting of parameters using the
            = (equals) operator. Usually, you'd set a parm value like this:
                node.parm('tx').set(50)
            With this implementation, we can do this:
                node.tx = 50
    
            @warning: this only works when the attr in question is a ParmWrap 
            object on a NodeWrap object and not a standalone hou.Parm or 
            ParmWrap object.
    
            For example, it should be obvious that this won't work:
                my_tx = node.tx
                my_tx = 50
            Or this:
                tx = node.parm('tx')
                tx = 50
            
            @type name: str 
            @param name: the parm we want to set.

            @type value: str,int,float 
            @param value: the value we want to set the parm to.
            
        """
        
        if name in ('node', '_idx'):
            
            object.__setattr__(self, name, value)
            
        else:
            
            attr = self.__getattr__(name)
            
            if isinstance(attr, ParmWrap):
                
                attr.parm.set(value)
                
            else:
                
                object.__setattr__(self, attr, value)


    def __rshift__(self, object):
        """
            connect node's output to node2's input
            node >> node2

            @type object: NodeWrap
            @param object: NodeWrap instance of the houdini node.
     
            @raise NodeWrapError: if the we can't wrap the node type.
            
        """
        if isinstance(object, NodeWrap):
            
            node = object
            
        else:
            
            try:
                
                node = NodeWrap(object)
                
            except NodeWrapError, e:
                
                raise NodeWrapError
            
        node.setInput(node._idx, self.node)
        

    def __lshift__(self, object):
        """
            connect node's input to node2's output 
            node << node2
                    
            @type object: NodeWrap
            @param object: NodeWrap instance of the houdini node.
     
            @raise NodeWrapError: if the we can't wrap the node type.
            
        """
        if isinstance(object, NodeWrap):
            
            node = object
            
        else:
            
            try:
                
                node = NodeWrap(object)
                
            except NodeWrapError, e:
                
                raise NodeWrapError
            
        self.node.setInput(self._idx, node.node)


    def __floordiv__(self, object):
        """
            Disconnect two nodes:
            >>> node = hou.node('/obj/geo1')
            >>> node2 = hou.node('/obj/geo2')
            >>> node >> node2 # connect them
            >>> node // node2 # disconnect them
            
            @type object: NodeWrap
            @param object: NodeWrap instance of the houdini node.
     
            @raise NodeWrapError: if the we can't wrap the node type.
             
        """
        # check object's input connections
        node = object

        if len(node.inputConnections()) <= node._idx:
            
            return
        
        conn = node.inputConnections()[node._idx]
        
        if not conn.inputNode() == self.node:
            
            raise NodeWrapError('Input node is incorrect')
        
        else:
            
            node.setInput(node._idx, None)


    def __repr__(self):
        """ returns a string representation of the houdini node asset. """
        return "<Node %s of type %s>" % (self.node.path(), self.node.type().name())


    def __str__(self):
        """ calls through to the HOM Node's str function """
        return str(self.node)



class ParmTupleWrap(object):
    """
        Houdini ParmTuple wrapper class. this will add functions such as
        left and right shift on parmTuples to channel reference.
        
    """
    
    
    def __init__(self, parmTuple):
        """
            initialize the parmTuple type. we hold a reference of the parmTuple
            this parmTuple wrapper is changing.
            
        """
        self.parmTuple = parmTuple


    def __rshift__(self, object):
        """
            right shift function for houdini parm Tuples.
            allowing you to connect 2 parm tuples.
            
            node.t >> node2.t
            
        """
        
        for parmFrom , parmTo in zip(tuple(self.parmTuple), tuple(object.parmTuple)):
            
            ParmWrap(parmFrom) >> ParmWrap(parmTo) 


    def __lshift__(self, object):
        """ 
            reverse of rshift.
            node.ty << node2.tx
        """
        
        raise NotImplementedError
            

    def __getattr__(self, name):
        """
            returns the function that we want to have from the stores self.parmTuple.
            We do this do make integration with hou.Node transparent.
            
            @rtype: hou.Parm
            @return: returns the underlying hou.Parm object from houdini.
            
            @raise AttributeError: if the function doesn't exists.
        
        """

        if name in dir(self.parmTuple):
            
            return getattr(self.parmTuple, name)
        
        else:
            
            msg = 'ParmWrap object has no attribute %s' % name
            
            raise AttributeError(msg)


    def __str__(self):
        """
            returns the string representation of the parm.
 
            @rtype: str
            @return: returns the string representation of the parm.
         
        """
        
        return str(self.parmTuple.eval())
    

class ParmWrap(object):
    """
        Houdini Parm wrapper class. this will add functions such as
        left and right shift on parms to channel reference.
        
    """
    
    def __init__(self, parm):
        """
            initialize the parm type. we hold a reference of the parm
            this parm wrapper is changing.
            
        """
        self.parm = parm


    def __rshift__(self, object):
        """
            right shift function for houdini parms.
            allowing you to connect 2 parms.
            
            node.tx >> node2.ty
            
        """
        
        cur_node = self.parm.node()
        to_node = object.node()
        rel_path = cur_node.relativePathTo(to_node)
        rel_reference = ""
        
        # see if the parm is a string. add the chs to the command.
        if self.parm.parmTemplate().type().name() == "String":
            
            rel_reference += 'chs'
            
        else:

            rel_reference += 'ch'
        
        rel_reference += '("%s/%s")' % (rel_path, object.name())
        self.parm.setExpression(rel_reference)
        

    def __lshift__(self, object):
        """ node.ty << node2.tx not implemented """
        
        raise NotImplementedError


    def __getattr__(self, name):
        """
            returns the function that we want to have from the stores self.parm.
            We do this do make integration with hou.Node transparent.
            
            @rtype: hou.Parm
            @return: returns the underlying hou.Parm object from houdini.
            
            @raise AttributeError: if the function doesn't exists.
        
        """

        if name in dir(self.parm):
            
            return getattr(self.parm, name)
        
        else:
            
            msg = 'ParmWrap object has no attribute %s' % name
            
            raise AttributeError(msg)
        
            
    def __str__(self):
        """
            returns the string representation of the parm.
 
            @rtype: str
            @return: returns the string representation of the parm.
         
        """
        
        return str(self.parm.eval())

