class Game():
    def __init__(self, field, referee, blue_team, yellow_team, blue_team_strategy, yellow_team_strategy):
        self.field = field
        self.referee = referee
        self.blue_team = blue_team
        self.yellow_team = yellow_team
        self.blue_team_strategy = blue_team_strategy
        self.yellow_team_strategy = yellow_team_strategy

    def update_strategies(self):
        self.blue_team_strategy.update()
        self.yellow_team_strategy.update()

    def get_commands(self):
        blue_team_commands = self._get_blue_team_commands()
        yellow_team_commands = self._get_yellow_team_commands()

        commands = blue_team_commands + yellow_team_commands

        self.blue_team_strategy.commands.clear()
        self.yellow_team_strategy.commands.clear()

        return commands

    def _get_blue_team_commands(self):
        blue_team_commands = self.blue_team_strategy.commands
        blue_team_commands = self._remove_commands_from_opponent_team(blue_team_commands, self.yellow_team)
        return blue_team_commands

    def _get_yellow_team_commands(self):
        yellow_team_commands = self.yellow_team_strategy.commands
        yellow_team_commands = self._remove_commands_from_opponent_team(yellow_team_commands, self.blue_team)
        return yellow_team_commands

    @staticmethod
    def _remove_commands_from_opponent_team(commands, opponent_team):
        final_commands = []
        for i in range(len(commands)):
            command = commands[i]
            if not opponent_team.has_player(command.player):
                final_commands.append(command)
        return final_commands