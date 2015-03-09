class Team():
    def __init__(self, players):
        self.players = players

    def has_player(self, player):
        has_player = False

        for team_player in self.players:
            if team_player == player:
                has_player = True

        return has_player