# Under MIT License, see LICENSE.txt

import math as m
import numpy as np

from Util import Position, Pose


def get_angle_between_three_points(start: Position, mid: Position, end: Position):
    return abs(wrap_to_pi((mid - start).angle - (end - mid).angle))


def are_collinear(pos1: Position, pos2: Position, pos3: Position, abs_tol=np.pi / 30) -> bool:
    return compare_angle((pos2 - pos3).angle, (pos1 - pos2).angle, abs_tol=abs_tol)


def wrap_to_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def compare_angle(angle1, angle2, abs_tol=0.004) -> bool:
    return m.fabs(wrap_to_pi(angle1 - angle2)) < abs_tol


def compare_pose_orientation(pose1: Pose, pose2: Pose, abs_tol=0.004) -> bool:
    return m.fabs(wrap_to_pi(pose1.orientation - pose2.orientation)) < abs_tol


def rotate(vec: Position, angle) -> Position:
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]).view(Position)
    return rotation @ vec


def normalize(vec: Position) -> Position:
    if vec.norm == 0:
        raise ZeroDivisionError
    return vec.copy() / vec.norm


def perpendicular(vec: Position) -> Position:
    """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
    return normalize(Position(-vec.y, vec.x))


def are_close(vec1: Position, vec2: Position, abs_tol=0.001) -> bool:
    return (vec1 - vec2).norm < abs_tol


def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)


def remove_duplicates(seq, concurent_list=None, round_up_threshold=1):
    # TODO: Clean that. Seems to complicate for nothing. + Varible return argument

    seen = set()
    seen2 = set()
    seen_add = seen.add
    seen2_add = seen2.add
    seq_rounded = round_position_to_number(seq, round_up_threshold)
    if concurent_list is None:
        return [x for idx, x in enumerate(seq) if not seq_rounded[idx] in seen or seen_add(seq_rounded[idx])]
    else:
        return [x for idx, x in enumerate(seq) if not seq_rounded[idx] in seen or seen_add(seq_rounded[idx])], \
               [y for idx, y in enumerate(concurent_list) if not seq_rounded[idx] in seen or seen_add(seq_rounded[idx])]


def round_position_to_number(positions, base=2):

    for position in positions:
        position.x = int(base * round(float(position.x)/base))
        position.y = int(base * round(float(position.y)/base))
    return positions


def get_closest_point_on_line(reference: Position,
                              position1: Position,
                              position2: Position) -> Position:
    """
        Calcul la position du point d'une droite le plus près d'une position de
        référence. La droite est donnée par deux positions. La ligne reliant la
        position recherchée et la position de référence est perpendiculaire à
        la droite.
        Args:
            reference: La position de référence
            position1: Le premier point formant la droite
            position2: Le second point formant la droite
        Returns:
            La position du point de la droite le plus proche de la position de
            référence.
    """
    assert isinstance(reference, Position)
    assert isinstance(position1, Position)
    assert isinstance(position2, Position)

    delta_x = position2.x - position1.x
    delta_y = position2.y - position1.y

    if delta_x != 0 and delta_y != 0:   # droite quelconque
        pente = delta_y / delta_x
        ordonnee = position1.y - pente*position1.x

        pente_orthogonale = -1/pente
        ordonnee_orthogonale = reference.y - pente_orthogonale*reference.x

        # Calcul des coordonnées de la destination
        pos_x = (ordonnee_orthogonale - ordonnee)/(pente - pente_orthogonale)
        pos_y = pente*pos_x + ordonnee

    elif delta_x == 0:  # droite verticale
        pos_x = position1.x
        pos_y = reference.y

    elif delta_y == 0:  # droite horizontale
        pos_x = reference.x
        pos_y = position1.y

    return Position(pos_x, pos_y)


def get_closest_point_on_segment(reference: Position,
                                 position1: Position,
                                 position2: Position) -> Position:
    """
        Calcul la position du point sur un segment le plus près d'une position de
        référence. Le segment est donné par deux positions. La ligne reliant la
        position recherchée et la position de référence est perpendiculaire à
        la droite représentant le segment.
        Args:
            reference: La position de référence
            position1: Le premier point formant la droite
            position2: Le second point formant la droite
        Returns:
            La position du point de la droite le plus proche de la position de
            référence.
    """

    position_on_line = get_closest_point_on_line(reference, position1, position2)
    position_on_segment = position_on_line

    # This handle the case where the projection is not between the two points
    outside_x = (reference.x > position1.x and reference.x > position2.x) or \
                (reference.x < position1.x and reference.x < position2.x)
    outside_y = (reference.y > position1.y and reference.y > position2.y) or \
                (reference.y < position1.y and reference.y < position2.y)
    if outside_x or outside_y:
        if (position1 - reference).norm < (position2 - reference).norm:
            position_on_segment = position1
        else:
            position_on_segment = position2
    return position_on_segment