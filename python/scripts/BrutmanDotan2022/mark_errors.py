import sc
import sc.utils as u

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/data/'


analyzer_12 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=False, accuracy_per_digit=True)
analyzer_12.run(base_dir + 'exp1&2/data_exp12.xlsx', base_dir + 'exp1&2')

analyzer_3 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=False)
analyzer_3.run(base_dir+'exp3/data_exp3.xlsx', base_dir+'exp3', False)

analyzer_4 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=True)
analyzer_4.run(base_dir + 'exp4/data_exp4.xlsx', base_dir + 'exp4', True)

analyzer_5 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=True)
analyzer_5.run(base_dir + 'exp5/data_exp5.xlsx', base_dir + 'exp5', True)
