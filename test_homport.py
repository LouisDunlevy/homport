import unittest
import homport
homport.bootstrap()

class NodeWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue('hou' in globals())

    def testWrapped(self):
        self.assertTrue(isinstance(hou.node('/obj'), homport.NodeWrap))

    def testGetNode(self):
        hou.node('/obj').createNode('geo')
        self.assertEquals(hou.node('/obj/geo1').node, hou.node('/obj').geo1.node)

    def testGetParm(self):
        null = hou.node('/obj').createNode('null')
        self.assertEquals(null.tx.parm, null.parm('tx'))

    def testRshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null

    def testLshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo << null

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
        geo >> subnet.input_two
        self.assert_(subnet.inputConnectors()[1])


class TestParmTupleWrap(object):

    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testGetParent(self):
        assert_equal(-self.geo1.t, self.geo1)

    def testSetParm(self):
        self.geo1.t = (500, 0, 0)
        assert_equal(self.geo1.t.eval(), (500.0, 0.0, 0.0))

    def testEvalParm(self):
        self.geo1.t.set((500, 0, 0))
        assert_equal(self.geo1.t.eval(), (500.0, 0.0, 0.0))

    def testStrParm(self):
        self.geo1.t.set((500, 0, 0))
        assert_equal(str(self.geo1.t), str((500.0, 0.0, 0.0)))

    def testLinkParms(self):
        self.geo1.t >> self.geo2.t
        self.geo1.t = (500, 0, 0)
        assert_equal(str(self.geo1.t), str(self.geo2.t))


class TestParmWrap(object):

    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testGetParent(self):
        assert_equal(-self.geo1.tx, self.geo1)

    def testSetParm(self):
        self.geo1.tx = 500
        assert_equal(self.geo1.tx.eval(), 500)

    def testEvalParm(self):
        self.geo1.tx.set(500.0)
        assert_equal(self.geo1.tx.eval(), 500.0)

    def testStrParm(self):
        self.geo1.tx.set(500.0)
        assert_equal(str(self.geo1.tx), str(500.0))

    def testLinkParms(self):
        self.geo1.tx >> self.geo2.tx
        self.geo1.tx = 450.0
        assert_equal(str(self.geo1.tx), str(self.geo2.tx))



if __name__ == "__main__":
    unittest.main()
