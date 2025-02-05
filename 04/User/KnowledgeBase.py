from typing import List
from OrodaelTurrim.Business.Interface.Player import PlayerTag
from OrodaelTurrim.Business.Proxy import MapProxy, GameObjectProxy, GameUncertaintyProxy
from ExpertSystem.Business.UserFramework import IKnowledgeBase
from ExpertSystem.Structure.RuleBase import Fact
from OrodaelTurrim.Structure.Enums import TerrainType, AttributeType, EffectType, GameRole
from OrodaelTurrim.Structure.Position import OffsetPosition, CubicPosition, AxialPosition


class KnowledgeBase(IKnowledgeBase):
    """
    Class for defining known facts based on Proxy information. You can transform here any information from
    proxy to better format of Facts. Important is method `create_knowledge_base()`. Return value of this method
    will be passed to `Inference.interfere`. It is recommended to use Fact class but you can use another type.

    |
    |
    | Class provides attributes:

    - **map_proxy [MapProxy]** - Proxy for access to map information
    - **game_object_proxy [GameObjectProxy]** - Proxy for access to all game object information
    - **uncertainty_proxy [UncertaintyProxy]** - Proxy for access to all uncertainty information in game
    - **player [PlayerTag]** - class that serve as instance of user player for identification in proxy methods

    """
    map_proxy: MapProxy
    game_object_proxy: GameObjectProxy
    game_uncertainty_proxy: GameUncertaintyProxy
    player: PlayerTag

    def __init__(self, map_proxy: MapProxy, game_object_proxy: GameObjectProxy,
                 game_uncertainty_proxy: GameUncertaintyProxy, player: PlayerTag):
        super().__init__(map_proxy, game_object_proxy, game_uncertainty_proxy, player)

    def create_knowledge_base(self) -> List[Fact]:

        facts = []

        if not self.map_proxy.player_have_base(self.player):
            facts.append(Fact('player_dont_have_base'))

        if self.map_proxy.get_bases_positions():
            facts.append(Fact('player_have_base'))

        facts.append(Fact('visible_free_tile', eval_function=self.visible_free_tile,
                          data=self.visible_free_tile))
        facts.append(Fact('free_money', eval_function=self.is_enough_money))
        facts.append(Fact('money', eval_function=self.all_fuzzy_money, data=self.all_fuzzy_money))
        facts.append(Fact('position', eval_function=self.all_fuzzy_position, data=self.all_fuzzy_position))
        facts.append(Fact('neighbour_for_king', eval_function=self.neighbour_for_king,
                          data=self.neighbour_for_king))
        facts.append(Fact('occupied', eval_function=self.is_occupied))

        return facts

    def is_enough_money(self, money):
        return self.game_object_proxy.get_resources(self.player) >= int(money)

    def is_occupied(self, x, y):
        return self.map_proxy.is_position_occupied(OffsetPosition(x, y))

    def neighbour_for_king(self):
        tiles = self.map_proxy.get_player_visible_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        # Find position player on map
        position_of_base = None
        for i in self.map_proxy.get_bases_positions():
            position_of_base = i

        # Find all neighbours of player on map
        for neighbour in position_of_base.get_all_neighbours():
            occupied = self.map_proxy.is_position_occupied(neighbour)
            if not occupied and neighbour not in border_tiles:
                return neighbour

        for neighbour in position_of_base.get_all_neighbours():
            for n_neighbour in neighbour.get_all_neighbours():
                occupied = self.map_proxy.is_position_occupied(n_neighbour)
                if not occupied and n_neighbour not in border_tiles and n_neighbour in tiles:
                    return n_neighbour

    def visible_free_tile(self):
        tiles = self.map_proxy.get_player_visible_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        for position in tiles:
            occupied = self.map_proxy.is_position_occupied(position)
            if not occupied and position not in border_tiles:
                return position
        return None

    def all_fuzzy_money(self):
        return self.fuzzy_money('malo'), self.fuzzy_money('stredne'), self.fuzzy_money('hodne')

    def fuzzy_money(self, fuzzy_rule):
        x = self.game_object_proxy.get_resources(self.player)

        if fuzzy_rule == 'malo':
            a, b, c, d = 0, 0, 40, 50

        elif fuzzy_rule == 'stredne':
            a, b, c, d = 40, 50, 65, 70

        elif fuzzy_rule == 'hodne':
            a, b, c, d = 65, 80, 100, 100
        else:
            a, b, c, d = -1, -1, -1, -1

        if a == b:
            if x <= c:
                return 1
            if x >= d:
                return 0
            if c < x < d:
                return (x - d) / (c - d)

        if c == d:
            if x <= a:
                return 0
            if x >= b:
                return 1
            if a < x < b:
                return (x - a) / (b - a)

        return max(min((x - a) / (b - a), 1, (d - x) / (d - c)), 0)

    def all_fuzzy_position(self, x, y):
        return self.fuzzy_position(x, y, 'blizko'), self.fuzzy_position(x, y, 'stredne'), self.fuzzy_position(x, y, 'daleko')

    def fuzzy_position(self, x, y, fuzzy_rule):
        position = OffsetPosition(x, y)

        if position not in self.map_proxy.get_player_visible_tiles() and fuzzy_rule == 'daleko':
            return 1

        if position not in self.map_proxy.get_player_visible_tiles() and fuzzy_rule != 'daleko':
            return 0

        length_from_king = -1
        base_position = OffsetPosition(0, 0)
        visited = {OffsetPosition(0, 0)}

        if position in base_position.get_all_neighbours():
            length_from_king = 1

        if length_from_king != 1:

            for i in base_position.get_all_neighbours():
                visited.add(i)

            for i in visited:
                if position in i.get_all_neighbours():
                    length_from_king = 2

            temp = set()
            for i in visited:
                for j in i.get_all_neighbours():
                    temp.add(j)

            for i in temp:
                visited.add(i)

            if length_from_king != 2:
                for i in visited:
                    if position in i.get_all_neighbours():
                        length_from_king = 3

                temp = set()
                for i in visited:
                    for j in i.get_all_neighbours():
                        temp.add(j)

                for i in temp:
                    visited.add(i)

                if length_from_king != 3:
                    for i in visited:
                        if position in i.get_all_neighbours():
                            length_from_king = 4

                    temp = set()
                    for i in visited:
                        for j in i.get_all_neighbours():
                            temp.add(j)

                    for i in temp:
                        visited.add(i)

                    if length_from_king not in [1, 2, 3, 4]:
                        length_from_king = 5

        if fuzzy_rule == 'blizko':
            a, b, c, d = 0, 0, 1, 2

        elif fuzzy_rule == 'stredne':
            a, b, c, d = 2, 2, 3, 4

        elif fuzzy_rule == 'daleko':
            a, b, c, d = 3, 4, 5, 5
        else:
            a, b, c, d = -1, -1, -1, -1

        if a == b:
            if length_from_king <= c:
                if fuzzy_rule == 'stredne' and length_from_king < b:
                    return 0
                else:
                    return 1
            if length_from_king >= d:
                return 0
            if c < length_from_king < d:
                return (length_from_king - d) / (c - d)

        if c == d:
            if length_from_king <= a:
                return 0
            if length_from_king >= b:
                return 1
            if a < length_from_king < b:
                return (length_from_king - a) / (b - a)

        return max(min((length_from_king - a) / (b - a), 1, (d - length_from_king) / (d - c)), 0)
