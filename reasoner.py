def get_rule_predicates(data_source, top_k, predicate):
    text = open('LPmln/' + data_source + '/rudik_rules_'+top_k + '/' + predicate + '_all', 'r')
    f = text.read()
    text.close()
    probs = re.findall("(\w+\()", f)
    probs = list(set(probs))
    predicates = [p.replace('(', '') for p in probs]
    return predicates


def evidence_writer(filtered_evidence, sentence_id, data_source, resource_v, top_k, predicate, set_up, rule_predicates):
    data_source = data_source+ '/' + set_up
    rule_predicates = get_rule_predicates(data_source, top_k, predicate)
    item_set = OrderedSet()
    print resource_v, predicate
    for evidence in filtered_evidence:
        if evidence[1] in rule_predicates:
            if evidence[0] == resource_v[0] and evidence[2] == resource_v[1] and evidence[1] == predicate:
                pass
            else:
                try:
                    item_set.add(evidence[1] + '("' + evidence[0] + '","' + evidence[2] + '").')
                except:
                    pass
    with open('LPmln/' + data_source + '/evidence_'+top_k+'/' + sentence_id + predicate + '.txt', 'wb') as csvfile:
        for i in item_set:
            if '*' not in i:
                try:
                    csvfile.write(i+'\n')
                except:
                    pass

    with open('LPmln/' + data_source + '/evidence_'+top_k+'/' + sentence_id + predicate + '.txt', 'r') as f, \
            open('LPmln/' + data_source + '/evidence_'+top_k+'/' + sentence_id + predicate + '_unique.txt', 'wb') as\
                    out_file:
        out_file.writelines(unique_everseen(f))
    remove_file = 'LPmln/' + data_source + '/evidence_'+top_k+'/' + sentence_id + predicate + '.txt'
    os.remove(remove_file)
    return item_set