

from ai.Algorithm.path_partitionner import PathPartitionner, CollisionBody

MIN_DISTANCE_FROM_OBSTACLE = 250


def create_pathfinder():  # FIXME: we should not create a new pathfinder object each time...

    return PathPartitionner()


def generate_path(game_state, player, ai_command):

    pathfinder = create_pathfinder()

    collision_bodies = get_pertinent_collision_objects(player, game_state, ai_command)

    start = player.pose.position
    target = ai_command.target.position

    path = pathfinder.get_path(start, target, obstacles=collision_bodies)

    return path


def get_pertinent_collision_objects(commanded_player, game_state, ai_command):

    collision_bodies = []

    our_team = [player for pid, player in game_state.our_team.onplay_players.items() if pid != commanded_player.id]
    enemy_team = [player for player in game_state.enemy_team.onplay_players.values()]

    for other in our_team + enemy_team:
        collision_bodies.append(CollisionBody(other.pose.position, avoid_radius=MIN_DISTANCE_FROM_OBSTACLE))

    if ai_command.ball_collision and game_state.is_ball_on_field:
        collision_bodies.append(CollisionBody(game_state.get_ball_position(), avoid_radius=MIN_DISTANCE_FROM_OBSTACLE))

    return collision_bodies


