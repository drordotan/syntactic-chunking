
import numpy as np

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


def subj_pattern(subj_df, conditions, dependent_var):
    mean_per_cond = np.array([subj_df[subj_df.Condition == cond][dependent_var].mean() for cond in conditions])
    dmeans = mean_per_cond[1:] - mean_per_cond[:-1]
    msign = [1 if m >= 0 else -1 for m in dmeans]
    return tuple(msign)


#---------------------------------------------------------------------------
