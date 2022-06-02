import sc
import sc.utils as u

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'

analyzer = sc.markerr.ErrorAnalyzer(consider_thousand_as_digit=False,
                                    digit_mapping=dict(F=2, T=3, L=4, K=5, B=6, P=7, A=8, S=9, X=0, x=0),
                                    in_col_names=dict(block=None, nwords=None), subj_id_in_xls=False)

analyzer.run_for_worksheets(base_dir+'raw/SC20220512.xlsx', worksheets=['SC{}'.format(i) for i in range(3, 19) if i != 4], out_dir=base_dir)
