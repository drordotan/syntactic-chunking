import sc
import sc.utils as u

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/data/'


sc.aerr.analyze_errors(base_dir + 'exp1&2/data_exp12.xlsx', base_dir + 'exp1&2', False, subj_id_transformer=u.clean_subj_id, per_word=True)
sc.aerr.analyze_errors(base_dir + 'exp3/data_exp3.xlsx', base_dir + 'exp3', False, subj_id_transformer=u.clean_subj_id)
sc.aerr.analyze_errors(base_dir + 'exp4/data_exp4.xlsx', base_dir + 'exp4', True, subj_id_transformer=u.clean_subj_id)
