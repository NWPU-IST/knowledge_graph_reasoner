





if __name__ == "__main__":
    nodes_id, edge_id = load_kgminer_resource()
    with open(KGMiner_data+'/sample_case/0sample_case.csv', 'rb') as f:
        reader = csv.reader(f)
        entity_sets = list(reader)
        entity_set = sum(entity_sets,[])
        node_ids = entity_id_finder(entity_set)
        expected_entities = entity_set[:2]
        training_data, test_data = train_data_csv(entity_set, node_ids, expected_entities)
        print training_data, test_data
        csv_writer(training_data, file_name='/sample_case/0sample_case_ids_backup')
        copyfile(KGMiner_data + '/sample_case/0sample_case_ids_backup.csv', KGMiner_data + '/training_data.csv')
        invoke_kgminer()