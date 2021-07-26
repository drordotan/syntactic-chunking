"""
Mark errors in the results file
"""
import openpyxl
import re
import pandas as pd
import mtl.verbalnumbers.hebrew as hebnums


one_thousand = hebnums.NumberWord(hebnums.thousands, 1)
decword_thousand = hebnums.NumberWord(hebnums.decword_thousand, None)

xls_copy_cols = 'Block', 'Condition', 'ItemNum', 'target', 'response', 'NWordsPerTarget'
xls_cols = ('Subject', ) + xls_copy_cols + ('NMissingWords', 'NMissingDigits', 'NMissingClasses')
xls_out_cols = ('Subject', ) + xls_copy_cols + \
               ('NTargetDigits', 'NMissingWords', 'PMissingWords', 'NMissingDigits',
                'PMissingDigits', 'NMissingClasses', 'PMissingClasses', 'PMissingMorphemes')

xls_optional_cols = 'manual', 'WordOrder'


#------------------------------------------------------
def analyze_errors(in_fn, out_dir, consider_thousand_as_digit=False, subj_id_transformer=None, accuracy_per_digit=False):
    """
    Analyze the error rates (digit, class, morpheme, word) in each trial

    :param in_fn: Excel file with the raw data (uncoded)
    :param out_dir: Directory for output files
    :param consider_thousand_as_digit:  Whether the word "thousand" should count towards digit errors
    :param use_teens: Consider teens as a separate class
    :param subj_id_transformer: Function for transfoming the subject ID field
    :param accuracy_per_digit: This concerns the output files per word/morpheme: whether to compute the word/digit accuracy
            for each specific word or less precisely. Value=True is impossible if the target contains duplicate digits.
    """

    in_ws, col_inds = _open_input_file(in_fn)
    out_wb, out_ws = create_output_workbook()

    result_per_word = dict(subject=[], block=[], condition=[], itemNum=[], target=[], response=[], nTargetWords=[],
                           wordOK=[], digitOK=[], classOK=[])

    result_per_morpheme = dict(subject=[], block=[], condition=[], itemNum=[], segment_num=[], target=[], response=[],
                               target_segment=[], nTargetWords=[], nTargetDigits=[], nTargetMorphemes=[],
                               morpheme_type=[], correct=[])

    ok = True
    for rownum in range(2, in_ws.max_row+1):
        ok = parse_row(in_ws, out_ws, rownum, col_inds, result_per_word, result_per_morpheme, subj_id_transformer, accuracy_per_digit) and ok

    if not ok:
        print('Some errors were encountered. Set 1 in the "manual" column to override automatic error encoding.')

    out_ws.freeze_panes = out_ws['A2']
    auto_col_width(out_ws)
    out_wb.save(out_dir + '/data_coded.xlsx')
    pd.DataFrame(result_per_word).to_csv(out_dir+'/data_coded_words.csv', index=False)
    pd.DataFrame(result_per_morpheme).to_csv(out_dir+'/data_coded_morphemes.csv', index=False)


#------------------------------------------------------
def parse_row(in_ws, out_ws, rownum, col_inds, result_per_word, result_per_morpheme, subj_id_transformer, per_word):
    """
    Parse a single row, copy it to the output file
    Return True if processed OK.

    If the value in the "manual" column is 1, don't do anything - just copy the error rates from the corresponding columns
    """

    subj_id = in_ws.cell(rownum, col_inds['Subject']).value
    block = in_ws.cell(rownum, col_inds['Block']).value
    cond_name = in_ws.cell(rownum, col_inds['Condition']).value
    item_num = in_ws.cell(rownum, col_inds['ItemNum']).value
    raw_target = in_ws.cell(rownum, col_inds['target']).value
    raw_response = in_ws.cell(rownum, col_inds['response']).value
    n_target_words = in_ws.cell(rownum, col_inds['NWordsPerTarget']).value
    manual_coding = 'manual' in col_inds and in_ws.cell(rownum, col_inds['manual']).value in (1, '1')

    if subj_id is None and raw_target is None:
        print('Warning: row #{} seems empty, ignored'.format(rownum))
        return True

    out_ws.cell(rownum, xls_out_cols.index('Subject')+1).value = subj_id if subj_id_transformer is None else subj_id_transformer(subj_id)

    for colname in xls_copy_cols:
        out_ws.cell(rownum, xls_out_cols.index(colname) + 1).value = in_ws.cell(rownum, col_inds[colname]).value

    target_segments, target, target_digits = analyze_target(raw_target, rownum)
    n_target_digits = len(target_digits)

    if n_target_words != len(target):
        print("Error in line {}: Invalid number of words ({}), expecting {} words".format(rownum, len(target), n_target_words))
        return False

    if manual_coding:

        n_word_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingWords']).value)
        if 'WordOrder' in col_inds:
            n_word_errs -= _nullto0(in_ws.cell(rownum, col_inds['WordOrder']).value)

        n_digit_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingDigits']).value)
        n_class_errs = _nullto0(in_ws.cell(rownum, col_inds['NMissingClasses']).value)
        response_digits = ()

    else:
        n_word_errs, n_class_errs, n_digit_errs, response_digits = analyze_response(raw_response, target, target_segments, target_digits, rownum)

    _save_value(out_ws, rownum, 'NTargetDigits', n_target_digits)
    _save_value(out_ws, rownum, 'NMissingWords', n_word_errs)
    _save_value(out_ws, rownum, 'NMissingDigits', n_digit_errs)
    _save_value(out_ws, rownum, 'NMissingClasses', n_class_errs)
    _save_value(out_ws, rownum, 'PMissingWords', n_word_errs / n_target_words)
    _save_value(out_ws, rownum, 'PMissingDigits', n_digit_errs / n_target_digits)
    _save_value(out_ws, rownum, 'PMissingClasses', n_class_errs / n_target_words)
    _save_value(out_ws, rownum, 'PMissingMorphemes', (n_class_errs + n_digit_errs) / (n_target_words + n_target_digits))

    if manual_coding and per_word:
        print('WARNING: line {} excluded from the per-word analyses because it was coded manually'.format(rownum))
        return True

    for i in range(n_target_words):
        result_per_word['subject'].append(subj_id)
        result_per_word['block'].append(block)
        result_per_word['condition'].append(cond_name)
        result_per_word['itemNum'].append(item_num)
        result_per_word['target'].append(raw_target)
        result_per_word['response'].append(raw_response)
        result_per_word['nTargetWords'].append(n_target_words)
        result_per_word['wordOK'].append(1 if i >= n_word_errs else 0)
        result_per_word['digitOK'].append(1 if i >= n_digit_errs else 0)
        result_per_word['classOK'].append(1 if i >= n_class_errs else 0)

        result_per_morpheme['subject'].append(subj_id)
        result_per_morpheme['block'].append(block)
        result_per_morpheme['condition'].append(cond_name)
        result_per_morpheme['itemNum'].append(item_num)
        result_per_morpheme['segment_num'].append('')
        result_per_morpheme['target'].append(raw_target)
        result_per_morpheme['target_segment'].append('')
        result_per_morpheme['response'].append(raw_response)
        result_per_morpheme['nTargetWords'].append(n_target_words)
        result_per_morpheme['nTargetDigits'].append(n_target_digits)
        result_per_morpheme['nTargetMorphemes'].append(n_target_words + n_target_digits)
        result_per_morpheme['morpheme_type'].append('class')
        result_per_morpheme['correct'].append(1 if i >= n_class_errs else 0)

    for i in range(n_target_digits):
        result_per_morpheme['subject'].append(subj_id)
        result_per_morpheme['block'].append(block)
        result_per_morpheme['condition'].append(cond_name)
        result_per_morpheme['itemNum'].append(item_num)
        result_per_morpheme['segment_num'].append(i+1 if per_word else '')
        result_per_morpheme['target'].append(raw_target)
        result_per_morpheme['target_segment'].append(target_digits[i] if per_word else '')
        result_per_morpheme['response'].append(raw_response)
        result_per_morpheme['nTargetWords'].append(n_target_words)
        result_per_morpheme['nTargetDigits'].append(n_target_digits)
        result_per_morpheme['nTargetMorphemes'].append(n_target_words + n_target_digits)
        result_per_morpheme['morpheme_type'].append('digit')

        if per_word:
            correct = target_digits[i] in response_digits
        else:
            correct = 1 if i >= n_digit_errs else 0

        result_per_morpheme['correct'].append(correct)

    return True


#------------------------
def _nullto0(v):
    if v is None or v == '':
        return 0
    else:
        return v


#------------------------------------------------------
def analyze_target(raw_target, rownum):
    target_segments = parse_target_or_response(raw_target, rownum)
    target = collapse_segments(target_segments)
    target = [decword_thousand if t == one_thousand else t for t in target]

    target_digits = [t.digit for t in target if t.digit is not None][::-1]  # put the ones word in position 1

    return target_segments, target, target_digits


#------------------------------------------------------
def analyze_response(raw_response, target, target_segments, target_digits, rownum):

    response_segments = parse_response(raw_response, rownum, target_segments)
    if target_segments is None or response_segments is None:
        return False

    response = collapse_segments(response_segments)
    response = [decword_thousand if r == one_thousand else r for r in response]

    n_word_errs = n_missing_target_items(target, response)
    n_class_errs = _n_missing_classes(target, response)

    response_digits = [r.digit for r in response if r.digit is not None]
    n_digit_errs = n_missing_target_items(target_digits, response_digits)

    return n_word_errs, n_class_errs, n_digit_errs, response_digits


#------------------------------------------------------
def _save_value(out_ws, rownum, colname, value):
    out_ws.cell(rownum, 1 + xls_out_cols.index(colname)).value = value


#------------------------------------------------------
def _n_missing_classes(target, response):
    target = [t.lexical_class for t in target]
    response = [r.lexical_class for r in response]

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

    if response_str is None:
        return None

    if response_str in ('+', '!'):
        return target_segments

    if response_str == '-':
        return []

    response_str = str(response_str)

    #-- Check if there are optional things
    m = re.match('(.*);(.+)', response_str)
    if m is None:
        response_segments_unknown_loc = []
    else:
        response_str = m.group(1)
        response_segments_unknown_loc = parse_target_or_response(m.group(2), rownum)
        if response_segments_unknown_loc is None:
            return None

    response_segments = parse_target_or_response(response_str, rownum)
    if response_segments is None:
        return None

    target_has_duplicate_segments = len(target_segments) != len(set(target_segments))

    if len(response_segments) != len(target_segments) and ['correct'] in response_segments:
        print('WARNING: "+" is ambiguous because the target and response have different number of segments. ' +
              'Line {} ignored'.format(rownum))
        return None

    #-- swap "+" with the corresponding target value
    for i, r in enumerate(response_segments):
        if i >= len(target_segments):
            break
        if list(r) == ['correct']:
            #-- double validation -- in case we have order mismatch. Validate this only if the tar
            if not target_has_duplicate_segments and target_segments[i] in response_segments:
                print('WARNING: "+" is ambiguous because the target and response have different order of segments. ' +
                      'Line {} ignored'.format(rownum))
                return None

            response_segments[i] = target_segments[i]

    return response_segments + response_segments_unknown_loc


#------------------------------------------------------
def collapse_segments(parsed_segments):
    return [x for pn in parsed_segments for x in pn]


#------------------------------------------------------
def parse_target_or_response(raw_text, rownum):
    """
    Return a list of segments, each of which is a list of words

    :param raw_text:
    :param rownum:
    """

    if isinstance(raw_text, float):
        raw_text = "{:.0f}".format(raw_text)
    elif isinstance(raw_text, int):
        raw_text = "{:}".format(raw_text)

    segments = [e.strip() for e in raw_text.split('/')]

    parsed_segments = []
    for seg in segments:
        m = re.match('^([0-9,]*)\\s*t\\s*([0-9,]+)?$', seg)

        if m is None:
            parsed_segment = [ parse_segment_into_word_list(seg) ]
        else:
            parsed_segment = _parse_pre_thousand_segment(m, seg)
            if m.group(2) is not None:
                parsed_segment.append(parse_segment_into_word_list(m.group(2)))

        if None in parsed_segment:  # invalid format
            print('WARNING: unsupported target/response format: "{}" -- line {} ignored'.format(raw_text, rownum))
            return None

        #-- combine parts of the parsed segment
        parsed_segment = [e for seg in parsed_segment for e in seg]

        parsed_segments.append(tuple(parsed_segment))

    return parsed_segments


#------------------------------------------------------
def _parse_pre_thousand_segment(matcher, segment):
    """ Parse the 'thousand' and the preceding digits """

    if len(matcher.group(1)) == 0:
        # -- The word "thousand" with no preceding digit
        return [parse_segment_into_word_list('t')]

    elif len(matcher.group(1)) == 1:
        # -- A 4-digit number: the "thousand" is combined with the preceding digit
        return [parse_segment_into_word_list(matcher.group(1) + '000')]

    elif len(matcher.group(1)) in (2, 3):
        # -- A 5- or 6-digit number: the "thousand" is a separate word
        return [parse_segment_into_word_list(matcher.group(1)), parse_segment_into_word_list('t')]

    else:
        raise Exception('Unsupported format: {}'.format(segment))


#------------------------------------------------------
def parse_segment_into_word_list(segment):
    """
    Parse a number into a series of words

    :param segment: a string describing one grammatical segment (one number)
    """

    if segment in ('+', '!'):
        return ['correct']

    if segment == '-':
        return []

    segment = segment.replace(',', '')  # delete commas

    return hebnums.number_to_words(segment)


#------------------------------------------------------
def _open_input_file(filename):
    wb = openpyxl.load_workbook(filename)
    if len(wb.worksheets) == 1:
        ws = wb.worksheets[0]
    else:
        sheet_names = [s.title for s in wb.worksheets]
        if 'data' not in sheet_names:
            raise Exception('{} does not contain any worksheet named "data"'.format(filename))
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
