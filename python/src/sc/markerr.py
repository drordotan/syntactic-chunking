"""
Mark errors in the results file
"""
import openpyxl
import re
import pandas as pd
from mtl import verbalnumbers


xls_copy_cols = 'Block', 'Condition', 'ItemNum', 'target', 'response', 'NWordsPerTarget'
xls_cols = ('Subject', ) + xls_copy_cols + ('NMissingWords', 'NMissingDigits', 'NMissingClasses')
xls_out_cols = ('Subject', ) + xls_copy_cols + \
               ('NTargetDigits', 'NMissingWords', 'PMissingWords', 'NMissingDigits',
                'PMissingDigits', 'NMissingClasses', 'PMissingClasses', 'PMissingMorphemes')

xls_optional_cols = 'manual', 'WordOrder'


# noinspection PyMethodMayBeStatic
class ErrorAnalyzer(object):

    #------------------------------------------------------
    def __init__(self, digit_mapping=None, subj_id_transformer=None, consider_thousand_as_digit=True, accuracy_per_digit=False):
        """

        :param digit_mapping:
        :param subj_id_transformer: Function for transfoming the subject ID field
        :param consider_thousand_as_digit:  Whether the word "thousand" should count towards digit errors also in numbers with 5 or 6 digits
        :param accuracy_per_digit: This concerns the output files per word/morpheme: whether to compute the word/digit accuracy
                for each specific word or less precisely. Value=True is impossible if the target contains duplicate digits.
        """
        self._digit_mapping = {str(d): d for d in range(0, 10)}
        if digit_mapping is not None:
            self._digit_mapping.update(digit_mapping)

        self.subj_id_transformer = subj_id_transformer
        self.consider_thousand_as_digit = consider_thousand_as_digit
        self.accuracy_per_digit = accuracy_per_digit


    #------------------------------------------------------
    def run(self, in_fn, out_dir, worksheet='data'):
        """
        Analyze the error rates (digit, class, morpheme, word) in each trial

        :param in_fn: Excel file with the raw data (uncoded)
        :param worksheet: Name of worksheet to read
        :param out_dir: Directory for output files
        """

        in_ws, col_inds = self._open_input_file(in_fn, worksheet)
        out_wb, out_ws = self.create_output_workbook()

        result_per_word = dict(subject=[], block=[], condition=[], itemNum=[], target=[], response=[], nTargetWords=[],
                               wordOK=[], digitOK=[], classOK=[])

        result_per_morpheme = dict(subject=[], block=[], condition=[], itemNum=[], segment_num=[], target=[], response=[],
                                   target_segment=[], nTargetWords=[], nTargetDigits=[], nTargetMorphemes=[],
                                   morpheme_type=[], correct=[])

        ok = True
        for rownum in range(2, in_ws.max_row+1):
            ok = self.parse_row(in_ws, out_ws, rownum, col_inds, result_per_word, result_per_morpheme) and ok

        if not ok:
            print('Some errors were encountered. Set 1 in the "manual" column to override automatic error encoding.')

        out_ws.freeze_panes = out_ws['A2']
        self.auto_col_width(out_ws)
        out_wb.save(out_dir + '/data_coded.xlsx')
        pd.DataFrame(result_per_word).to_csv(out_dir+'/data_coded_words.csv', index=False)
        pd.DataFrame(result_per_morpheme).to_csv(out_dir+'/data_coded_morphemes.csv', index=False)


    #------------------------------------------------------
    def parse_row(self, in_ws, out_ws, rownum, col_inds, result_per_word, result_per_morpheme):
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

        out_ws.cell(rownum, xls_out_cols.index('Subject')+1).value = \
            subj_id if self.subj_id_transformer is None else self.subj_id_transformer(subj_id)

        for colname in xls_copy_cols:
            out_ws.cell(rownum, xls_out_cols.index(colname) + 1).value = in_ws.cell(rownum, col_inds[colname]).value

        target_segments, target, target_digits = self.analyze_target(raw_target, rownum)
        n_target_digits = len(target_digits)

        if n_target_words is None:
            print("Error in line {}: 'NWordsPerTarget' was not specified".format(rownum))
            return False

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
            n_word_errs, n_class_errs, n_digit_errs, response_digits = \
                self.analyze_response(raw_response, target, target_segments, target_digits, rownum)
            if n_word_errs is None:  # Error
                return False

        self._save_value(out_ws, rownum, 'NTargetDigits', n_target_digits)
        self._save_value(out_ws, rownum, 'NMissingWords', n_word_errs)
        self._save_value(out_ws, rownum, 'NMissingDigits', n_digit_errs)
        self._save_value(out_ws, rownum, 'NMissingClasses', n_class_errs)
        self._save_value(out_ws, rownum, 'PMissingWords', n_word_errs / n_target_words)
        self._save_value(out_ws, rownum, 'PMissingDigits', n_digit_errs / n_target_digits)
        self._save_value(out_ws, rownum, 'PMissingClasses', n_class_errs / n_target_words)
        self._save_value(out_ws, rownum, 'PMissingMorphemes', (n_class_errs + n_digit_errs) / (n_target_words + n_target_digits))

        if manual_coding and self.accuracy_per_digit:
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
            result_per_morpheme['segment_num'].append(i+1 if self.accuracy_per_digit else '')
            result_per_morpheme['target'].append(raw_target)
            result_per_morpheme['target_segment'].append(target_digits[i] if self.accuracy_per_digit else '')
            result_per_morpheme['response'].append(raw_response)
            result_per_morpheme['nTargetWords'].append(n_target_words)
            result_per_morpheme['nTargetDigits'].append(n_target_digits)
            result_per_morpheme['nTargetMorphemes'].append(n_target_words + n_target_digits)
            result_per_morpheme['morpheme_type'].append('digit')

            if self.accuracy_per_digit:
                correct = target_digits[i] in response_digits
            else:
                correct = 1 if i >= n_digit_errs else 0

            result_per_morpheme['correct'].append(correct)

        return True


    #------------------------------------------------------
    def analyze_target(self, raw_target, rownum):
        target_segments = self.parse_target_or_response(raw_target, rownum)
        target = self.collapse_segments(target_segments)

        target_digits = [t.digit for t in target if t.digit is not None][::-1]  # put the ones word in position 1

        return target_segments, target, target_digits


    #------------------------------------------------------
    def analyze_response(self, raw_response, target, target_segments, target_digits, rownum):

        response_segments = self.parse_response(raw_response, rownum, target_segments)
        if target_segments is None or response_segments is None:
            return [None] * 4

        response = self.collapse_segments(response_segments)

        n_word_errs = self.n_missing_target_items(target, response)
        n_class_errs = self._n_missing_classes(target, response)

        response_digits = [r.digit for r in response if r.digit is not None]
        n_digit_errs = self.n_missing_target_items(target_digits, response_digits)

        return n_word_errs, n_class_errs, n_digit_errs, response_digits


    #------------------------------------------------------
    def _save_value(self, out_ws, rownum, colname, value):
        out_ws.cell(rownum, 1 + xls_out_cols.index(colname)).value = value


    #------------------------------------------------------
    def _n_missing_classes(self, target, response):
        target = [t.lexical_class for t in target]
        response = [r.lexical_class for r in response]

        for r in response:
            if r in target:
                target.remove(r)

        return len(target)


    #------------------------------------------------------
    def n_missing_target_items(self, target_items, response_items):
        # No. of target items that are not in the response

        tmp = list(target_items)
        for r in response_items:
            if r in tmp:
                tmp.remove(r)

        return len(tmp)


    #------------------------------------------------------
    def parse_response(self, response_str, rownum, target_segments):

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
            response_segments_unknown_loc = self.parse_target_or_response(m.group(2), rownum)
            if response_segments_unknown_loc is None:
                return None

        try:
            response_segments = self.parse_target_or_response(response_str, rownum)
            if response_segments is None:
                return None
        except ValueError as e:
            print('Error in line {} (line ignored): {} '.format(rownum, e))
            return None

        target_has_duplicate_segments = len(target_segments) != len(set(target_segments))

        if len(response_segments) != len(target_segments) and ['correct'] in response_segments:
            print('WARNING: "+" is ambiguous because the target and response have different number of segments. ' +
                  'Line {} ignored'.format(rownum))
            return None

        #-- swap "+" with the corresponding target value
        for i, r in enumerate(response_segments):
            if list(r) == ['correct']:
                #-- double validation -- in case we have order mismatch. Validate this only if the tar
                if i >= len(target_segments) or (not target_has_duplicate_segments and target_segments[i] in response_segments):
                    print('WARNING: "+" is ambiguous because the target and response have different order of segments. ' +
                          'Line {} ignored'.format(rownum))
                    return None

                response_segments[i] = target_segments[i]

        return response_segments + response_segments_unknown_loc


    #------------------------------------------------------
    def collapse_segments(self, parsed_segments):
        return [x for pn in parsed_segments for x in pn]


    #------------------------------------------------------
    def parse_target_or_response(self, raw_text, rownum):
        """
        Return a list of segments, each of which is a list of words
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
                parsed_segment = [self.parse_segment_into_word_list(seg)]
            else:
                parsed_segment = self._parse_pre_thousand_segment(m, seg)
                if m.group(2) is not None:
                    parsed_segment.append(self.parse_segment_into_word_list(m.group(2)))

            if None in parsed_segment:  # invalid format
                print('WARNING: unsupported target/response format: "{}" -- line {} ignored'.format(raw_text, rownum))
                return None

            #-- combine parts of the parsed segment
            parsed_segment = [e for seg in parsed_segment for e in seg]

            parsed_segments.append(tuple(parsed_segment))

        return parsed_segments


    #------------------------------------------------------
    def _parse_pre_thousand_segment(self, matcher, segment):
        """ Parse the 'thousand' and the preceding digits """

        if len(matcher.group(1)) == 0:
            # -- The word "thousand" with no preceding digit
            return [self.parse_segment_into_word_list('t')]

        elif len(matcher.group(1)) == 1:
            # -- A 4-digit number: the "thousand" is combined with the preceding digit
            return [self.parse_segment_into_word_list(matcher.group(1) + '000')]

        elif len(matcher.group(1)) in (2, 3):
            # -- A 5- or 6-digit number: the "thousand" is a separate word
            return [self.parse_segment_into_word_list(matcher.group(1)), self.parse_segment_into_word_list('t')]

        else:
            raise Exception('Unsupported format: {}'.format(segment))


    #------------------------------------------------------
    def parse_segment_into_word_list(self, segment):
        """
        Parse a number into a series of words

        :param segment: a string describing one grammatical segment (one number)
        """

        if segment in ('+', '!'):   # "+" is correct; "!" is TBD
            return ['correct']

        if segment in ('-', '?'):   # "-" means omission; "?" means "I don't know"
            return []

        segment = segment.replace(',', '')  # delete commas

        result = verbalnumbers.hebrew.number_to_words(segment, digit_mapping=self._digit_mapping)

        if not self.consider_thousand_as_digit:
            #todo this fix should be in the code
            one_thousand = verbalnumbers.general.NumberWord(verbalnumbers.hebrew.thousands, 1)
            decimal_word_thousand = verbalnumbers.general.NumberWord(verbalnumbers.hebrew.decword_thousand, None)
            for i, w in enumerate(result):
                if w == one_thousand:
                    result[i] = decimal_word_thousand

        return result


    #------------------------------------------------------
    def _open_input_file(self, filename, worksheet):
        wb = openpyxl.load_workbook(filename)
        if len(wb.worksheets) == 1:
            ws = wb.worksheets[0]
        else:
            sheet_names = [s.title for s in wb.worksheets]
            if worksheet not in sheet_names:
                raise Exception('{} does not contain any worksheet named "data"'.format(filename))
            ws = wb.get_sheet_by_name(worksheet)

        col_inds = self._xls_structure(ws)

        return ws, col_inds


    def _xls_structure(self, ws):
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
    def create_output_workbook(self):

        wb = openpyxl.Workbook()
        ws = wb.worksheets[0]

        for i_col, colname in enumerate(xls_out_cols):
            ws.cell(1, i_col+1).value = colname

        return wb, ws


    #------------------------------------------------------
    def auto_col_width(self, ws):
        for col in ws.columns:
            max_length = 0
            for cell in col:
                try:  # Necessary to avoid error on empty cells
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass

            ws.column_dimensions[col[0].column_letter].width = max_length


#------------------------
def _nullto0(v):
    if v is None or v == '':
        return 0
    else:
        return v
