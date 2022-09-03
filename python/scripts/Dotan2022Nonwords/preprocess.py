import sc
import pandas as pd
import mtl.stats as ms
import re

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'
recalc_exclusions = False


#-----------------------------------------------------------------------------------------------------------------------
def load_participant_conditions(filename, load_excluded):
    df = pd.read_excel(filename)
    df = df[df.exclude != 'force']

    if not load_excluded:
        df = df[df.exclude != 'exclude']

    cond_order = list(df['Blocked order'])
    return dict(subjid=list(df['Subject']), cond_order=cond_order,
                orderA=[co.index('A') + 1 for co in cond_order],
                orderB=[co.index('B')+1 for co in cond_order],
                orderC=[co.index('C')+1 for co in cond_order])


#-----------------------------------------------------------------------------------------------------------------------
def exclude_outliers(df):
    subj_sum = df.groupby('Subject').mean()

    subj_sum[['phonol_error', 'PMissingMorphemes', 'PMissingDigits', 'PMissingClasses']].to_excel(base_dir+'mean_per_subj.xlsx')

    phon_outlier = ms.outlier(subj_sum.phonol_error)
    phon_outlier_ids = [sid for sid, o in zip(subj_sum.index, phon_outlier) if o]
    print('{} participants are outliers due to phonological errors: {}'.format(sum(phon_outlier), ', '.join(phon_outlier_ids)))

    [print('{:.1f}%'.format(a*100)) for a in sorted(subj_sum.phonol_error)]

    morph_outlier = ms.outlier(subj_sum.PMissingMorphemes)
    morph_outlier_ids = [sid for sid, o in zip(subj_sum.index, morph_outlier) if o]
    print('{} participants are outliers due to morpheme errors: {}'.format(sum(morph_outlier), ', '.join(morph_outlier_ids)))

    outlier_subj_ids = set(phon_outlier_ids+morph_outlier_ids)
    df = df[~df.Subject.isin(outlier_subj_ids)]
    print('{} outliers were removed, {} participants remained'.format(len(outlier_subj_ids), len(df.Subject.unique())))

    return df


#-----------------------------------------------------------------------------------------------------------------------
def exclude_subjects_with_too_many_excluded_trials(df, max_n_excluded_trials=5, max_n_excluded_trials_per_cond=3):

    df = df.copy()
    df['exclude'] = df.manual.str.lower() == 'repeated'
    subj_sum = df.groupby('Subject').sum()

    n_excluded = {sid: n for sid, n in zip(subj_sum.index, subj_sum.exclude)}
    print('Total no. of trials excluded: {}'.format(sum(n_excluded.values())))

    excluded_subject_ids = [sid for sid, n in n_excluded.items() if n > max_n_excluded_trials]
    print('{} participant/s ({}) excluded for having more than {} excluded trials'
          .format(len(excluded_subject_ids), excluded_subject_ids, max_n_excluded_trials))

    df = df[~df.Subject.isin(excluded_subject_ids)]

    subj_sum = df.groupby(['Subject', 'Condition']).sum()
    n_excluded = {(sid, cond): n for (sid, cond), n in zip(subj_sum.index, subj_sum.exclude)}
    excluded_subject_ids = {sid for (sid, cond), n in n_excluded.items() if n > max_n_excluded_trials_per_cond}
    print('{} participant/s ({}) excluded for having more than {} excluded trials in one condition'
          .format(len(excluded_subject_ids), excluded_subject_ids, max_n_excluded_trials_per_cond))

    df = df[~df.Subject.isin(excluded_subject_ids)]

    return df


#-----------------------------------------------------------------------------------------------------------------------
def add_fields(data_fn):
    df = pd.read_excel(data_fn)
    df['block'] = [order.index(cond)+1 for order, cond in zip(df.cond_order, df.Condition)]
    df['phonol_error'] = df.NPhonologicalErrors > 0
    df.to_excel(data_fn, index=False)
    return df


#-----------------------------------------------------------------------------------------------------------------------
def subj_id_mapping(df):
    result = {}
    for subject in df.Subject.unique():
        m = re.match('^SC(\\d+$)', subject)
        if m is None:
            print('ERROR: Invalid subject ID format ({}) - not changed')
            result[subject] = subject
        else:
            result[subject] = int(m.group(1))

    return result

#-----------------------------------------------------------------------------------------------------------------------

cond_order_info = load_participant_conditions(base_dir + 'participants & conditions.xlsx', load_excluded=recalc_exclusions)

print('Loading data of {} subjects...'.format(len(cond_order_info['subjid'])))

analyzer = sc.markerr.ErrorAnalyzer(consider_thousand_as_digit=False,
                                    digit_mapping=dict(F=2, T=3, L=4, K=5, B=6, P=7, A=8, S=9, X=0, x=0),
                                    in_col_names=dict(block=None, nwords=None), subj_id_in_xls=False,
                                    phonological_error_flds=('phonerr - >1 feature', 'more than 1 phonerr'),
                                    set_per_subject=cond_order_info)

analyzer.run_for_worksheets(base_dir+'raw-data.xlsx', out_dir=base_dir, worksheets=cond_order_info['subjid'])

all_data = add_fields(base_dir+'data_coded.xlsx')

if recalc_exclusions:
    all_data = exclude_subjects_with_too_many_excluded_trials(all_data)
    all_data = exclude_outliers(all_data)

subj_id = subj_id_mapping(all_data)
all_data.Subject = [subj_id[s] for s in all_data.Subject]

all_data.to_excel(base_dir+'data_clean.xlsx', index=False)
all_data.to_csv(base_dir+'data_clean.csv', index=False)
