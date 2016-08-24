# Under MIT License, see LICENSE.txt

from math import ceil, sqrt
import numpy

from RULEngine.Util.constant import *
from RULEngine.Util.Position import Position

from ai.Algorithm.IntelligentModule import IntelligentModule

__author__ = 'RoboCupULaval'


class InfluenceMap(IntelligentModule):
    """
    Une classe représentant une influence map d'un terrain de robosoccer. C'est une matrice de cellule représentant le
    terrain auquelle on ajoute des points avec des influences qui se propagent sur le reste du terrain.

    La matrice et le code respecte le format suivant:
        - axe X ou axe 0 est l'axe représentant les rangées / l'axe 0 de la matrice /
          la largeur (axe Y) du terrain physique
        - axe Y ou axe 1 est l'axe représentant les colonnes / l'axe 1 de la matrice /
          la longueur (axe X) du terrain physique
        - Le point d'origine (0, 0) se situe au coin supérieur gauche du terrain physique.
        - Ce qui veut dire que c'est tableaux sont row-major.

    L'algorithm de propagation de l'influence est:
    (force appliqué à la case) = (force du point d'origine de l'influence) * ((facteur de réduction) ** (distance))
    transfomé en int arrondie vers 0.
    """

    def __init__(self, info_manager, resolution=100, strength_decay=0.85, strength_peak=100, effect_radius=25,
                 have_static=False, have_it_executed=False):
        """
            Constructeur de la classe InfluenceMap

            :param info_manager:  référence vers l'InfoManager
            :param resolution:    résolution des cases (défaut = 100)
            :param strength_decay: facteur de réduction de l'influence par la distance (défaut = 0.8)
            :param strength_peak:  maximum de la force appliquable par un point (est aussi le min) (défaut = 100)
            :param effect_radius:  distance qui borne la propagation de l'influence autour de l'origine (défaut = 40)
        """
        assert isinstance(resolution, int), "Creation InfluenceMap avec param resolution autre que int"
        assert isinstance(strength_decay, float), "Creation InfluenceMap avec param strength_decay autre que int"
        assert isinstance(effect_radius, int), "Creation InfluenceMap avec param effect_radius autre que int"
        assert isinstance(strength_peak, int), "Creation InfluenceMap avec param strength_peak autre que int"
        assert isinstance(have_static, bool), "Creation InfluenceMap avec param have_static autre que bool"
        assert isinstance(have_it_executed, bool), "Creation InfluenceMap avec param have_it_executed autre que bool"
        assert 0 < resolution, "Creation InfluenceMap avec param resolution <= 0"
        assert 0 < strength_decay < 1, "Creation InfluenceMap avec param strength_decay pas dans intervalle ]0, 1["
        assert 0 < strength_peak, "Creation InfluenceMap avec param strength_decay <= à 0"
        assert 0 < effect_radius, "Creation InfluenceMap avec param effect_radius <= 0"

        super().__init__(info_manager)

        # board parameters
        self._resolution = resolution
        self._strength_decay = strength_decay
        self._strength_peak = strength_peak
        self._effect_radius = effect_radius
        self._border_strength = - strength_peak * 0.03  # TODO change this variable for something not out of thin air!

        # things on the baord parameters
        self._ball_position_on_board = ()
        self._friendly_bots_on_board = []
        self._enemy_bots_on_board = []

        self._number_of_rows, self._number_of_columns = self._calculate_rows_and_columns()

        if self.state is not None:
            self.have_it_executed = have_it_executed
            self._last_updated = self.state.timestamp

        self._adjust_effect_radius()

        # different tableau pour enregistrer les différentes représentation
        self._static_boards = None
        self._starterboard = self._create_standard_influence_board()
        self._board = self._create_standard_influence_board()

        # those board are optionnal
        self._borders_board = self._create_standard_influence_board()
        self._goals_board = self._create_standard_influence_board()

        # todo determine how to choose if you want different kinds of static boards (ex: borders, goals, to determine..)
        if have_static:
            self._create_static_board()

    def update(self):
        if self.have_it_executed:
            if self.state.timestamp - self._last_updated > 5:
                if self._static_boards is not None:
                    self._board = numpy.copy(self._static_boards)
                else:
                    self._board = self._create_standard_influence_board()

                self._update_friend_position()
                self.update_foes_position()
                self._update_ball_position()
                self.state.debug_manager.add_influence_map(self.export_board())
                self._last_updated = self.state.timestamp

    def export_board(self):
        return self._board.tolist()

    def find_points_over_strength_square(self, top_left_position, bottom_right_position, strength):
        """
        Retourne les points qui se trouve au-dessus ou égale à la force demandé dans le tableau principal(_board)

        :param Positon top_left_position: la rangé supérieure
        :param Position bottom_right_position: la rangé inférieure
        :param int strength: le force à trouvé qui est égale ou au dessus.

        :return: un liste de point qui se trouve au dessus ou égale à la force demandé
        """
        assert isinstance(top_left_position, Position), "Cette méthode requiert un object Position"
        assert isinstance(bottom_right_position, Position), "Cette méthode requiert un object Position"

        top_row, left_column = self._transform_field_to_board_position(top_left_position)
        bot_row, right_column = self._transform_field_to_board_position(bottom_right_position)
        ind_x, ind_y = numpy.where(self._board[top_row:bot_row, left_column:right_column] >= strength)
        ind_x = ind_x.tolist()
        ind_x = [x+top_row for x in ind_x]
        ind_y = ind_y.tolist()
        ind_y = [x+left_column for x in ind_y]
        indices = zip(ind_x, ind_y)
        return list(indices)

    def find_points_under_strength_square(self, top_left_position, bottom_right_position, strength):
        """
        Retourne les points qui se trouve au-dessous ou égale à la force demandé dans le tableau principal(_board)

        :param Positon top_left_position: la rangé supérieure
        :param Position bottom_right_position: la rangé inférieure
        :param int strength: le force à trouvé qui est égale ou au dessous.

        :return: un liste de point qui se trouve au-dessous ou égale à la force demandé
        :rtype: une liste de tuple rangée * colonne (int * int) list
        """
        assert isinstance(top_left_position, Position), "Cette méthode requiert un object Position"
        assert isinstance(bottom_right_position, Position), "Cette méthode requiert un object Position"

        top_row, left_column = self._transform_field_to_board_position(top_left_position)
        bot_row, right_column = self._transform_field_to_board_position(bottom_right_position)
        ind_x, ind_y = numpy.where(self._board[top_row:bot_row, left_column:right_column] <= strength)
        ind_x = ind_x.tolist()
        ind_x = [x+top_row for x in ind_x]
        ind_y = ind_y.tolist()
        ind_y = [x+left_column for x in ind_y]
        indices = zip(ind_x, ind_y)
        return list(indices)

    def find_max_value_in_board(self):
        """
        Permet de trouver les points du tableau qui ont la plus grande valeur du tableau

        :return: la valeur maximale du tableau et la liste de point (rangée * colonne) des point qui ont la valeur max
        :rtype: tuple (int * (int * int) list)
        """
        uniques = numpy.unique(self._board)
        max_in_board = uniques[-1]
        x, y = numpy.where(self._board >= max_in_board)
        x = x.tolist()
        y = y.tolist()
        indices = zip(x, y)
        return max_in_board, indices

    def find_min_value_in_board(self):
        """
        Permet de trouver les points du tableau qui ont la plus petite valeur du tableau

        :return: la valeur minimale du tableau et la liste de point (rangée * colonne) des point qui ont la valeur min
        :rtype: tuple (int * (int * int) list)
        """
        uniques = numpy.unique(self._board)
        min_in_board = uniques[0]
        x, y = numpy.where(self._board <= min_in_board)
        x = x.tolist()
        y = y.tolist()
        indices = zip(x, y)
        return min_in_board, indices

    def find_max_value_in_circle(self, center, radius):
        pass

    def get_influence_at_position(self, position):
        assert isinstance(position, Position), "accessing this function require a Position object"

        row_column_in_board = self._transform_field_to_board_position(position)
        return self._board[row_column_in_board[0], row_column_in_board[1]]

    def set_ball_position(self, row, column):
        assert isinstance(row, int), "Setting the ball's row position with this method is only posible with an int"
        assert isinstance(column, int), "Setting the ball's column position with this method is only posible with " \
                                        "an int"
        assert 0 <= row <= self._number_of_rows, "setting the ball's row position at the exterior of the board"
        assert 0 <= column <= self._number_of_columns, "setting the ball's column position at the exterior" \
                                                       " of the board"

        self._ball_position_on_board = (row, column)

    def get_ball_influence(self):
        return self._board[self._ball_position_on_board[0], self._ball_position_on_board[1]]

    def get_number_of_cells(self):
        return self._number_of_rows * self._number_of_columns

    def print_board_to_file(self):
        """
        Create a file in the same running directory with a representation of the current board.
        """

        numpy.savetxt("IMBoard", self._board, fmt='%4i')
        # todo remove this line while not in debug mode
        print(self._starterboard.shape[0], " x ", self._starterboard.shape[1])

    def str(self):
        # todo comment and make sure this is right! Embelish?
        return "Influence Map - ", str(self._number_of_rows), " x ", str(self._number_of_columns)

    def _update_friend_position(self):
        """
        Fetch la position de nos robots dans l'infomanager et les applique sur le tableau principal.
        """
        self._friendly_bots_on_board.clear()
        for i in range(self.state.get_count_player()):
            friend_position = self._transform_field_to_board_position(self.state.get_player_position(i))
            self._friendly_bots_on_board.append(friend_position)
            self._add_point_and_propagate_influence(friend_position[0], friend_position[1], self._board, 100)

    # TODO ask about implementation of foes in infomanager
    def update_foes_position(self):
        pass

    def _update_ball_position(self):
        self._ball_position_on_board = self._transform_field_to_board_position(self.state.get_ball_position())

    def _calculate_rows_and_columns(self):
        """
        Utilise la resolution pour calculer le nombre de rangée(rows) et de colonne(columns) pour le terrain

        :return: le nombre de rangées et le nombre de colonnes
        :rtype: tuple (int * int)
        """
        numberofrow = int(ceil((abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / self._resolution))
        numberofcolumn = int(ceil((abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / self._resolution))

        return numberofrow, numberofcolumn

    def _create_standard_influence_board(self):
        """
        Crée un objet numpy.ndarray, une liste à 2 dimenson de self._number_of_rows par self._number_of_columns d'int8.

        :return: Un numpy.ndarray d'int8 de self._number_of_rows par self._number_of_columns.
        :rtype: numpy.ndarray dtype=numpy.int8
        """
        return numpy.zeros((self._number_of_rows, self._number_of_columns), numpy.int8)

    def _adjust_effect_radius(self):
        """
        Permet d'ajuster le rayon d'effet de l'influence (self._effect_radius) si celui-ci éxède la propagation normale.

        Si la propagation de l'influence se retrouve à zéro avant d'avoir atteint le rayon d'effet défini à la création
        de la classe, cette méthode l'ajuste pour quelle donne exactement le rayon qui permet d'afficher tous les points
        qui ne donnent pas zéro.

        influence dans les cases:
        100 91 86 ... 6 5 4 3 2 1 0 0 0 0 0 0 0  sans effect_radius ajusté (si effect_radius est trop gros)
                v
        100 91 86 ... 6 5 4 3 2 1                avec effect_radius ajusté

        Coupe le nombre d'itérations des boucles de mise en place de l'influence lorsque le calcul donnerait une
        influence à 0.
        """
        distance_from_center = 0
        strenght_value_at_current_distance = self._strength_peak
        while strenght_value_at_current_distance >= 1:
            distance_from_center += 1
            decay = self._compute_value_by_distance(self._strength_peak, distance_from_center)
            strenght_value_at_current_distance = decay

        if self._effect_radius > distance_from_center:
            self._effect_radius = distance_from_center

    def _initialize_borders_board(self):
        """
        Ajoute des bordures sur le board dédie _borders_board
        """
        temp_array = self._create_standard_influence_board()
        self._put_and_propagate_borders(temp_array)
        numpy.add(temp_array, self._borders_board, out=self._borders_board)

    def _put_and_propagate_borders(self, board_to_apply):
        """
        Mets des bordures sur un array numpy.ndarray vierge.

        :param board_to_apply: Un numpy.ndarray un array vierge pour y ajouter des bordures.
        :type board_to_apply: numpy.ndarray dtype=numpy.int8
        """
        assert(isinstance(board_to_apply, numpy.ndarray))
        assert(board_to_apply.shape[0] == self._number_of_rows)
        assert(board_to_apply.shape[1] == self._number_of_columns)
        assert(board_to_apply.dtype == numpy.int8)

        board_to_apply[0] = self._border_strength
        board_to_apply[:, 0] = self._border_strength

        # keep the effectradius low while making the border speed up greatly the initialization, also you don't need
        # so much border
        # TODO see if this variable is okay, maybe change the way it is determined
        border_variance = 2
        temp_effectradius = int(ceil(ROBOT_RADIUS / self._resolution)) + border_variance

        # TODO make sure this does what you think it does.
        # Top border
        for border in range(0, self._number_of_columns):
            # only for the rows affected by the change.
            for x in range(0, temp_effectradius):

                columnmin = max(0, (border - temp_effectradius - 1))
                columnmax = min(self._number_of_columns, (border + temp_effectradius + 1))

                # for every columns affected
                for y in range(columnmin, columnmax):
                    decay = self._compute_value_by_distance(self._border_strength, self._distance(0, border, x, y))
                    board_to_apply[x, y] += decay

        # left border
        for border in range(0, self._number_of_rows):

            for y in range(0, temp_effectradius):

                rowmin = max(0, (border - temp_effectradius - 1))
                rowmax = min(self._number_of_rows, border + temp_effectradius + 1)

                for x in range(rowmin, rowmax):
                    decay = self._compute_value_by_distance(self._border_strength, self._distance(border, 0, x, y))
                    board_to_apply[x, y] += decay

        # Prend l'image créer et la flip l-r et u-d puis additionne
        temp_inverse_board = numpy.copy(board_to_apply)
        temp_inverse_board = temp_inverse_board[::-1, ::-1]
        board_to_apply += temp_inverse_board

    def _initialize_goals_board(self, v_h_goal_offset):
        """
        Mets des buts sur le starterboard et le board
        """
        # todo fetch which side we are on.
        temp_array = self._create_standard_influence_board()

        self._put_goals_and_propagate(v_h_goal_offset, temp_array)
        numpy.add(temp_array, self._goals_board, out=self._goals_board)

    def _calculate_goal_vertical_offset(self):
        """
        Calcule la dimension vertical du but p/r à la résolution.
        :return: la valeur verticale du but ajusté à la résolution
        :rtype: int
        """
        return int(ceil(FIELD_GOAL_Y_TOP / self._resolution))

    def _calculate_goal_horizontal_offset(self):
        """
        Calcule la dimension horizontale du but p/r à la résolution.

        :return: la valeur horizontale du but ajusté à la résolution
        :rtype: int
        """
        return int(ceil(FIELD_GOAL_SEGMENT / self._resolution))

    def _put_goals_and_propagate(self, v_h_offset, board_to_apply):
        """
        Mets des buts sur le numpy.ndarray fourni.

        :param v_h_offset: la dimension verticale et horizontale des buts.
        :type v_h_offset: tuple (int * int)
        :param board_to_apply: Un numpy.ndarray un array vierge pour y ajouter des buts.
        :type board_to_apply: numpy.ndarray dtype=numpy.int8
        """

        # TODO take into account what team you are ie: orientation and strength adjustment
        for x in range(int(self._number_of_rows / 2 - v_h_offset[0]),
                       int(self._number_of_rows / 2 + v_h_offset[0]) + 1,
                       6):
            self._add_point_and_propagate_influence(x, 0, board_to_apply, 100)

        numpy.add((numpy.negative(board_to_apply[:, ::-1])), board_to_apply, out=board_to_apply)

    def _create_static_board(self):
        """
        Crée des tableaux pour les bordures et les buts et les enregistres dans les variables de classes déjà présente.

        Il reste à déterminer comment on s'occupe de choisir quel tableau static à créer.
        """
        # TODO see to make flags to control what goes into the static board
        self._static_boards = self._create_standard_influence_board()

        self._initialize_borders_board()
        numpy.add(self._borders_board, self._static_boards, out=self._static_boards)

        v_h_goal_offset = (self._calculate_goal_vertical_offset(), self._calculate_goal_horizontal_offset())
        self._initialize_goals_board(v_h_goal_offset)
        numpy.add(self._goals_board, self._static_boards, out=self._static_boards)
        self._clamp_board(self._static_boards)
        # numpy.savetxt("Debug", self._static_boards, fmt='%5i')

    def _compute_value_by_distance(self, strength, distance):
        """
        Calcule la valeur qu'une recoit d'un point de force strength à distance distance.

        :param strength: la force du point central
        :type strength: int
        :param distance: la distance entre le point central et le point où calculer la value
        :type distance: int or float

        :return: la valeur calculé
        :rtype: int

        """
        return int(strength * (self._strength_decay ** distance))

    def _clamp_board(self, board_to_clamp):
        """
        Arrondis toutes les cellules du tableau pour qu'ils soient dans [-self._strength_peak, self._strength_peak].

        :param board_to_clamp: Un numpy.ndarray à clampé
        :type board_to_clamp: numpy.ndarray dtype=numpy.int8
        """
        numpy.clip(board_to_clamp, -self._strength_peak, self._strength_peak, out=board_to_clamp)

    def _add_point_and_propagate_influence(self, row, column, board_to_apply, strength=0):
        """
        Pose un point et propage son influence sur le tableau donné.

        :param int row: la rangée du point d'origine de la force
        :param int column: int La colonne du point d'origine de la force
        :param board_to_apply: numpy.ndarray l'array sur lequel on ajoute un point et on le propage
        :type board_to_apply: numpy.ndarray dtype=numpy.int8
        :param int strength: la force du point à appliquer
        """
        assert (isinstance(row, int))
        assert (isinstance(column, int))
        assert (0 <= row < self._number_of_rows)
        assert (0 <= column < self._number_of_columns)
        assert (isinstance(board_to_apply, numpy.ndarray))
        assert (board_to_apply.shape[0] == self._number_of_rows)
        assert (board_to_apply.shape[1] == self._number_of_columns)
        assert (isinstance(strength, int))
        assert (-self._strength_peak <= strength <= self._strength_peak)

        rowmin = max(0, (row - self._effect_radius))
        rowmax = min((self._number_of_rows - 1), (row + self._effect_radius))

        columnmin = max(0, (column - self._effect_radius))
        columnmax = min((column + self._effect_radius), self._number_of_columns)

        cases_iterator = numpy.nditer(board_to_apply[rowmin:(rowmax + 1), columnmin:(columnmax + 1)],
                                      flags=['multi_index'], op_flags=['readwrite'])

        while not cases_iterator.finished:
            to_put = self._compute_value_by_distance(strength, self._distance(cases_iterator.multi_index[0],
                                                                              cases_iterator.multi_index[1],
                                                                              (row - rowmin),
                                                                              (column - columnmin)))
            influence_already_in_case = cases_iterator[0]
            influence_to_put_instead = to_put + influence_already_in_case
            cases_iterator[0] = influence_to_put_instead
            cases_iterator.iternext()
        self._clamp_board(board_to_apply)

    def _transform_field_to_board_position(self, position):
        assert(isinstance(position, Position))
        assert(FIELD_X_LEFT <= position.x <= FIELD_X_RIGHT)
        assert(FIELD_Y_BOTTOM <= position.y <= FIELD_Y_TOP)
        # this should hold up

        xpos = -position.x + ((abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / 2)
        ypos = position.y + ((abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / 2)

        xpos = int(xpos / self._resolution)
        ypos = int(ypos / self._resolution)

        if ypos == self._number_of_rows:
            ypos -= 1
        if xpos == self._number_of_columns:
            xpos -= 1

        return ypos, xpos

    def _transform_board_to_field_position(self, row, column):
        assert(isinstance(row, int))
        assert(isinstance(column, int))
        assert(0 <= row <= self._number_of_rows)
        assert(0 <= column <= self._number_of_columns)

        # This should hold up
        ypos = row * self._resolution
        xpos = column * self._resolution

        ypos = (ypos - ((abs(FIELD_Y_BOTTOM) + FIELD_Y_TOP) / 2)) + (self._resolution / 2)
        xpos = (xpos - ((abs(FIELD_X_LEFT) + FIELD_X_RIGHT) / 2)) + (self._resolution / 2)

        tempposition = Position(xpos, ypos)
        return tempposition

    def _distance(self, x1, y1, x2, y2):
        assert (isinstance(x1, int or float))
        assert (isinstance(x2, int))
        assert (isinstance(y1, int))
        assert (isinstance(y2, int))

        return sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))