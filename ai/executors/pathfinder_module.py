

from ai.Algorithm.path_partitionner import PathPartitionner, CollisionBody

MIN_DISTANCE_FROM_OBSTACLE = 250


def create_pathfinder():

    return PathPartitionner()


def generate_path(game_state, player, ai_command):

    pathfinder = create_pathfinder()

    collision_bodies = get_pertinent_collision_objects(player, game_state, ai_command)

    player_collision_object = CollisionBody(position=player.pose.position,
                                            velocity=player.velocity.position)

    target = CollisionBody(position=ai_command.target.position)

    path = pathfinder.get_path(player_collision_object,
                               target,
                               end_speed=ai_command.end_speed,
                               collidable_objects=collision_bodies)

    return path


def get_pertinent_collision_objects(commanded_player, game_state, ai_command):
    factor = 1.1
    collision_bodies = []
    gap_proxy = MIN_DISTANCE_FROM_OBSTACLE

    our_team = [player for pid, player in game_state.our_team.onplay_players.items() if pid != commanded_player.id]
    enemy_team = [player for player in game_state.enemy_team.onplay_players.values()]

    for other in our_team + enemy_team:
        dist_commanded_to_other = (commanded_player.pose.position - other.pose.position).norm
        dist_target_to_other = (ai_command.target.position - other.pose.position).norm
        dist_commanded_to_target = (ai_command.target.position - commanded_player.pose.position).norm
        if dist_commanded_to_other + dist_target_to_other < dist_commanded_to_target * factor:
            collision_bodies.append(CollisionBody(other.pose.position, other.velocity.position, gap_proxy))

    if ai_command.ball_collision and game_state.ball_on_field:
        ball_collision_body = CollisionBody(game_state.get_ball_position(), game_state.get_ball_velocity(), gap_proxy)
        collision_bodies.append(ball_collision_body)

    return collision_bodies


