import re


#---------------------------------------------------------------------------
def clean_subj_id(full_subj_id):
    m = re.match('^(\\d+)([A-Z]+)$', full_subj_id)
    if m is None:
        return full_subj_id
    else:
        return int(m.group(1))
