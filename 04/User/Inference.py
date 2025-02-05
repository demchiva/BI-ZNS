from typing import List

from ExpertSystem.Business.UserFramework import IInference, ActionBaseCaller
from ExpertSystem.Structure.Enums import LogicalOperator
from ExpertSystem.Structure.Enums import Operator
from ExpertSystem.Structure.RuleBase import Rule, Fact, ExpressionNode, Expression


class Inference(IInference):
    """
    | User definition of the inference. You can define here you inference method (forward or backward).
      You can have here as many functions as you want, but you must implement interfere with same signature

    |
    | `def interfere(self, knowledge_base: List[Fact], rules: List[Rule], action_base: ActionBase):`
    |

    | Method `interfere` will be called each turn or manually with `Inference` button.
    | Class have no class parameters, you can use only inference parameters

    """
    knowledge_base: List[Fact]
    action_base: ActionBaseCaller
    list_of_fuzzy: list

    def __init__(self):
        super().__init__()
        self.list_of_fuzzy = []

    def infere(self, knowledge_base: List[Fact], rules: List[Rule], action_base: ActionBaseCaller) -> None:
        """
        User defined inference

        :param knowledge_base: - list of Fact classes defined in  KnowledgeBase.create_knowledge_base()
        :param rules:  - list of rules trees defined in rules file.
        :param action_base: - instance of ActionBaseCaller for executing conclusions

        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        !!    TODO: Write implementation of your inference mechanism definition HERE    !!
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """
        self.knowledge_base = knowledge_base
        self.action_base = action_base
        self.list_of_fuzzy = []
        list_of_args = []

        if Fact('player_have_base') in knowledge_base:
            for rule in rules:
                if rule.conclusion.value.value is not None:
                    j = -1
                    for i in self.list_of_fuzzy:
                        if i[0] == rule.conclusion.value.value and self.fuzzy_evaluation(rule.condition) >= i[1] and \
                                i[2] == rule.conclusion.value.args:
                            j = i

                    if j != -1:
                        self.list_of_fuzzy.remove(j)

                    self.list_of_fuzzy.append((rule.conclusion.value.value, self.fuzzy_evaluation(rule.condition),
                                               rule.condition.right.value.args))

                    if rule.condition.right.value.args not in list_of_args:
                        list_of_args.append(rule.condition.right.value.args)

        for j in list_of_args:
            defuzzy = self.defuzzifikace(self.list_of_fuzzy, j)

            for rule in rules:
                if rule.condition.value and rule.condition.value.name == 'postav_maga' and defuzzy >= 5 and rule.conclusion.value.args == j:
                    if not self.knowledge_base[self.knowledge_base.index('occupied')](*rule.conclusion.value.args) and \
                       self.knowledge_base[self.knowledge_base.index('free_money')](30):
                        self.conclusion_evaluation(rule.conclusion)

        for rule in rules:
            if rule.conclusion.value.value is None:
                condition = self.rule_evaluation(rule.condition)
                if condition:
                    self.conclusion_evaluation(rule.conclusion)


    def rule_evaluation(self, root_node: ExpressionNode):
        """
        Example of rule tree evaluation. This implementation did not check comparision operators and uncertainty.
        For usage in inference extend this function

        :param root_node: root node of the rule tree
        :return: True if rules is satisfiable, False in case of not satisfiable or missing Facts
        """
        if root_node.operator == LogicalOperator.AND:
            return self.rule_evaluation(root_node.left) and self.rule_evaluation(root_node.right)

        elif root_node.operator == LogicalOperator.OR:
            return self.rule_evaluation(root_node.left) or self.rule_evaluation(root_node.right)

        elif isinstance(root_node.value, Expression):
            try:
                return self.knowledge_base[self.knowledge_base.index(root_node.value.name)](*root_node.value.args)
            except ValueError:
                return False
        else:
            return bool(root_node.value)

    def fuzzy_evaluation(self, root_node: ExpressionNode):

        first_compare = 1
        second_compare = 1
        if root_node.operator == LogicalOperator.AND:
            if root_node.left.value.comparator == Operator.EQUAL:
                malo, stredne, hodne = self.knowledge_base[self.knowledge_base.index(root_node.left.value.name)](
                    *root_node.left.value.args)

                if root_node.left.value.value == 'malo':
                    first_compare = malo
                elif root_node.left.value.value == 'stredne':
                    first_compare = stredne
                elif root_node.left.value.value == 'hodne':
                    first_compare = hodne

            if root_node.right.value.comparator == Operator.EQUAL:
                blizko, stredne, daleko = self.knowledge_base[self.knowledge_base.index(root_node.right.value.name)](
                        *root_node.right.value.args)

                if root_node.right.value.value == 'blizko':
                    second_compare = blizko
                elif root_node.right.value.value == 'stredne':
                    second_compare = stredne
                elif root_node.right.value.value == 'daleko':
                    second_compare = daleko

            return min(first_compare, second_compare)

        if root_node.operator == LogicalOperator.OR:
            if root_node.left.value.comparator == Operator.EQUAL:
                malo, stredne, hodne = self.knowledge_base[self.knowledge_base.index(root_node.left.value.name)](
                    *root_node.left.value.args)

                if root_node.left.value.value == 'malo':
                    first_compare = malo
                elif root_node.left.value.value == 'stredne':
                    first_compare = stredne
                elif root_node.left.value.value == 'hodne':
                    first_compare = hodne

            if root_node.right.value.comparator == Operator.EQUAL:
                blizko, stredne, daleko = self.knowledge_base[self.knowledge_base.index(root_node.right.value.name)](
                        *root_node.right.value.args)

                if root_node.right.value.value == 'blizko':
                    second_compare = blizko
                elif root_node.right.value.value == 'stredne':
                    second_compare = stredne
                elif root_node.right.value.value == 'daleko':
                    second_compare = daleko

            return max(first_compare, second_compare)

        elif isinstance(root_node.value, Expression):
            try:
                a, b, c = self.knowledge_base[self.knowledge_base.index(root_node.value.name)](*root_node.value.args)

                if root_node.value.value == 'malo' or root_node.value.value == 'blizko':
                    return a
                elif root_node.value.value == 'stredne' or root_node.value.value == 'stredne':
                    return b
                elif root_node.value.value == 'hodne' or root_node.value.value == 'daleko':
                    return c
                return 1
            except ValueError:
                return False
        else:
            return bool(root_node.value)

    def conclusion_evaluation(self, root_node: ExpressionNode):
        if self.action_base.has_method(root_node.value):
            self.action_base.call(root_node.value)

    def defuzzifikace(self, fuzzy, coordinates: list):
        nizko, stredne, vysoko = 0, 0, 0
        total_up, total_bottom = 0, 0
        for i in fuzzy:
            if i[0] == 'nizko' and i[2] == coordinates:
                nizko = i[1]
            elif i[0] == 'stredne' and i[2] == coordinates:
                stredne = i[1]
            elif i[0] == 'vysoko' and i[2] == coordinates:
                vysoko = i[1]

        for i in range(10):
            if 0 <= i <= 3:
                total_up += i * nizko
                total_bottom += nizko
            elif 4 <= i <= 6:
                total_up += i * stredne
                total_bottom += stredne
            else:
                total_up += i * vysoko
                total_bottom += vysoko

        return total_up / (1 if total_bottom == 0 else total_bottom)
