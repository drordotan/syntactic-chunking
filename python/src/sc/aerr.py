
import openpyxl
import re

import sc.utils as u

lexical_classes = 'unit', 'decade', 'hundred', 'unit', 'decade', 'hundred'
thousands_word = ('thousand', None)

xls_copy_cols = 'Block', 'Condition', 'ItemNum', 'target', 'response', 'NWordsPerTarget'
xls_cols = ('Subject', ) + xls_copy_cols + ('NMissingWords', 'NMissingDigits', 'NMissingClasses')
xls_out_cols = ('Subject', ) + xls_copy_cols + ('NMissingWords', 'PMissingWords', 'NMissingDigits', 'PMissingDigits', 'NMissingClasses', 'PMissingClasses')

xls_optional_cols = 'manual', 'WordOrder'


#------------------------------------------------------
def analyze_errors(in_fn, out_fn):

    in_ws, col_inds = _open_input_file(in_fn)
    out_wb, out_ws = create_output_workbook()

    ok = True
    for rownum in range(2, in_ws.max_row+1):
        ok = parse_row(in_ws, out_ws, rownum, col_inds) and ok

    if not ok:
        print('Some errors were encountered. Set 1 in the "manual" column to override automatic error encoding.')

    out_ws.freeze_panes = out_ws['A2']
    auto_col_width(out_ws)
    out_wb.save(out_fn)


#------------------------------------------------------
def parse_row(in_ws, out_ws, rownum, col_inds):
    """
    Parse a single row, copy it to the output file
    Return True if processed OK.

    If the value in the "manual" column is 1, don't do anything - just copy the error rates from the corresponding columns
    """

    out_ws.cell(rownum, xls_out_cols.index('Subject')+1).value = u.clean_subj_id(in_ws.cell(rownum, col_inds['Subject']).value)

    for colname in xls_copy_cols:
        out_ws.cell(rownum, xls_out_cols.index(colname) + 1).value = in_ws.cell(rownum, col_inds[colname]).value

    if 'manual' in col_inds and in_ws.cell(rownum, col_inds['manual']).value in (1, '1'):

        n_word_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingWords']).value)
        if 'WordOrder' in col_inds:
            n_word_errs -= _nullto0(in_ws.cell(rownum, col_inds['WordOrder']).value)

        n_digit_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingDigits']).value)
        n_class_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingClasses']).value)

    else:

        target_segments = parse_target(in_ws.cell(rownum, col_inds['target']).value, rownum)
        response_segments = parse_response(in_ws.cell(rownum, col_inds['response']).value, rownum, target_segments)
        if target_segments is None or response_segments is None:
            return False

        target = collapse_segments(target_segments)
        response = collapse_segments(response_segments)

        n_word_errs = n_missing_target_items(target, response)
        n_digit_errs = n_missing_target_items([t[1] for t in target], [r[1] for r in response])
        n_class_errs = _n_missing_classes(target, response)

    out_ws.cell(rownum, 1 + xls_out_cols.index('NMissingWords')).value = n_word_errs
    out_ws.cell(rownum, 1 + xls_out_cols.index('NMissingDigits')).value = n_digit_errs
    out_ws.cell(rownum, 1 + xls_out_cols.index('NMissingClasses')).value = n_class_errs

    n_target_words = in_ws.cell(rownum, col_inds['NWordsPerTarget']).value
    out_ws.cell(rownum, 1 + xls_out_cols.index('PMissingWords')).value = n_word_errs / n_target_words
    out_ws.cell(rownum, 1 + xls_out_cols.index('PMissingDigits')).value = n_digit_errs / n_target_words
    out_ws.cell(rownum, 1 + xls_out_cols.index('PMissingClasses')).value = n_class_errs / n_target_words

    return True


def _nullto0(v):
    if v is None or v == '':
        return 0
    else:
        return v

#------------------------------------------------------
def _n_missing_classes(target, response):
    target = [t if t == 'thousand' else t[0] for t in target]
    response = [r if r == 'thousand' else r[0] for r in response]

    for r in response:
        if r in target:
            target.remove(r)

    return len(target)

#------------------------------------------------------
def n_missing_target_items(target_items, response_items):
    # No. of target items that are not in the response

    tmp = list(target_items)
    for r in response_items:
        if r in tmp:
            tmp.remove(r)

    return len(tmp)


#------------------------------------------------------
def parse_response(response_str, rownum, target_segments):

    if response_str == '+':
        return target_segments

    if response_str == '-':
        return []

    response_segments = parse_target(response_str, rownum)
    if response_segments is None:
        return None

    #-- swap "+" with the corresponding target value
    for i, r in enumerate(response_segments):
        if r == ['correct']:
            if len(response_segments) != len(target_segments):
                print('WARNING: "+" is ambiguous because the target and response have different number of segments. ' +
                      'Line {} ignored'.format(rownum))
                return None

            #-- double validation -- in case we have order mismatch
            if target_segments[i] in response_segments:
                print('WARNING: "+" is ambiguous because the target and response have different order of segments. ' +
                      'Line {} ignored'.format(rownum))
                return None

            response_segments[i] = target_segments[i]

    return response_segments


#------------------------------------------------------
def collapse_segments(parsed_segments):
    return [x for pn in parsed_segments for x in pn]


#------------------------------------------------------
def parse_target(target, rownum):
    """
    Return a list of segments, each of which is a list of words

    :param target:
    :param rownum:
    :return:
    """

    if isinstance(target, float):
        target = "{:.0f}".format(target)
    elif isinstance(target, int):
        target = "{:}".format(target)

    segments = [e.strip() for e in target.split('/')]

    parsed_segments = []
    for seg in segments:
        m = re.match('^([0-9,]+)\\s*t\\s*([0-9,]+)?$', seg)
        if m is None:
            parsed_segment = parse_segment_into_word_list(seg),
        else:
            parsed_segment = [parse_segment_into_word_list(m.group(1)), parse_segment_into_word_list('t')]
            if m.group(2) is not None:
                parsed_segments.append(parse_segment_into_word_list(m.group(2)))

        if None in parsed_segment:  # invalid format
            print('WARNING: unsupported target/response format: "{}" -- line {} ignored'.format(target, rownum))
            return None

        parsed_segments.append([e for seg in parsed_segment for e in seg])

    return parsed_segments


#------------------------------------------------------
def parse_segment_into_word_list(n):
    """
    Parse a number into a series of words
    """

    if n == 't' or n == '1000':
        return ['thousand']

    if n == '+':
        return ['correct']

    if n == '-':
        return []

    n = n.replace(',', '')  # delete commas

    if re.match('^\\d+$', n) is None:
        return None

    ndigits = len(n)

    result = []
    for i in range(0, ndigits):
        digit = int(n[-(i+1)])
        if ndigits == 4 and i == 3:
            if digit == 1:
                result.append('thousand')
            else:
                result.append(('thousand', digit))
        elif digit != 0:
            result.append((lexical_classes[i], digit))

    return result[::-1]


#------------------------------------------------------
def _open_input_file(filename):
    wb = openpyxl.load_workbook(filename)
    ws = wb.get_sheet_by_name('data')

    col_inds = _xls_structure(ws)

    return ws, col_inds


def _xls_structure(ws):
    result = {}
    for i in range(1, ws.max_column+1):
        col_name = ws.cell(1, i).value
        if col_name in xls_cols + xls_optional_cols:
            result[col_name] = i

    missing_cols = [c for c in xls_cols if c not in result]
    if len(missing_cols) > 0:
        raise Exception('Invalid file format: columns {} are missing'.format(",".join(missing_cols)))

    return result


#------------------------------------------------------
def create_output_workbook():

    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]

    for i_col, colname in enumerate(xls_out_cols):
        ws.cell(1, i_col+1).value = colname

    return wb, ws

#------------------------------------------------------
def auto_col_width(ws):
    for col in ws.columns:
        max_length = 0
        for cell in col:
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass

        ws.column_dimensions[col[0].column_letter].width = max_length
