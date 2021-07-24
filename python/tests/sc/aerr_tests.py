import unittest

from sc.aerr import parse_segment_into_word_list


from sc.aerr import *


#------------------------------------------------------
def get_n_errors(raw_target, raw_response):
    target_segments, target, target_digits = analyze_target(raw_target, 0)
    n_word_errs, n_class_errs, n_digit_errs, response_digits = analyze_response(raw_response, target, target_segments, target_digits, 0)
    return n_word_errs, n_class_errs, n_digit_errs



class ParseSegmentTest(unittest.TestCase):

    #-------------------
    #-- No errors
    #-------------------

    #-- Simple cases

    def test_same_2(self):
        self.assertEqual((0, 0, 0), get_n_errors('2', '2'))

    def test_same_222(self):
        self.assertEqual((0, 0, 0), get_n_errors('222', '222'))

    def test_same_200(self):
        self.assertEqual((0, 0, 0), get_n_errors('200', '200'))

    def test_same_1000(self):
        self.assertEqual((0, 0, 0), get_n_errors('1000', '1000'))


    #-- Correct responses marked as +

    def test_same_plus(self):
        self.assertEqual((0, 0, 0), get_n_errors('2', '+'))

    def test_same_2segments_plus(self):
        self.assertEqual((0, 0, 0), get_n_errors('2 / 3', '+'))

    def test_same_2segments_2plus(self):
        self.assertEqual((0, 0, 0), get_n_errors('2 / 3', '+ / +'))


    #-- Correct responses, different formats

    def test_same_1000t(self):
        self.assertEqual((0, 0, 0), get_n_errors('1000', 't'))

    def test_same_decomposed_number(self):
        self.assertEqual((0, 0, 0), get_n_errors('234', '200 / 34'))

    def test_same_decomposed_number_2(self):
        self.assertEqual((0, 0, 0), get_n_errors('234', '200 / 30 / 4'))

    def test_same_1000_as_number_vs_alone(self):
        self.assertEqual((0, 0, 0), get_n_errors('1002', '1000 / 2'))

    def test_same_1000_as_number_vs_alone_2(self):
        self.assertEqual((0, 0, 0), get_n_errors('21002', '21 / 1000 / 2'))


    #-- Invalid word order doesn't matter

    def test_same_reversed_segments(self):
        self.assertEqual((0, 0, 0), get_n_errors('23 / 560', '560 / 23'))


    #-------------------
    #-- Digit errors
    #-------------------

    def test_digerr_ones(self):
        w, c, d = get_n_errors('2', '3')
        self.assertEqual((1, 0, 1), (w, c, d))

    def test_digerr_tens(self):
        w, c, d = get_n_errors('20', '30')
        self.assertEqual((1, 0, 1), (w, c, d))

    def test_digerr_ths(self):
        w, c, d = get_n_errors('2000', '3000')
        self.assertEqual((1, 0, 1), (w, c, d))

    #-------------------
    #-- Class errors
    #-------------------

    def test_classerr_ones_tens(self):
        w, c, d = get_n_errors('2', '20')
        self.assertEqual((1, 1, 0), (w, c, d))

    def test_classerr_ones_teens(self):
        w, c, d = get_n_errors('2', '12')
        self.assertEqual((1, 1, 0), (w, c, d))


    #-- Thousand is a special case

    def test_thousand_decimal_word_is_class_without_digit(self):
        w, c, d = get_n_errors('20000', '20')
        self.assertEqual((1, 0), (c, d))

    def test_one_thousand_is_not_a_digit(self):
        w, c, d = get_n_errors('1000', '-')
        self.assertEqual((1, 0), (c, d))

    def test_four_thousand_is_a_digit(self):
        w, c, d = get_n_errors('4000', '-')
        self.assertEqual((1, 1), (c, d))

    #-- The word "thousand" is said differently in 4-digit and 5-digit numbers
    def test_thousand_is_different_as_decimal_word_and_number(self):
        w, c, d = get_n_errors('20000', '20')
        self.assertEqual((1, 0), (c, d))  # the class is missing; the digit is not


if __name__ == '__main__':
    unittest.main()
