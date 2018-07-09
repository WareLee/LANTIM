from udpserver import myserver
import unittest


class UdpServerTest(unittest.TestCase):
    def test_slice_msg(self):
        """(b_msg, per_add, maxlen=1474):"""
        b_msg = '#' * 3000
        b_msg = b_msg.encode('utf-8')
        per_add = 'ware'.encode('utf-8')
        maxlen = 1474

        li = myserver._slice_msg(b_msg, per_add, maxlen=maxlen)

        self.assertEqual(len(li), 3)
        self.assertEqual(len(li[0]), maxlen)
        self.assertEqual(len(li[1]), maxlen)
        self.assertEqual(li[2].decode('utf-8').startswith('ware'), True)
        # for it in li:
        #     print(it)

        b_msg = 'sajfkkkkkkkkk'.encode('utf-8')
        li2 = myserver._slice_msg(b_msg, per_add, maxlen=maxlen)
        self.assertEqual(len(li2), 1)
        self.assertEqual(li[0].decode('utf-8').startswith('ware'), True)


if __name__ == '__main__':
    unittest.main()
