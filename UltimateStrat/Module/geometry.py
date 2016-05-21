from RULEngine.Util.geometry import *
from Util.geometry import *
from RULEngine.Util.Pose import Pose

__author__ = 'RoboCupULaval'


def getDictSpeed(list_pose, debug=False):
    '''
    getDictSpeed output dictionnary and calculate speed, normal and speed vector thanks to list of pose input.
    Args:
        list_pose: list of Pose objects
        debug: Display Input and Output for debugging

    Returns: dict with 'speed': int | 'normal': tuple(int, int) with -1 <= int <= int | 'vector': tuple(int, int)

    '''
    assert isinstance(list_pose, list), 'getDictSpeed : Input should be list of Pose'
    
    if not len(list_pose) == 10:
        speed = 0
        normal = (0, 0)
        vector = (0, 0)
    else:
        # Get 10 feedback on previous position
        time_ref, pst_ref = list_pose[9]
        time_sec, pst_sec = list_pose[0]

        # Pre calculations
        angle = get_angle(pst_ref, pst_sec)
        dst_tot = get_distance(pst_ref, pst_sec)
        time_tot = get_milliseconds(time_ref) - get_milliseconds(time_sec)

        # Final calculations
        speed = dst_tot / time_tot
        normal = (m.cos(m.radians(angle)), m.sin(m.radians(angle)))
        vector = (normal[0] * speed, normal[1] * speed)

    # Display input / output for debugging
    if debug:
        print('### DEBUG getDictSpeed(list(Pose), debug=bool) ###')
        for i, pose in enumerate(list_pose):
            print('INPUT  >> {}: {}'.format(i, pose))
        print('OUTPUT >> SPEED:{0:.4f} | NORMAL:{1} | VECTOR:{2}'.format(speed, normal, vector))

    return {'speed': speed, 'normal': normal, 'vector': vector}