# Under MIT License, see LICENSE.txt
""" Module de test de pTestBench """
from nose.tools import assert_equal, assert_raises
from ai.STP.Play.pTestBench import pTestBench, SEQUENCE_TEST_BENCH

class TestTestBench:
    """ Class test pTestBench """
    @classmethod
    def setup(cls):
        cls.pTestBench = pTestBench()

    def test_getTactics_with_no_args(self):
        assert_equal(SEQUENCE_TEST_BENCH, self.pTestBench.getTactics())

    def test_getTactics_with_index(self):
        assert_equal(SEQUENCE_TEST_BENCH[0], self.pTestBench.getTactics(0))

    def test_get_Tactics_with_invalid_index(self):
        assert_raises(IndexError, self.pTestBench.getTactics, 6)
