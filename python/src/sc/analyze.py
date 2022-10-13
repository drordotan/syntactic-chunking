from operator import itemgetter
import numpy as np
from collections import namedtuple
import scipy.stats
import scipy.signal
import pandas as pd

import mtl.utils as mu

TTestResult = namedtuple('TTestResult', ['subj', 't', 'p'])


#---------------------------------------------------------------------------
def exp1_auto_group_subjects(df, dependent_var):
    """
    Group subjects according to their results pattern across the 4 conditions in Experiment 1
    """

    conditions = sorted(df.Condition.unique())
    subj_ids = sorted(df.Subject.unique())

    subjtypes = [subj_pattern(df[df.Subject == subj], conditions, dependent_var) for subj in subj_ids]

    sinf = sorted([(pat, i) for i, pat in zip(subj_ids, subjtypes)])
    for pat, i in sinf:
        print('{}: {}'.format(i, pat))


#---------------------------------------------------------------------------
def subj_pattern(subj_df, conditions, dependent_var):
    mean_per_cond = np.array([subj_df[subj_df.Condition == cond][dependent_var].mean() for cond in conditions])
    dmeans = mean_per_cond[1:] - mean_per_cond[:-1]
    msign = [1 if m >= 0 else -1 for m in dmeans]
    return tuple(msign)


#---------------------------------------------------------------------------
def compare_conds_per_item(df, cond1, cond2, dependent_var):
    """
    Compare two conditions with respect to the number of specific items that are bettern in condition 1 than in condition 2
    or vice-versa.
    """

    cond1_results = _get_success_per_item(df[df.Condition == cond1], dependent_var)
    cond2_results = _get_success_per_item(df[df.Condition == cond2], dependent_var)

    keys = set(cond1_results.keys()).intersection(set(cond2_results.keys()))
    n_cond1_gt_cond2 = sum([cond1_results[k] > cond2_results[k] for k in keys])
    n_cond1_eq_cond2 = sum([cond1_results[k] == cond2_results[k] for k in keys])
    n_cond2_gt_cond1 = len(keys) - n_cond1_eq_cond2 - n_cond1_gt_cond2
    print('Comparing {} between condition {} and {}:'.format(dependent_var, cond1, cond2))
    print('   Higher in {}: {}/{} ({:.1f}%) items'.format(cond1, n_cond1_gt_cond2, len(keys), n_cond1_gt_cond2 / len(keys) * 100))
    print('   Higher in {}: {}/{} ({:.1f}%) items'.format(cond2, n_cond2_gt_cond1, len(keys), n_cond2_gt_cond1 / len(keys) * 100))
    print('   Same: {}/{} ({:.1f}%) items'.format(n_cond1_eq_cond2, len(keys), n_cond1_eq_cond2 / len(keys) * 100))


#---------------------------------------------------------------------------
def compare_conds_per_subj(df, cond_good, cond_bad, dependent_var):
    """
    Compare the performance between 2 conditions, separately for each subject

    :param df:
    :param cond_good: The condition in which better performance is expected
    :param cond_bad: The condition in which worse performance is expected
    :param dependent_var:
    """

    t_and_p = []

    subj_ids = sorted(df.Subject.unique())
    for subj in subj_ids:
        sdf1 = df[(df.Subject == subj) & (df.Condition == cond_good)].sort_values('ItemNum')
        sdf2 = df[(df.Subject == subj) & (df.Condition == cond_bad)].sort_values('ItemNum')
        assert list(sdf1.ItemNum) == list(sdf2.ItemNum)

        if sdf1[dependent_var].mean() < sdf2[dependent_var].mean():
            t, p = scipy.stats.ttest_rel(sdf1[dependent_var], sdf2[dependent_var])
            p = p / 2
        else:
            t = None
            p = 1

        nrows = sdf1.shape[0]
        t_and_p.append((t, p / 2, nrows, subj))

    t_and_p.sort(key=itemgetter(1))

    min_t = None
    corrected_ps = []

    div_by = len(subj_ids)
    for t, p, n, subj in t_and_p:
        if t is None:
            print('Subject {}: Opposite to prediction'.format(subj))

        else:
            corrected_p = p * div_by
            corrected_ps.append(corrected_p)

            print('Subject {}: t({}) = {:.2f}, p = {}, corrected p = {}'.format(subj, n-1, t, mu.p_str(p), mu.p_str(corrected_p)))

            if min_t is None or t < min_t:
                min_t = t

        div_by -= 1

    print('Overall: t > {:.2f}'.format(min_t))
    print('Sorted corrected p: {}'.format([mu.p_str(p) for p in sorted(corrected_ps, reverse=True)]))


#---------------------------------------------------------------------------
def _get_success_per_item(df, dependent_var):
    return {(subj, item): succ for subj, item, succ in zip(df.Subject, df.ItemNum, df[dependent_var])}


#---------------------------------------------------------------------------
def compare_effect_size(dependent_var, df1, df2, conds1=None, conds2=None, expnames=('A', 'B')):
    """
    Compare the effect size between two experiments.
    The effect size is defined, per subject, as delta-accuracy between two conditions.
    The per-subject values are compared with unpaired t-test

    :param df1: Data of experiment 1
    :param conds1: Condition names for experiment 1
    :param df2: Data of experiment 2
    :param conds2: Condition names for experiment 2
    """

    if conds1 is None:
        conds1 = sorted(set(df1.Condition))

    if conds2 is None:
        conds2 = sorted(set(df2.Condition))

    assert len(conds1) == 2
    assert len(conds2) == 2
    assert len(expnames) == 2

    effect_sizes_1 = _get_effect_size(df1, conds1, dependent_var)
    effect_sizes_2 = _get_effect_size(df2, conds2, dependent_var)

    t, p = scipy.stats.ttest_ind(effect_sizes_1, effect_sizes_2)
    print('Effect size of {} in experiment {} = {:.2f}%, in experiment {} = {:.2f}%;'.
          format(dependent_var, expnames[0], np.mean(effect_sizes_1) * 100, expnames[1], np.mean(effect_sizes_2) * 100), end='')
    if np.mean(effect_sizes_1) > np.mean(effect_sizes_2):
        print(' unpaired t({}) = {:.3f}, one-tailed p={}'.format(len(effect_sizes_1) + len(effect_sizes_2) - 2, t, mu.p_str(p/2)))
    else:
        print('opposite to predicted direction')

    print('No. of participants in the predicted direction: {} in experiment {}, {} in experiment {}'.
          format(sum(np.array(effect_sizes_1) >= 0), expnames[0], sum(np.array(effect_sizes_2) >= 0), expnames[1]))


def _get_effect_size(df, conds, dependent_var):
    subjects = sorted(set(df.Subject))
    means1 = df[df.Condition == conds[0]].groupby('Subject')[dependent_var].aggregate(np.mean)
    means2 = df[df.Condition == conds[1]].groupby('Subject')[dependent_var].aggregate(np.mean)

    return [means2[s] - means1[s] for s in subjects]


#---------------------------------------------------------------------------
def get_value_per_subj_and_cond(conds, dependent_var, df, subj_ids, sort_by_delta=False):
    """
    Get the value of the dependent variable in each condition for each subject

    Returns a list with one dict per subject. The dict entries are cNNN:VVV, where NNN is the condition number (1, 2, ...) and VVV is
    the dependent variable average value in that condition.
    The dict also contains a 'delta' key, whose value is the difference between the last and first conditions.
    """

    subj_inf = []
    for subj in subj_ids:
        i = dict(subject=subj)
        for condnum in range(len(conds)):
            i['c{}'.format(condnum+1)] = df[(df.Condition == conds[condnum]) & (df.Subject == subj)][dependent_var].mean()
        i['delta'] = i['c{}'.format(len(conds))] - i['c1']
        subj_inf.append(i)

    if sort_by_delta:
        subj_inf.sort(key=itemgetter('delta'), reverse=True)

    return subj_inf


#---------------------------------------------------------------------------
def correlate_sc_effect_vs_reading_errors(df, dependent_var, reading_filename):

    read_df = pd.read_excel(reading_filename)

    subj_ids = sorted(set(df.Subject.unique()).intersection(set(read_df.subject)))

    sc_effect = get_value_per_subj_and_cond(('A', 'B'), dependent_var, df, subj_ids)
    sc_effect = [s['delta'] for s in sc_effect]

    reading_errors = [float(read_df.syntactic_errors[read_df.subject == s] / read_df.n_items[read_df.subject == s]) for s in subj_ids]

    r, p = scipy.stats.pearsonr(sc_effect, reading_errors)
    if r > 0:
        print('The correlation between syntactic chunking effect size and the rate of syntactic errors in reading: r={:.3f}, p={}'.format(r, mu.p_str(p/2)))
