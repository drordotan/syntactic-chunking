import sc
import sc.utils as u

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/pilots/pilot_3/'

analyzer = sc.markerr.ErrorAnalyzer(consider_thousand_as_digit=False,
                                    digit_mapping=dict(F=2, B=3, L=4, K=5, A=6, P=7, O=8, S=9, X=0, x=0))
analyzer.run(base_dir+'results.xlsx', base_dir+'blocked/', worksheet='blocked')
analyzer.run(base_dir+'results.xlsx', base_dir+'mixed/', worksheet='mixed')
# 