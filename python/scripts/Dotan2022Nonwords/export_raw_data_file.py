import pandas as pd

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'


def split_target_to_segments(target, cond):
    if cond == 'A':
        return target
    elif cond == 'B':
        return target[2:] + ' / ' + target[:2] + '00'
    elif cond == 'C':
        return '{} / {}0 / {}00 / {}000'.format(target[3], target[2], target[1], target[0])
    else:
        raise ValueError('Invalid condition: {}'.format(cond))



df = pd.read_excel(base_dir + 'data_clean.xlsx')

df['verbal target'] = [split_target_to_segments(t, c) for t, c in zip(df.target, df.Condition)]

df.phonol_error = df.phonol_error.map({True: 1, False: 0})

df = df[['Subject', 'Condition', 'block', 'ItemNum', 'target', 'verbal target', 'response', 'verbal response',
         'NMissingWords', 'PMissingWords', 'NMissingDigits', 'PMissingDigits', 'NMissingClasses', 'PMissingClasses', 'PMissingMorphemes',
         'NPhonologicalErrors', 'cond_order', 'orderA', 'orderB', 'orderC', 'phonol_error']]

df.to_csv(base_dir + 'data_supp_mat.csv')
