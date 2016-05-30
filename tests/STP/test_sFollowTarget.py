# Under MIT License, see LICENSE.txt
""" Module de test pour Action GoToTarget """
from nose.tools import assert_equal

from UltimateStrat.STP.Skill.sFollowTarget import sFollowTarget
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose

__author__ = 'RoboCupULaval'

def test_act():
    """ Test de base """

    player = Pose(Position(0,0), 0)
    target = Position(500, -300)
    angle = get_angle(player.position, target)
    expect = Pose(target, angle)

    action = sFollowTarget()
    result = action.act(player, target, None)

    assert_equal(result.position, expect.position)

    # comparaison foireuse de float
    delta = result.orientation - expect.orientation
    assert delta < 0.001
