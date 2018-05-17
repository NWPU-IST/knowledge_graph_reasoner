import csv
import argparse
from main import lpmln_reasoning, stats_computer
from resource_writer import update_resources
from reasoner import get_rule_predicates
import sys
import datetime


def query_test(triples_list, id_list, true_labels, data_source, data_size, init_time, const):
    results_hard = {}
    results_soft = {}
    results_mcsat = {}
    true_count = 0
    false_count = 0
    true_pos = 0
    true_neg = 0
    false_neg, false_pos = 0, 0
    true_neutral, false_neutral = 0, 0
    true_none, false_none = 0, 0
    true_unsat, false_unsat = 0, 0
    true_no_evd, false_no_evd = 0, 0

    true_pos_wt = 0
    true_neg_wt = 0
    false_neg_wt, false_pos_wt = 0, 0
    true_neutral_wt, false_neutral_wt = 0, 0
    true_none_wt, false_none_wt = 0, 0
    true_unsat_wt, false_unsat_wt = 0, 0
    true_no_evd_wt, false_no_evd_wt = 0, 0
    rule_predicates, rules = get_rule_predicates(data_source, data_size, const)
    lpmln_evaluation_map = [['sentence_id', 'true_label', 'sentence', 'map_hard_label',\
                         'map_soft_label', 'map_hard_as','map_soft_as']]
    lpmln_evaluation_mcsat = [['sentence_id', 'true_label', 'sentence', 'mc_label', \
                             'mc_prob']]
    # error_list_author_const_soft = ['255','343','361']
    for t, triple in enumerate(triples_list):
        sentence_id = id_list[t]
        # if sentence_id in error_list:
        #     continue
        print true_labels[t]
        true_label = int(float(true_labels[t]))

        if true_label == 1:
            true_count += 1
        else:
            false_count += 1

        triple_check = triples_list[t]
        print sentence_id, triple_check, true_label, '\n'
        map_wt, label_map_wt, map, prob, label_prob, label_map, query_prob, query_map = lpmln_reasoning(triple_check,\
                                                        rule_predicates, sentence_id, data_source, rules)
        if query_map:
            if true_label == 1 and label_map == '1':
                true_pos += 1
            elif true_label == 0 and label_map == '-1':
                true_neg += 1
            elif true_label == 1 and label_map == '-1':
                false_neg += 1
            elif true_label == 0 and label_map == '1':
                false_pos += 1
            elif true_label == 0 and label_map == 'None':
                false_none += 1
            elif true_label == 1 and label_map == 'None':
                true_none += 1
            elif true_label == 0 and label_map == '0':
                false_neutral += 1
            elif true_label == 1 and label_map == '0':
                true_neutral += 1
            elif true_label == 0 and label_map == 'UNSAT':
                false_unsat += 1
            elif true_label == 1 and label_map == 'UNSAT':
                true_unsat += 1
            elif true_label == 1 and label_map == 'NO_EVD':
                true_no_evd += 1
            elif true_label == 0 and label_map == 'NO_EVD':
                false_no_evd += 1

            if true_label == 1 and label_map_wt == '1':
                true_pos_wt += 1
            elif true_label == 0 and label_map_wt == '-1':
                true_neg_wt += 1
            elif true_label == 1 and label_map_wt == '-1':
                false_neg_wt += 1
            elif true_label == 0 and label_map_wt == '1':
                false_pos_wt += 1
            elif true_label == 0 and label_map_wt == 'None':
                false_none_wt += 1
            elif true_label == 1 and label_map_wt == 'None':
                true_none_wt += 1
            elif true_label == 0 and label_map_wt == '0':
                false_neutral_wt += 1
            elif true_label == 1 and label_map_wt == '0':
                true_neutral_wt += 1
            elif true_label == 0 and label_map_wt == 'UNSAT':
                false_unsat_wt += 1
            elif true_label == 1 and label_map_wt == 'UNSAT':
                true_unsat_wt += 1
            elif true_label == 1 and label_map_wt == 'NO_EVD':
                true_no_evd_wt += 1
            elif true_label == 0 and label_map_wt == 'NO_EVD':
                false_no_evd_wt += 1
            lpmln_evaluation_map.append(
                [sentence_id, true_label, triple_check, str(label_map), str(label_map_wt), str(map), str(map_wt)])

        if query_prob:
            if true_label == 1 and label_prob == '1':
                true_pos += 1
            elif true_label == 0 and label_prob == '-1':
                true_neg += 1
            elif true_label == 1 and label_prob == '-1':
                false_neg += 1
            elif true_label == 0 and label_prob == '1':
                false_pos += 1
            elif true_label == 1 and (label_prob == 'equal' or label_prob == '0'):
                true_neutral += 1
            elif true_label == 0 and (label_prob == 'equal' or label_prob == '0'):
                false_neutral += 1
            elif true_label == 0 and label_prob == 'None':
                false_none += 1
            elif true_label == 1 and label_prob == 'None':
                true_none += 1
            elif true_label == 1 and label_prob == 'NO_EVD':
                true_no_evd += 1
            elif true_label == 0 and label_prob == 'NO_EVD':
                false_no_evd += 1
            lpmln_evaluation_mcsat.append([sentence_id, true_label, triple_check,str(label_prob), str(prob)])



    if query_map:
        results_hard = {'true_pos': true_pos, 'true_neg': true_neg, 'false_neg': false_neg, 'false_pos': false_pos, \
                        'true_neutral': true_neutral, 'false_neutral': false_neutral, 'true_none': true_none + true_no_evd, \
                        'false_none': false_none + false_no_evd, 'true_unsat': true_unsat, 'false_unsat': false_unsat}

        results_soft = {'true_pos': true_pos_wt, 'true_neg': true_neg_wt, 'false_neg': false_neg_wt,
                        'false_pos': false_pos_wt, \
                        'true_neutral': true_neutral_wt, 'false_neutral': false_neutral_wt,
                        'true_none': true_none + true_no_evd_wt, \
                        'false_none': false_none + false_no_evd_wt, 'true_unsat': true_unsat_wt,
                        'false_unsat': false_unsat_wt}
        stats_computer(init_time, true_count, true_pos, false_count, true_neg, data_source, true_neutral, false_neutral, \
                       false_neg, false_pos, true_none, false_none, true_unsat, false_unsat, true_no_evd, false_no_evd, \
                       true_neutral_wt, false_neutral_wt, false_neg_wt, false_pos_wt, true_none_wt, false_none_wt, \
                       true_unsat_wt, false_unsat_wt, true_no_evd_wt, false_no_evd_wt, true_pos_wt, true_neg_wt, const,
                       data_size)
        lpmln_type = 'map'
        lpmln_evaluation = lpmln_evaluation_map

    if query_prob:
        results_mcsat = {'true_pos': true_pos, 'true_neg': true_neg, 'false_neg': false_neg, 'false_pos': false_pos, \
                        'true_neutral': true_neutral, 'false_neutral': false_neutral,
                        'true_none': true_none + true_no_evd, \
                        'false_none': false_none + false_no_evd, 'true_unsat': true_unsat, 'false_unsat': false_unsat}
        lpmln_type = 'mc_sat'
        lpmln_evaluation = lpmln_evaluation_mcsat

    update_resources(triple_flag=False, ambiverse_flag=False, file_triples=False, ambiverse_resources=False, \
                     lpmln_evaluation=lpmln_evaluation, data_source=data_source, input=input,\
                     const=const,data_size=data_size,lpmln_type=lpmln_type)
    return results_hard, results_soft, results_mcsat


def write_stats(data_source, data_size, const, results_hard, results_soft, result_mcsat, start_time):
    end_time = datetime.datetime.now()
    if result_mcsat:
        with open('dataset/' + data_source + '/output_stats/summary_'+data_size+'_'+const+'_'+str(end_time)+'_output.csv','a') as file:
            file.write('True Examples , Weighted Rules , False Examples , Weighted Rules' +'\n')
            file.write('True Positives ,' + str(result_mcsat.get('true_pos',0))\
                       + '/200 ,True Negatives,' + \
                       str(result_mcsat.get('true_neg',0))+'/200'+ '\n')
            file.write(
                'False Negatives ,' + str(result_mcsat.get('false_neg', 0)) \
                + '/200 ,False Positives,' + '/200, ' + \
                str(result_mcsat.get('false_pos', 0)) + '/200' + '\n')
            file.write(
                'Neutral ,' + str(result_mcsat.get('true_neutral', 0)) \
                + '/200 ,Neutral,' + '/200, ' + \
                str(result_mcsat.get('false_neutral', 0)) + '/200' + '\n')
            file.write(
                'None ,' + str(result_mcsat.get('true_none', 0)) \
                + '/200 ,None,' + str(result_mcsat.get('false_none', 0)) + '/200' + '\n')
            file.write(
                'UNSATISFIABLE ,' + str(result_mcsat.get('true_unsat', 0)) \
                + '/200 ,UNSATISFIABLE,' + str(result_mcsat.get('false_unsat', 0)) + '/200' + '\n')
            file.write("Execution Time, "+ str((end_time-start_time).total_seconds()))

    else:
        with open('dataset/' + data_source + '/output_stats/summary_'+data_size+'_'+const+'_'+str(end_time)+'_output.csv','a') as file:
            file.write('True Examples , Hard Rules , Weighted Rules , False Examples , Hard Rules , Weighted Rules' +'\n')
            file.write('True Positives ,'+ str(results_hard.get('true_pos',0))+ '/200 ,'+ str(results_soft.get('true_pos',0))\
                       + '/200 ,True Negatives,'+str(results_hard.get('true_neg',0))+'/200, '+ \
                       str(results_soft.get('true_neg',0))+'/200'+ '\n')
            file.write(
                'False Negatives ,' + str(results_hard.get('false_neg', 0)) + '/200 ,' + str(results_soft.get('false_neg', 0)) \
                + '/200 ,False Positives,' + str(results_hard.get('false_pos', 0)) + '/200, ' + \
                str(results_soft.get('false_pos', 0)) + '/200' + '\n')
            file.write(
                'Neutral ,' + str(results_hard.get('true_neutral', 0)) + '/200 ,' + str(results_soft.get('true_neutral', 0)) \
                + '/200 ,Neutral,' + str(results_hard.get('false_neutral', 0)) + '/200, ' + \
                str(results_soft.get('false_neutral', 0)) + '/200' + '\n')
            file.write(
                'None ,' + str(results_hard.get('true_none', 0)) + '/200 ,' + str(results_soft.get('true_none', 0)) \
                + '/200 ,None,' + str(results_hard.get('false_none', 0)) + '/200, ' + \
                str(results_soft.get('false_none', 0)) + '/200' + '\n')
            file.write(
                'UNSATISFIABLE ,' + str(results_hard.get('true_unsat', 0)) + '/200 ,' + str(results_soft.get('true_unsat', 0)) \
                + '/200 ,UNSATISFIABLE,' + str(results_hard.get('false_unsat', 0)) + '/200, ' + \
                str(results_soft.get('false_unsat', 0)) + '/200' + '\n')
            file.write("Execution Time, "+ str((end_time-start_time).total_seconds()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default='test_sample.csv')
    parser.add_argument("-t", "--test_predicate", default='sample_case')
    parser.add_argument("-s", "--sampling", default=True)
    args = parser.parse_args()
    # data_sizes = ['1k', '5k', '10k']
    start_time = datetime.datetime.now()

    data_sizes = ['0k']
    constraint = ['const_','']
    # constraint = ['const_']
    for data_size in data_sizes:
        for const in constraint:
            print "query for",data_size, const
            print"++++++++++++++++"
            init_time = datetime.datetime.now()
            input_file = 'dataset/' + args.test_predicate + '/input/test_' + data_size + '.csv'
            # input_file = 'dataset/' + args.test_predicate + '/input/test_sample' + '.csv'
            with open(input_file) as f:
                reader = csv.DictReader(f)
                triples_list = []
                id_list = []
                true_labels = []
                for row in reader:
                    if args.sampling:
                        triples_list.append([row.get('sub'), row.get('obj')])
                    else:
                        triples_list.append([row.get('sub').split(":")[1], row.get('obj').split(":")[1]])
                    true_labels.append(row.get('class'))
                    id_list.append(row.get('sid'))
                results_hard, results_soft, results_mcsat = query_test(triples_list, id_list, true_labels, args.test_predicate, \
                                                        data_size, init_time, const)
            write_stats(args.test_predicate,data_size,const,results_hard,results_soft,results_mcsat, start_time)
