import sc
import pandas as pd

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'


#-----------------------------------------------------------------------------------------------------------------------


def load_participant_conditions(filename):
    df = pd.read_excel(filename)
    df = df[df.exclude != 'exclude']
    cond_order = list(df['Blocked order'])
    return dict(subjid=list(df['Subject']), cond_order=cond_order,
                orderA=[co.index('A') + 1 for co in cond_order],
                orderB=[co.index('B')+1 for co in cond_order],
                orderC=[co.index('C')+1 for co in cond_order])


#-----------------------------------------------------------------------------------------------------------------------

cond_order_info = load_participant_conditions(base_dir + 'participants & conditions.xlsx')

print('Loading data of {} subjects...'.format(len(cond_order_info['subjid'])))

analyzer = sc.markerr.ErrorAnalyzer(consider_thousand_as_digit=False,
                                    digit_mapping=dict(F=2, T=3, L=4, K=5, B=6, P=7, A=8, S=9, X=0, x=0),
                                    in_col_names=dict(block=None, nwords=None), subj_id_in_xls=False,
                                    phonological_error_flds=('phonerr - >1 feature', 'more than 1 phonerr'),
                                    set_per_subject=cond_order_info)

analyzer.run_for_worksheets(base_dir+'raw-data.xlsx', out_dir=base_dir,
                            worksheets=cond_order_info['subjid'])


#-- Add some fields

out_fn = base_dir + 'data_coded.xlsx'
df = pd.read_excel(out_fn)

df['block'] = [order.index(cond) + 1 for order, cond in zip(df.cond_order, df.Condition)]
df['phonol_error'] = df.NPhonologicalErrors > 0

df.to_excel(out_fn, index=False)
