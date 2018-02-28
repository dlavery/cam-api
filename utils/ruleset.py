import json

class RuleSet:
    '''
    Classify subjects according to JSON rules
    '''

    def __init__(self, data):
        self.data = data

    def evaluate_conditions(self, attr, when):
        if type(when) is dict:
            # process recursively
            for k, v in when.items():
                self.current_node = when
                self.evaluate_conditions(k, v)
        elif type(when) is list:
            # evaluate conditions
            if when[0] == 'NULL':
                if attr not in self.subject:
                    self.current_node[attr] = True
            elif when[0] == 'ALL':
                if type(self.subject[attr]) is list and type(when[1]) is list:
                    if all([x in self.subject[attr]] for x in when[1]):
                        self.current_node[attr] = True
                    else:
                        self.current_node[attr] = False
                else:
                    self.current_node[attr] = False
            elif when[0] == 'ANY':
                if type(self.subject[attr]) is list and type(when[1]) is list:
                    if any([x in self.subject[attr]] for x in when[1]):
                        self.current_node[attr] = True
                    else:
                        self.current_node[attr] = False
                else:
                    self.current_node[attr] = False
            elif when[0] == 'IN':
                if self.subject[attr] in when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
            elif when[0] == 'EQ':
                if self.subject[attr] == when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
            elif when[0] == 'LT':
                if self.subject[attr] < when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
            elif when[0] == 'GT':
                if self.subject[attr] > when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
            elif when[0] == 'LE':
                if self.subject[attr] <= when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
            elif when[0] == 'GE':
                if self.subject[attr] >= when[1]:
                    self.current_node[attr] = True
                else:
                    self.current_node[attr] = False
        else:
            # ignore unexpected elements
            pass

    def evaluate_when(self, when):
        andor = {'and': True, 'or': False}
        for k, v in when.items():
            if k in andor:
                res = andor[k]
                for k1, v1 in v.items():
                    if type(v1) == dict:
                        if self.evaluate_when(v1) == (not andor[k]):
                            res = (not andor[k])
                    elif (type(v1) == bool and v1 == (not andor[k])):
                        res = (not andor[k])
            elif type(v) == bool:
                res = v
            else:
                continue
        return res

    def action_then(self, rule):
        if 'then' in rule:
            for k, v in rule['then'].items():
                self.subject[k] = v

    def evaluate(self, subject):
        self.ruleset = self.data['rules']
        self.subject = subject
        for rule in self.ruleset:
            if 'when' in rule:
                self.evaluate_conditions('when', rule['when'])
                if self.evaluate_when(rule['when']):
                    self.action_then(rule)
            else:
                self.action_then(rule)
        return self.subject
