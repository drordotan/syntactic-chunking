
import math
import re
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter

#---------------------------------------------------------------------------
def plot_cond_means(df, dependent_var, out_fn, ymax=None, dy=0.1, fig_size=None, cond_names=None):
    """
    Plot the mean value for each condition
    """

    conditions = sorted(df.Condition.unique())
    n_conds = len(conditions)

    if cond_names is None:
        cond_names = {c: c for c in conditions}
    else:
        assert len(cond_names) == n_conds, 'Invalid cond_names: got {} condition names, expecting {}'.format(len(cond_names), n_conds)

    cond_means = [df[df.Condition == cond][dependent_var].mean() for cond in conditions]

    fig = plt.figure(figsize=fig_size)

    plt.bar(range(n_conds), cond_means, color='grey', zorder=10)

    ax = plt.gca()

    _format_conds_graph(ax, cond_names, conditions, dy, n_conds, ymax, font_size=None)

    plt.savefig(out_fn)
    plt.close(fig)


#---------------------------------------------------------------------------
def _format_conds_graph(ax, cond_names, conditions, dy, n_conds, ymax, font_size, x_labels=True):

    if ymax is None:
        ymax = plt.ylim()[1]
    else:
        plt.ylim([0, ymax])

    if x_labels:
        ax.set_xticks(range(n_conds))
        ax.set_xticklabels([cond_names[c] for c in conditions], fontsize=font_size)
    else:
        ax.set_xticks([])

    y_ticks = np.arange(0, ymax+.0001, dy)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(['{:.0f}%'.format(y*100) for y in y_ticks], fontsize=font_size)

    ax.grid(axis='y', color=[0.9]*3, linewidth=0.5, zorder=0)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params('x', length=0, width=0)
    ax.tick_params('y', length=0, width=0)


#---------------------------------------------------------------------------
def plot_2cond_means_per_subject(df, dependent_var, out_fn, ymax=None, dy=0.1, fig_size=None, cond_names=None, font_size=8):
    """
    Plot the mean value for each condition - separate plot per subject
    """

    conds = sorted(df.Condition.unique())
    assert len(conds) == 2
    subj_ids = sorted(df.Subject.unique())
    n_subjs = len(subj_ids)

    subj_inf = _get_2cond_info_per_subject(conds, dependent_var, df, subj_ids)

    fig = plt.figure(figsize=fig_size)

    x0 = np.array(range(n_subjs)) * 3
    plt.bar(x0, [i['c1'] for i in subj_inf], color=[0.3] * 3, zorder=10)
    plt.bar(x0 + 1, [i['c2'] for i in subj_inf], color=[0.6] * 3, zorder=10)

    ax = plt.gca()

    _format_conds_graph(ax, cond_names, conds, dy, 2, ymax, font_size=font_size, x_labels=False)

    ax.set_xticks(x0 + 0.5)
    ax.set_xticklabels([clean_subj_id(i['subject']) for i in subj_inf], fontsize=font_size)

    plt.legend([cond_names[c] for c in conds], fontsize=font_size)

    plt.savefig(out_fn)
    plt.close(fig)


#---------------------------------------------------------------------------
def _get_2cond_info_per_subject(conds, dependent_var, df, subj_ids):

    subj_inf = []
    for subj in subj_ids:
        i = dict(subject=subj,
                 c1=df[(df.Condition == conds[0]) & (df.Subject == subj)][dependent_var].mean(),
                 c2=df[(df.Condition == conds[1]) & (df.Subject == subj)][dependent_var].mean())
        i['delta'] = i['c2'] - i['c1']
        subj_inf.append(i)

    subj_inf.sort(key=itemgetter('delta'), reverse=True)

    return subj_inf


#---------------------------------------------------------------------------
def plot_cond_means_per_subject(df, dependent_var, out_fn, ymax=None, dy=0.1, fig_size=None, cond_names=None, subj_grouping=None,
                                n_cols=2, colors=('#496C51', '#6C9C76', '#A3E0B0', '#C7FAD2'), font_size=8):
    """
    Plot the mean value for each condition - separate plot per subject
    """

    conditions = sorted(df.Condition.unique())
    n_conds = len(conditions)
    subj_ids = sorted(df.Subject.unique())

    #-- Group subject arbitrarily
    if subj_grouping is None:
        subj_grouping = [subj_ids[i:i+3] for i in range(0, len(subj_ids), 3)]
    n_rows = math.ceil(len(subj_grouping) / n_cols)

    if cond_names is None:
        cond_names = {c: c for c in conditions}
    else:
        assert len(cond_names) == n_conds, 'Invalid cond_names: got {} condition names, expecting {}'.format(len(cond_names), n_conds)

    plt.figure(figsize=fig_size)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=fig_size)
    fig.subplots_adjust(hspace=.8, wspace=0.3)
    axes = np.reshape(axes, [n_rows * n_cols])

    for i_group, curr_group_subj_ids in enumerate(subj_grouping):
        plot_subject_group(df, dependent_var, curr_group_subj_ids, conditions, cond_names, ax=axes[i_group],
                           ymax=ymax, dy=dy, colors=colors, font_size=font_size)

    for i in range(len(subj_grouping), n_cols * n_rows):
        axes[i].axis('off')

    plt.savefig(out_fn)
    plt.close(fig)


#---------------------------------------------------------------------------
def plot_subject_group(df, dependent_var, subj_ids, conditions, cond_names, ax, ymax, dy, colors, font_size):

    for i_subj, subj in enumerate(subj_ids):
        subj_df = df[df.Subject == subj]
        cond_means = [subj_df[subj_df.Condition == cond][dependent_var].mean() for cond in conditions]

        ax.plot(range(len(conditions)), cond_means, color=colors[i_subj], zorder=10, linewidth=0.5, marker='o')

    _format_conds_graph(ax, cond_names, conditions, dy, len(conditions), ymax, font_size)
    ax.legend([clean_subj_id(s) for s in subj_ids], fontsize=5)


#---------------------------------------------------------------------------
def clean_subj_id(full_subj_id):
    m = re.match('^(\\d+)([A-Z]+)$', full_subj_id)
    if m is None:
        return full_subj_id
    else:
        return int(m.group(1))

