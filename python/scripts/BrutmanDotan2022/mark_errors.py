import sc
import sc.utils as u

base_dir = '/Users/dror/data/acad-proj/3-Submitted/syntactic chunking Nadin/data/'


analyzer_12 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=False, accuracy_per_digit=True)
analyzer_12.run_for_worksheet(base_dir+'exp1&2/data_exp12.xlsx', base_dir+'exp1&2')

analyzer_3 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=False)
analyzer_3.run_for_worksheet(base_dir+'exp3/data_exp3.xlsx', False, base_dir+'exp3')

analyzer_4 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=True)
analyzer_4.run_for_worksheet(base_dir+'exp4/data_exp4.xlsx', True, base_dir+'exp4')

analyzer_5 = sc.markerr.ErrorAnalyzer(subj_id_transformer=u.clean_subj_id, consider_thousand_as_digit=True)
analyzer_5.run_for_worksheet(base_dir+'exp5/data_exp5.xlsx', True, base_dir+'exp5')
