
import math
import numpy as np
import matplotlib.pyplot as plt
import sc.utils


#---------------------------------------------------------------------------
from sc.analyze import get_value_per_subj_and_cond

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

    _format_conds_graph(ax, conditions, dy, n_conds, ymax, font_size=None, cond_names=cond_names)

    plt.savefig(out_fn)
    plt.close(fig)


#---------------------------------------------------------------------------
def plot_cond_means_multiple_measures(df, dependent_vars, out_fn, ymax, d_y_ticks, fig_size, cond_names, conditions=None, dependent_var_names=None,
                                      cond_comparison_text=None, colors=None, font_size=None, show_legend=True):
    """
    Plot the mean value for each condition - multiple measures

    :param df:
    :param dependent_vars: List of variables to plot (columns in df)
    :param out_fn: Output pdf/png file name
    :param ymax: Maximal y axis value
    :param d_y_ticks: Delta between y ticks
    :param fig_size: (width, height)
    :param cond_names: Name of each condition (for legend)
    :param conditions: List of conditions to compare
    :param dependent_var_names: Names of each dependent variable (for x axis)
    :param cond_comparison_text: List of lists - one list for each dependent variable.
                    The inner list contains #conditions-1 texts to print as significance-comparison between adjacent conditions.
    :param colors: List of bar colors - one per condition
    :param font_size:
    """

    if conditions is None:
        conditions = sorted(df.Condition.unique())
    elif sorted(conditions) != sorted(df.Condition.unique()):
        print("Warning: conditions are not identical with what's available in the data")

    n_conds = len(conditions)
    if colors is None:
        colors = ['grey'] * n_conds

    if cond_names is None:
        cond_names = {c: c for c in conditions}
    else:
        assert len(cond_names) == n_conds, 'Invalid cond_names: got {} condition names, expecting {}'.format(len(cond_names), n_conds)

    if dependent_var_names is None:
        dependent_var_names = dependent_vars

    # -- Get data
    mean_per_var_and_cond = {}
    for dependent_var in dependent_vars:
        for i_cond, cond in enumerate(conditions):
            mean_per_var_and_cond[(dependent_var, cond)] = df[df.Condition == cond][dependent_var].mean()

    #-- Plot!

    fig = plt.figure(figsize=fig_size)

    for i_cond, cond in enumerate(conditions):
        # mean_per_dv = [df[df.Condition == cond][dependent_var].mean() for dependent_var in dependent_vars]
        mean_per_dv = [mean_per_var_and_cond[(dependent_var, cond)] for dependent_var in dependent_vars]
        x = [i_dv*(n_conds+1) + i_cond for i_dv in range(len(dependent_vars))]
        plt.bar(x, mean_per_dv, color=colors[i_cond], zorder=10)

    ax = plt.gca()

    _format_conds_graph(ax, conditions, d_y_ticks, n_conds, ymax, font_size=font_size, x_labels=False, visible_y_labels=2)
    ax.set_xticks([i_dv*(n_conds+1) + ((n_conds+1) / 2 - 1) for i_dv in range(len(dependent_vars))])
    ax.set_xticklabels(dependent_var_names, fontsize=font_size)
    ax.set_ylabel('Error rate', fontsize=font_size)

    if cond_comparison_text is not None:
        cmp_lines_x_offset = 0.1
        assert len(cond_comparison_text) == len(dependent_vars), "cond_comparison_text must be a list with {} lists".format(len(dependent_vars))
        for i_dv, cct in enumerate(cond_comparison_text):
            assert not isinstance(cct, str), "cond_comparison_text must be a list of {} lists".format(len(dependent_vars))
            assert len(cct) == n_conds - 1, "cond_comparison_text[{}] has {} elements, expecting {}".format(i_dv, len(cct), n_conds)

            for i_cond in range(n_conds - 1):
                x_bar1 = i_dv * (n_conds+1) + i_cond
                x1 = x_bar1 + cmp_lines_x_offset
                x2 = x_bar1 + 1 - cmp_lines_x_offset
                y1 = mean_per_var_and_cond[(dependent_vars[i_dv], conditions[i_cond])]
                y2 = mean_per_var_and_cond[(dependent_vars[i_dv], conditions[i_cond+1])]
                sc.utils.plot_bar_comparison(ax, x1, x2, y1, y2, 0.02, cct[i_cond], 0.005)

    if show_legend:
        plt.legend([cond_names[c] for c in conditions], fontsize=font_size)

    plt.savefig(out_fn)
    plt.close(fig)

#---------------------------------------------------------------------------
def _format_conds_graph(ax, conditions, dy, n_conds, ymax, font_size, x_labels=True, cond_names=None, visible_y_labels=None):
    """

    :param ax:
    :param conditions:
    :param dy:
    :param n_conds:
    :param ymax:
    :param font_size:
    :param x_labels:
    :param cond_names:
    :param visible_y_labels: If specified (int), show only every nth y label
    """

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
    y_labels = ['{:.0f}%'.format(y*100) for y in y_ticks]
    if visible_y_labels is not None:
        y_labels = [y if i % visible_y_labels == 0 else '' for i, y in enumerate(y_labels)]
    ax.set_yticklabels(y_labels, fontsize=font_size)

    ax.grid(axis='y', color=[0.9]*3, linewidth=0.5, zorder=0)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params('x', length=0, width=0)
    ax.tick_params('y', length=0, width=0)


#---------------------------------------------------------------------------
def plot_2cond_means_per_subject(df, dependent_var, out_fn, ymax=None, dy=0.1, fig_size=None, conds=None, cond_names=None, font_size=8,
                                 get_subj_id_func=str, sort_by_delta=True, colors = (0.3, 0.6, 0.8), legend_loc=None):
    """
    Plot the mean value for each condition - separate plot per subject
    """

    if conds is None:
        conds = sorted(df.Condition.unique())

    n_conds = len(conds)
    if cond_names:
        n_missing = len([c for c in conds if c not in cond_names])
        assert n_missing == 0, 'Invalid cond_names={} (conds={})'.format(cond_names, conds)

    subj_ids = sorted(df.Subject.unique())
    n_subjs = len(subj_ids)

    subj_inf = get_value_per_subj_and_cond(conds, dependent_var, df, subj_ids, sort_by_delta)

    fig = plt.figure(figsize=fig_size)

    x0 = np.array(range(n_subjs)) * (n_conds + 1)
    for condnum in range(n_conds):
        plt.bar(x0 + condnum, [i['c{}'.format(condnum+1)] for i in subj_inf], color=[colors[condnum]] * 3, zorder=10)

    ax = plt.gca()

    _format_conds_graph(ax, conds, dy, n_conds, ymax, font_size=font_size, x_labels=False, cond_names=cond_names)

    ax.set_xticks(x0 + (n_conds-1) / 2)
    ax.set_xticklabels([get_subj_id_func(i['subject']) for i in subj_inf], fontsize=font_size)
    plt.xlabel('Participant', fontsize=font_size)
    plt.ylabel('Error rate', fontsize=font_size)

    if cond_names is not None:
        plt.legend([cond_names[c] for c in conds], fontsize=font_size, loc=legend_loc)

    plt.savefig(out_fn)
    plt.close(fig)


#---------------------------------------------------------------------------
def plot_cond_means_per_subject(df, dependent_var, out_fn, ymax=None, dy=0.1, fig_size=None, cond_names=None, subj_grouping=None,
                                n_cols=2, colors=('#496C51', '#6C9C76', '#A3E0B0', '#C7FAD2'), font_size=8, y_label=None):
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
        if i_group % 2 == 0:
            axes[i_group].set_ylabel(y_label, fontsize=font_size)

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

    _format_conds_graph(ax, conditions, dy, len(conditions), ymax, font_size=font_size, cond_names=cond_names)
    ax.legend([str(s) for s in subj_ids], fontsize=5)

