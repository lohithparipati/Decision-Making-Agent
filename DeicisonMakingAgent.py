import copy, sys

class BayesianNode(object):
    def __init__(self, node, parent_nodes, cpt):
        self.node = node
        self.parent_nodes = parent_nodes
        self.cpt = cpt
        self.node_class = ''

    def probability(self, sign, Evidence_dict):
        if self.node_class == 'decision':
            prob_val = 1.0
            return prob_val
        i = 0
        while i != len(self.cpt):
            match_flag = True
            j = 0
            while j != len(self.parent_nodes):
                parent = self.parent_nodes[j]
                value = self.cpt[i][j+1]
                if Evidence_dict[parent] == value:
                    pass
                else:
                    match_flag = False
                    break
                j = j + 1
            if not match_flag:
                pass
            else:
                if sign == '-':
                    return 1.0 - self.cpt[i][0]
                elif sign == '+':
                    return self.cpt[i][0]
            i = i + 1

class BayesianNetwork(object):
    def __init__(self):
        self.node_names = []
        self.nodes_list = []
        self.utility = None

    def create_node(self, bnode_obj):
        self.node_names.append(bnode_obj.node)
        self.nodes_list.append(bnode_obj)

    def fetch_node(self, node_name):
        node_id = self.node_names.index(node_name)
        return self.nodes_list[node_id]


'''Main ASK'''

def ask_main(line_query, bnet_obj):

    line_query = line_query.split('(')
    query_type = line_query[0]
    line_query[1] = line_query[1].strip(')')
    query_dets = line_query[1]

    if query_type == 'P':
        if not ' | ' in query_dets:
            query = query_dets.split(', ')
            E = {}

            i = 0
            while i != len(query):
                key_val = query[i].split(' = ')
                E[key_val[0]] = key_val[1]
                i = i + 1

            prob_val = enumerate_all(bnet_obj.node_names, E, bnet_obj)

        else:

            query_evidence = query_dets.split(' | ')
            query = query_evidence[0].split(', ')
            X = {}

            i = 0
            while i != len(query):
                key_val = query[i].split(' = ')
                X[key_val[0]] = key_val[1]
                # storing it as key value pair, values are signs (t/f)
                i = i + 1

            evidence = query_evidence[1].split(', ')
            E = {}

            i = 0
            while i != len(evidence):
                key_val = evidence[i].split(' = ')
                E[key_val[0]] = key_val[1]
                i = i + 1
            prob_val = enumeration_ask(X, E, bnet_obj)
        '''printing prob'''
        print "%.2f" %round(prob_val, 2)

    elif query_type == 'EU':
        query_evidence = query_dets.split(' | ')
        if (len(query_evidence) <= 1):
            pass
        else:
            query_evidence[0] = query_evidence[0] + ', ' + query_evidence[1]
        first = query_evidence[0]
        querys = first.split(', ')
        E = {}
        i = 0
        while i != len(querys):
            rhs = querys[i]
            rhs = rhs.split(' = ')
            E[rhs[0]] = rhs[1]
            i = i + 1
        eu_val = eu_enumerate_all(E, bnet_obj)
        '''printing eu'''
        print str(int(round(eu_val)))

    elif query_type == 'MEU':
        query_evidence = query_dets.split(' | ')
        X = []
        first = query_evidence[0]
        lhs = first.split(', ')
        for l in lhs:
            X.append(l)
        E = {}
        if(len(query_evidence) != 2):
            pass
        else:
            second = query_evidence[1]
            rhs = second.split(', ')
            i = 0
            while i != len(rhs):
                t = rhs[i].split(' = ')
                E[t[0]] = t[1]
                i = i + 1
        meu_values, meu = meu_enumerate_all(X, E, bnet_obj)
        '''printing meu'''
        meu_str = ''
        for v in meu_values:
            meu_str = meu_str + v + ' '
        print meu_str + str(int(round(meu)))
    else:
        print "Query is of unexpected type"

def true_false_combs(ptr, length):
    combs = []
    i = 0
    while i != length:
        if (ptr >> i) & 1 != 0:
            combs.append('-')
        else:
            combs.append('+')
        i = i + 1
    return combs


'''AIMA 14.9 bayesian network enumeration algo'''
'''enum_ask method'''

def enumeration_ask(Query_dict, Evidence_dict, bnet_obj):
    for key in Query_dict.keys():
        if Evidence_dict.__contains__(key): #query in evidence case
            if Evidence_dict[key] == Query_dict[key]: #sign of those
                Query_dict.__delitem__(key)
            else:
                return 0.0

    prob_list = []
    id = 0
    i = 0
    while i != 2 ** len(Query_dict): ##looping all table entries
        combs = true_false_combs(i, len(Query_dict))
        cp_Evidence_dict = copy.deepcopy(Evidence_dict)
        match_flag = True
        for j in range(len(Query_dict)):
            xj = Query_dict.keys()[j]
            cp_Evidence_dict[xj] = combs[j]
            if combs[j] == Query_dict[xj]:
                pass
            else:
                match_flag = False
        if not match_flag:
            pass
        else:
            id = i
        enum_prob_val = enumerate_all(bnet_obj.node_names, cp_Evidence_dict, bnet_obj)
        prob_list.append(enum_prob_val)
        i = i + 1
    normalize = prob_list[id] / sum(prob_list)
    return normalize

def enumerate_all(nodes_list, Evidence_dict, bnet_obj):
    if len(nodes_list) != 0:
        pass
    else:
        return 1.0
    Y = nodes_list[0]
    node = bnet_obj.fetch_node(Y)
    if Y not in Evidence_dict.keys():
        Evidence_dict_Y_true = copy.deepcopy(Evidence_dict)
        Evidence_dict_Y_true[Y] = '+'
        pos_cal = node.probability('+', Evidence_dict) * enumerate_all(nodes_list[1:], Evidence_dict_Y_true, bnet_obj)
        Evidence_dict_Y_false = copy.deepcopy(Evidence_dict)
        Evidence_dict_Y_false[Y] = '-'
        neg_call = node.probability('-', Evidence_dict) * enumerate_all(nodes_list[1:], Evidence_dict_Y_false, bnet_obj)
        tot = pos_cal + neg_call
        return tot

    else:
        tot = node.probability(Evidence_dict[Y], Evidence_dict) * enumerate_all(nodes_list[1:], Evidence_dict, bnet_obj)
        return tot

def eu_enumerate_all(Evidence_dict, bnet_obj):
    tot = 0.0
    util_node = bnet_obj.utility
    parents = util_node.parent_nodes
    entry = 0
    while entry != len(util_node.cpt):
        X = {}
        j = 0
        while j != len(parents):
            X[parents[j]] = util_node.cpt[entry][j+1]
            j = j + 1
        tot = tot + enumeration_ask(X, Evidence_dict, bnet_obj) * util_node.cpt[entry][0]
        entry = entry + 1
    return tot

def meu_enumerate_all(X, E, bnet_obj):
    max_eu = -1e309
    max_values = []
    i = 0
    while i != 2 ** len(X):
        values = true_false_combs(i, len(X))
        ei = copy.deepcopy(E)
        j = 0
        while j != len(X):
            ei[X[j]] = values[j]
            j = j + 1
        m = eu_enumerate_all(ei, bnet_obj)
        if(m <= max_eu):
            pass
        else:
            max_eu = m
            max_values = values
        i = i + 1
    return max_values, max_eu


def main():

    #fname = 'sample03.txt'
    fname = sys.argv[2]
    fin = open(fname, 'r')
    fout = open('output.txt', 'w')
    sys.stdout = fout

    end_of_data_set = '******'
    end_of_data_in_set = '***'
    end_of_file = ''

    '''Preparing list of Queries'''

    query_list = []
    line = fin.readline()
    exact_line = line.strip('\n')

    while exact_line != end_of_data_set:

        query_list.append(exact_line)
        line = fin.readline()
        exact_line = line.strip('\n')

    '''Preparing Bayesian Network with nodes
    and their corresponding tables'''

    bnet_obj = BayesianNetwork()
    line = fin.readline()
    exact_line = line.strip('\n')

    while exact_line != end_of_file:
        wil = exact_line.split(' ') # wil - words in line
        node = wil[0]
        parent_nodes = wil[2:]
        cpt = []
        decision_flag = False

        cpt_entry = 0
        while cpt_entry != 2 ** len(parent_nodes):
            line = fin.readline()
            exact_line = line.strip('\n')
            wil = exact_line.split(' ')
            if(wil[0] == 'decision'):
                decision_flag = True
                wil[0] = 1.0
            else:
                wil[0] = float(wil[0])
            cpt.append(wil)
            cpt_entry = cpt_entry + 1

        bnode = BayesianNode(node, parent_nodes, cpt)
        if(decision_flag == True):
            bnode.node_class = 'decision'
        bnet_obj.create_node(bnode)

        line = fin.readline()
        exact_line = line.strip('\n')
        if exact_line != end_of_data_in_set:
            break
        line = fin.readline()
        exact_line = line.strip('\n')

    '''Preparing Utility Table'''
    if exact_line == end_of_data_set:

        line = fin.readline()
        exact_line = line.strip('\n')
        wil = exact_line.strip(' ').split(' ')

        node = wil[0] # wil[0] = 'utility'
        parent_nodes = wil[2:]
        cpt = []

        cpt_entry = 0
        while cpt_entry != 2 ** len(parent_nodes):

            line = fin.readline()
            exact_line = line.strip('\n')
            wil = exact_line.split(' ')

            wil[0] = float(wil[0])
            cpt.append(wil)
            cpt_entry = cpt_entry + 1

        bnode = BayesianNode(node, parent_nodes, cpt)
        bnode.node_class = 'utility'
        bnet_obj.utility = bnode


    '''Iterating queries in the query list'''

    flag = True
    query_id = 0
    while query_id != len(query_list):
        if flag:
            pass
        flag = False
        ask_main(query_list[query_id], bnet_obj)
        query_id = query_id + 1

    fin.close()
    fout.close()

if __name__ == '__main__':
    main()