#!/usr/bin/env python
# file testmodel.py
import unittest
from Model import DataSet

class TestModel(unittest.TestCase):
    def test_DataSetCreate(self):
        m = DataSet("testobj",[1,2,3])
        self.assertEqual("testobj",m.name)

if __name__ == '__main__':
    unittest.main()
