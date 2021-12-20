import re


#---------------------------------------------------------------------------
def clean_subj_id(full_subj_id):
    m = re.match('^(\\d+)([A-Z]+)$', str(full_subj_id))
    if m is None:
        return full_subj_id
    else:
        return int(m.group(1))


#---------------------------------------------------------------------------
def plot_bar_comparison(ax, x0, x1, y0, y1, y_length, text, dy_text, font_size=8, linecolor='grey', linewidth=0.5, textcolor=None):
    """
    Plot lines that compare two bars (2 vertical lines connected by a horizontal line), and text above them

    :param ax: Axes to plot on
    :param x0: X coordinate of vertical line 1 (for bar #1)
    :param x1: X coordinate of vertical line 2 (for bar #2)
    :param y0: Top of bar 1
    :param y1: Top of bar 1
    :param y_length: Length of the shorter vertical line
    :param text: The text to plot
    :param dy_text: The height of the text above the horizontal line
    :param linecolor:
    :param linewidth:
    :param textcolor:
    """
    if y_length > 0:
        h_y = max(y0, y1)+y_length
    else:
        h_y = min(y0, y1)+y_length

    ax.plot([x0, x0], [y0, h_y], color=linecolor, label='_nolegend_', linewidth=linewidth)
    ax.plot([x1, x1], [y1, h_y], color=linecolor, label='_nolegend_', linewidth=linewidth)
    ax.plot([x0, x1], [h_y, h_y], color=linecolor, label='_nolegend_', linewidth=linewidth)

    if textcolor is None:
        ax.text((x0+x1)/2, h_y+dy_text, text, fontsize=font_size, horizontalalignment='center')
    else:
        ax.text((x0+x1)/2, h_y+dy_text, text, fontsize=font_size, horizontalalignment='center', color=textcolor)
