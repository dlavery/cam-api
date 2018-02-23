import json

class RuleSet:
    '''
    Classify subjects according to JSON rules
    '''

    def __init__(self, data):
        self.data = data

    def process_when(self, attr, when):
        if type(when) is dict:
            # process recursively
            for k, v in when.items():
                self.current_node = when
                self.process_when(k, v)
        elif type(when) is list:
            # evaluate conditions
            if when[0] == 'NULL':
                if attr not in self.subject:
                    self.current_node[attr] = True
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

    def process_andor(self, when):
        for k, v in when.items():
            if k == 'or':
                satisfied = False
                for k1, v1 in v.items():
                    if type(v1) == dict:
                        return False
                    elif v1 == True:
                        satisfied = True
                #when['or'] = satisfied
                return satisfied
            elif k == 'and':
                satisfied = True
                for k1, v1 in v.items():
                    if type(v1) == dict:
                        return False
                    elif v1 == False:
                        satisfied = False
                #when['and'] = satisfied
                return satisfied
            else:
                if type(v) == bool:
                    return v
                else:
                    continue

    def process_then(self, rule):
        if 'then' in rule:
            for k, v in rule['then'].items():
                self.subject[k] = v

    def evaluate(self, subject):
        self.ruleset = self.data['rules']
        self.subject = subject
        for rule in self.ruleset:
            if 'when' in rule:
                self.process_when('when', rule['when'])
                if self.process_andor(rule['when']):
                    self.process_then(rule)
            else:
                self.process_then(rule)
        return self.subject

if __name__ == '__main__':
    with open('people.json') as f1:
        people_data = json.load(f1)
    for person in people_data['people']:
        with open('rules.json') as f2:
            rules_data = json.load(f2)
        rs = RuleSet(rules_data)
        print(rs.evaluate(person))
