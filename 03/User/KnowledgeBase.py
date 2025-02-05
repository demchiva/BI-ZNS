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
    current_round: int

    def __init__(self, map_proxy: MapProxy, game_object_proxy: GameObjectProxy,
                 game_uncertainty_proxy: GameUncertaintyProxy, player: PlayerTag):
        self.current_round = 0
        super().__init__(map_proxy, game_object_proxy, game_uncertainty_proxy, player)

    def create_knowledge_base(self) -> List[Fact]:

        facts = []

        if not self.map_proxy.player_have_base(self.player):
            facts.append(Fact('player_dont_have_base'))

        facts.append(Fact('free_tile', eval_function=self.first_free_tile, data=self.first_free_tile))
        facts.append(Fact('visible_free_tile', eval_function=self.visible_free_tile,
                          data=self.visible_free_tile))
        facts.append(Fact('free_money', eval_function=self.is_enough_resources))
        facts.append(Fact('check_uncertainly_module', eval_function=self.possible_spawn_tiles,
                          data=self.possible_spawn_tiles))
        facts.append(Fact('neighbour_for_king', eval_function=self.neighbour_for_king, data=self.neighbour_for_king))
        facts.append(Fact('round_control', eval_function=self.round_control))

        return facts

    def round_control(self):
        self.current_round += 1
        return self.current_round

    def first_free_tile(self, terrain_type: str):
        """ Find random tile with given terrain type """
        tiles = self.map_proxy.get_inner_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        for position in tiles:
            terrain = self.map_proxy.get_terrain_type(position) == TerrainType.from_string(terrain_type)
            if terrain and position not in border_tiles:
                return position
        return None

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

    def visible_free_tile(self, terrain_type: str):
        """ Find random free tile with given terrain type """
        tiles = self.map_proxy.get_player_visible_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        # If all neighbours are occupied find a new free position on map
        for position in tiles:
            terrain = self.map_proxy.get_terrain_type(position) == TerrainType.from_string(terrain_type)
            occupied = self.map_proxy.is_position_occupied(position)
            if terrain and not occupied and position not in border_tiles:
                return position
        return None

    def is_enough_resources(self, count_of_resources: str):
        return self.game_object_proxy.get_resources(self.player) >= int(count_of_resources)

    def possible_spawn_tiles(self, uncertainly):
        """ Get list of possible tiles, where enemy spawn a unit """
        spawn_info = self.game_uncertainty_proxy.spawn_information()
        tiles = self.map_proxy.get_player_visible_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        next_round = spawn_info[0]

        possible_tiles = set()

        for unit in next_round:
            uncertainly_array = [x.uncertainty for x in unit.positions]
            max_uncertainly = max(uncertainly_array)
            possible_tiles.update([x for x in unit.positions if x.uncertainty == max_uncertainly])

        position_set = set()
        for i in possible_tiles:
            if float(i.uncertainty) >= float(uncertainly):
                position_set.add(i.position)

        for i in position_set:
            for j in i.get_all_neighbours():
                for z in j.get_all_neighbours():
                    if z not in border_tiles and z in tiles and not self.map_proxy.is_position_occupied(z):
                        return z
        return None

    def check_direction(self, uncertainly):
        """ Get list of possible tiles, where enemy spawn a unit """
        spawn_info = self.game_uncertainty_proxy.spawn_information()
        tiles = self.map_proxy.get_player_visible_tiles()
        border_tiles = self.map_proxy.get_border_tiles()

        next_round = spawn_info[0]

        possible_tiles = set()

        for unit in next_round:
            uncertainly_array = [x.uncertainty for x in unit.positions]
            max_uncertainly = max(uncertainly_array)
            possible_tiles.update([x for x in unit.positions if x.uncertainty == max_uncertainly])

        position_set = set()
        for i in possible_tiles:
            if float(i.uncertainty) >= float(uncertainly):
                position_set.add(i.position)

        for i in possible_tiles:
            for j in i.position.get_all_neighbours():
                for z in j.get_all_neighbours():
                    if z not in border_tiles and z in tiles and not self.map_proxy.is_position_occupied(z):
                        return z
        return None
