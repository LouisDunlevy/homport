import unittest
import homport

class NodeWrapTestCase(unittest.TestCase):

    def setUp(self):
        hou.hipFile.clear(suppress_save_prompt = True)

    def testGetNode(self):
        hou.node('/obj').createNode('geo')
        self.assertEquals(hou.node('/obj/geo1'), hou.node('/obj').geo1)

    def testGetParent(self):
        node = hou.node('/obj').createNode('geo')
        self.assertEquals(hou.node('/obj'), -node)

    def testGetParm(self):
        null = hou.node('/obj').createNode('null')
        self.assertEquals(null.tx, null.parm('tx'))

    def testRshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null
        self.assertEquals(null.inputs()[0].name(), geo.name())

    def testLshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo << null
        self.assertEquals(geo.inputs()[0].name(), null.name())

    def testFloorDiv(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null
        self.assertTrue(len(null.inputConnections()) == 1)
        geo // null
        self.assertTrue(len(null.inputConnections()) == 0)

    def testDefinedInputConn(self):
        geo = hou.node('/obj').createNode('geo')
        subnet = hou.node('/obj').createNode('subnet')
        geo >> subnet[1]
        self.assertTrue(subnet.inputConnectors()[1])

class TestParmTupleWrap(object):

    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testGetParent(self):
        self.assertEquals(-self.geo1.t, self.geo1)

    def testSetParm(self):
        self.geo1.t = (500, 0, 0)
        self.assertEquals(self.geo1.t.eval(), (500.0, 0.0, 0.0))

    def testEvalParm(self):
        self.geo1.t.set((500, 0, 0))
        self.assertEquals(self.geo1.t.eval(), (500.0, 0.0, 0.0))

    def testStrParm(self):
        self.geo1.t.set((500, 0, 0))
        self.assertEquals(str(self.geo1.t), str((500.0, 0.0, 0.0)))

    def testLinkParms(self):
        self.geo1.t >> self.geo2.t
        self.geo1.t = (500, 0, 0)
        self.assertEquals(str(self.geo1.t), str(self.geo2.t))


class TestParmWrap(object):

    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testGetParent(self):
        self.assertEquals(-self.geo1.tx, self.geo1)

    def testSetParm(self):
        self.geo1.tx = 500
        self.assertEquals(self.geo1.tx.eval(), 500)

    def testEvalParm(self):
        self.geo1.tx.set(500.0)
        self.assertEquals(self.geo1.tx.eval(), 500.0)

    def testStrParm(self):
        self.geo1.tx.set(500.0)
        self.assertEquals(str(self.geo1.tx), str(500.0))

    def testLinkParms(self):
        self.geo1.tx >> self.geo2.tx
        self.geo1.tx = 450.0
        self.assertEquals(str(self.geo1.tx), str(self.geo2.tx))



if __name__ == "__main__":
    unittest.main()
