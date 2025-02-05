from typing import List, Set

from OrodaelTurrim.Business.Interface.Player import IPlayer
from OrodaelTurrim.Business.Proxy import MapProxy, GameObjectProxy, GameUncertaintyProxy
from ExpertSystem.Business.UserFramework import IKnowledgeBase
from ExpertSystem.Structure.RuleBase import Fact
from OrodaelTurrim.Structure.Position import OffsetPosition
from OrodaelTurrim.Structure.Enums import TerrainType


class KnowledgeBase(IKnowledgeBase):
    """
    Class for defining known facts based on Proxy information. You can transform here any information from
    proxy to better format of Facts. Important is method `create_knowledge_base()`. Return value of this method
    will be passed to `Interference.interfere`. It is recommended to use Fact class but you can use another type.

    |
    |
    | Class provides attributes:

    - **map_proxy [MapProxy]** - Proxy for access to map information
    - **game_object_proxy [GameObjectProxy]** - Proxy for access to all game object information
    - **uncertainty_proxy [UncertaintyProxy]** - Proxy for access to all uncertainty information in game
    - **player [IPlayer]** - instance of user player for identification in proxy methods

    """
    map_proxy: MapProxy
    game_object_proxy: GameObjectProxy
    game_uncertainty_proxy: GameUncertaintyProxy
    player: IPlayer


    def __init__(self, map_proxy: MapProxy, game_object_proxy: GameObjectProxy,
                 game_uncertainty_proxy: GameUncertaintyProxy, player: IPlayer):
        """
        You can add some code to __init__ function, but don't change the signature. You cannot initialize
        KnowledgeBase class manually so, it is make no sense to change signature.
        """
        super().__init__(map_proxy, game_object_proxy, game_uncertainty_proxy, player)

    def is_enough_resources(self, count_of_resources):
        return self.game_object_proxy.get_resources(self.player) >= int(count_of_resources)


    def create_knowledge_base(self) -> List[Fact]:
        """
        Method for create user knowledge base. You can also have other class methods, but entry point must be this
        function. Don't change the signature of the method, you can change return value, but it is not recommended.

        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        !!  TODO: Write implementation of your knowledge base definition HERE   !!
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """

        facts = []

        # Add bool fact
        if not self.map_proxy.player_have_base(self.player):
            facts.append(Fact('player_dont_have_base'))

        facts.append(Fact('is_enough_resources', lambda x: 1 if self.is_enough_resources(x) else 0 ))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-1, -2)) and \
                OffsetPosition(-1, -2) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_a'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(1, -2)) and \
                OffsetPosition(1, -2) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_b'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-2, -1)) and \
                OffsetPosition(-2, -1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_c'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-2, 1)) and \
                OffsetPosition(-2, 1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_d'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(2, 1)) and \
                OffsetPosition(2, 1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_e'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(2, -1)) and \
                OffsetPosition(2, -1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_f'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(0, 2)) and \
                OffsetPosition(0, 2) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_i'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(0, -2)) and \
                OffsetPosition(0, -2) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_with_ent_seventh_side_g'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-1, -1)) and \
                OffsetPosition(-1, -1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_seventh_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-1, 0)) and \
                OffsetPosition(-1, 0) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_first_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(0, -1)) and \
                OffsetPosition(0, -1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_third_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(0, 1)) and \
                OffsetPosition(0, 1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_fourth_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(1, -1)) and \
                OffsetPosition(1, -1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_sixth_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(1, 0)) and \
                OffsetPosition(1, 0) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_eighth_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(-1, 1)) and \
                OffsetPosition(-1, 1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_second_side'))

        if not self.map_proxy.is_position_occupied(OffsetPosition(1, 1)) and \
                OffsetPosition(1, 1) in self.map_proxy.get_player_visible_tiles():
            facts.append(Fact('possible_to_protect_fifth_side'))

        return facts