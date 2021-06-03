
import numpy as np
from collections import namedtuple
from operator import attrgetter
import scipy.stats


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
def compare_conds_per_subject(df, cond1, cond2, dependent_var, alpha=0.05):

    subj_ids = sorted(set(df.Subject.unique()))

    ttest_results = []

    for subj_id in subj_ids:
        subj_df = df[df.Subject == subj_id]
        cond1_data = subj_df[subj_df.Condition == cond1].sort_values(['ItemNum'])
        cond2_data = subj_df[subj_df.Condition == cond2].sort_values(['ItemNum'])

        #-- Take only items that exist in both conditions
        cond1_items = set(cond1_data.ItemNum)
        cond2_items = set(cond2_data.ItemNum)
        common_items = cond1_items.intersection(cond2_items)
        n_items = len(common_items)
        if n_items < 3:
            print('Subject {}: only {} items exist in both conditons {}, {}. Skipping'.format(subj_id, n_items, cond1, cond2))
            continue

        cond1_data = cond1_data[cond1_data.ItemNum.isin(common_items)].reset_index()
        cond2_data = cond2_data[cond2_data.ItemNum.isin(common_items)].reset_index()

        data1 = cond1_data[dependent_var]
        data2 = cond2_data[dependent_var]

        #t, p = scipy.stats.ttest_rel(data1, data2)
        t, p = scipy.stats.wilcoxon(data1, data2)
        print('Subject {}: t({}) = {:.2f}, 1-tail p = {:.5g}'.format(subj_id, n_items-1, t, p/2))
        ttest_results.append(TTestResult(subj_id, t, p))

    ttest_results.sort(key=attrgetter('p'), reverse=True)

    non_significant = []
    for i, r in enumerate(ttest_results):
        threshold = alpha / (len(subj_ids) - i)
        non_significant.append(r.p > threshold)
        print(r.p, threshold, r.p <= threshold)

    sig_data = ['{}({:.4f})'.format(r.subj, r.p) for r, s in zip(ttest_results, non_significant) if s]
    print('{} participants with non-significant effect (alpha={:.3g}): {}'.format(sum(non_significant), alpha, sig_data))
