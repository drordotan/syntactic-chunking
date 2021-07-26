
import numpy as np
from collections import namedtuple
import scipy.stats

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
        print(' t({}) = {:.3f}, one-tailed p={}'.format(len(effect_sizes_1) + len(effect_sizes_2) - 2, t, mu.p_str(p/2)))
    else:
        print('opposite to predicted direction')


def _get_effect_size(df, conds, dependent_var):
    subjects = sorted(set(df.Subject))
    means1 = df[df.Condition == conds[0]].groupby('Subject')[dependent_var].aggregate(np.mean)
    means2 = df[df.Condition == conds[1]].groupby('Subject')[dependent_var].aggregate(np.mean)

    return [means2[s] - means1[s] for s in subjects]
