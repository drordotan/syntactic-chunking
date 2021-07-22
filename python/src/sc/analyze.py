
import numpy as np
from collections import namedtuple


TTestResult = namedtuple('TTestResult', ['subj', 't', 'p'])

#---------------------------------------------------------------------------
def exp1_auto_group_subjects(df, dependent_var):
    """
    Group subjects according to their results pattern across the 4 conditions
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
