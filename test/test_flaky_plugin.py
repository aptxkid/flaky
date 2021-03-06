# coding: utf-8

from __future__ import unicode_literals
from io import StringIO
from mock import call, MagicMock, patch
from unittest import TestCase
from box.test.flaky.flaky_decorator import flaky
from box.test.flaky.flaky_plugin import FlakyPlugin
from box.test.flaky.names import FlakyNames


class TestFlakyPlugin(TestCase):
    def setUp(self):
        super(TestFlakyPlugin, self).setUp()

        test_mod = 'box.test.flaky.flaky_plugin'
        self._mock_test_result = MagicMock()
        self._mock_stream = MagicMock(spec=StringIO)
        with patch(test_mod + '.TextTestResult') as flaky_result:
            with patch(test_mod + '.StringIO') as string_io:
                string_io.return_value = self._mock_stream
                flaky_result.return_value = self._mock_test_result
                self._flaky_plugin = FlakyPlugin()
        self._mock_test = MagicMock(name='flaky_plugin_test')
        self._mock_test_case = MagicMock(
            name='flaky_plugin_test_case',
            spec=TestCase
        )
        self._mock_test_case.address = MagicMock()
        self._mock_test_case.test = self._mock_test
        self._mock_test_module_name = 'test_module'
        self._mock_test_class_name = 'TestClass'
        self._mock_test_method_name = 'test_method'
        self._mock_test_names = '{}:{}.{}'.format(
            self._mock_test_module_name,
            self._mock_test_class_name,
            self._mock_test_method_name
        )
        self._mock_exception = Exception('Error in {}'.format(
            self._mock_test_method_name)
        )
        self._mock_stack_trace = ''
        self._mock_exception_type = Exception
        self._mock_error = (
            self._mock_exception_type,
            self._mock_exception,
            self._mock_stack_trace
        )

    def _expect_call_test_address(self):
        self._mock_test_case.address.return_value = (
            None,
            None,
            self._mock_test_names
        )

    def _expect_test_flaky(self, is_test_method, max_runs, min_passes):
        self._expect_call_test_address()
        if is_test_method:
            for flaky_attr in FlakyNames():
                setattr(self._mock_test, flaky_attr, None)
            mock_test_method = getattr(
                self._mock_test,
                self._mock_test_method_name
            )
            flaky(max_runs, min_passes)(mock_test_method)
        else:
            flaky(max_runs, min_passes)(self._mock_test)
            mock_test_method = getattr(
                self._mock_test,
                self._mock_test_method_name
            )
            for flaky_attr in FlakyNames():
                setattr(mock_test_method, flaky_attr, None)

    def _expect_test_not_flaky(self):
        self._expect_call_test_address()
        for test_object in (
            self._mock_test,
            getattr(self._mock_test, self._mock_test_method_name)
        ):
            for flaky_attr in FlakyNames():
                setattr(test_object, flaky_attr, None)

    def _assert_test_ignored(self):
        self._mock_test_case.address.assert_called_with()
        self.assertEqual(self._mock_test_case.mock_calls, [call.address()])
        self.assertEqual(self._mock_test.mock_calls, [])

    def _get_flaky_attributes(self, is_test_method):
        if is_test_method:
            mock_test_method = getattr(
                self._mock_test,
                self._mock_test_method_name
            )
            test_object = mock_test_method
        else:
            test_object = self._mock_test
        actual_flaky_attributes = {
            attr: getattr(
                test_object,
                attr
            ) for attr in FlakyNames()
        }
        return actual_flaky_attributes

    def _set_flaky_attribute(self, is_test_method, attr, value):
        if is_test_method:
            mock_test_method = getattr(
                self._mock_test,
                self._mock_test_method_name
            )
            test_object = mock_test_method
        else:
            test_object = self._mock_test
        setattr(test_object, attr, value)

    def _assert_flaky_attributes_contains(
        self,
        expected_flaky_attributes,
    ):
        actual_flaky_attributes = self._get_flaky_attributes(True)
        self.assertDictContainsSubset(
            expected_flaky_attributes,
            actual_flaky_attributes,
            'Unexpected flaky attributes, {} vs {}'.format(
                expected_flaky_attributes,
                actual_flaky_attributes
            )
        )

    def test_flaky_plugin_report(self):
        flaky_report = 'Flaky tests passed; others failed. ' \
                       'No more tests; that ship has sailed.'
        self._test_flaky_plugin_report(flaky_report)

    def test_flaky_plugin_handles_success_for_test_method(self):
        self._test_flaky_plugin_handles_success()

    def test_flaky_plugin_handles_success_for_test_instance(self):
        self._test_flaky_plugin_handles_success(is_test_method=False)

    def test_flaky_plugin_handles_success_for_needs_rerun(self):
        self._test_flaky_plugin_handles_success(min_passes=2)

    def test_flaky_plugin_ignores_success_for_non_flaky_test(self):
        self._expect_test_not_flaky()
        self._flaky_plugin.addSuccess(self._mock_test_case)
        self._assert_test_ignored()

    def test_flaky_plugin_ignores_error_for_non_flaky_test(self):
        self._expect_test_not_flaky()
        self._flaky_plugin.handleError(self._mock_test_case, None)
        self._assert_test_ignored()

    def test_flaky_plugin_ignores_failure_for_non_flaky_test(self):
        self._expect_test_not_flaky()
        self._flaky_plugin.handleFailure(self._mock_test_case, None)
        self._assert_test_ignored()

    def test_flaky_plugin_handles_error_for_test_method(self):
        self._test_flaky_plugin_handles_failure_or_error()

    def test_flaky_plugin_handles_error_for_test_instance(self):
        self._test_flaky_plugin_handles_failure_or_error(is_test_method=False)

    def test_flaky_plugin_handles_failure_for_test_method(self):
        self._test_flaky_plugin_handles_failure_or_error(is_failure=True)

    def test_flaky_plugin_handles_failure_for_test_instance(self):
        self._test_flaky_plugin_handles_failure_or_error(
            is_failure=True,
            is_test_method=False
        )

    def test_flaky_plugin_handles_failure_for_no_more_retries(self):
        self._test_flaky_plugin_handles_failure_or_error(
            is_failure=True,
            max_runs=1
        )

    def test_flaky_plugin_handles_additional_errors(self):
        self._test_flaky_plugin_handles_failure_or_error(
            current_errors=[self._mock_error]
        )

    def _test_flaky_plugin_handles_failure_or_error(
        self,
        current_errors=None,
        current_passes=0,
        current_runs=0,
        is_failure=False,
        is_test_method=True,
        max_runs=2,
        min_passes=1,
    ):
        self._expect_test_flaky(is_test_method, max_runs, min_passes)
        if current_errors is None:
            current_errors = [self._mock_error]
        else:
            current_errors.append(self._mock_error)
        self._set_flaky_attribute(
            is_test_method,
            FlakyNames.CURRENT_ERRORS,
            current_errors
        )
        self._set_flaky_attribute(
            is_test_method,
            FlakyNames.CURRENT_PASSES,
            current_passes
        )
        self._set_flaky_attribute(
            is_test_method,
            FlakyNames.CURRENT_RUNS,
            current_runs
        )

        too_few_passes = current_passes < min_passes
        retries_remaining = current_runs + 1 < max_runs
        expected_plugin_handles_failure = too_few_passes and retries_remaining

        self._flaky_plugin.prepareTestCase(self._mock_test_case)
        if is_failure:
            actual_plugin_handles_failure = self._flaky_plugin.handleFailure(
                self._mock_test_case,
                self._mock_error
            )
        else:
            actual_plugin_handles_failure = self._flaky_plugin.handleError(
                self._mock_test_case,
                self._mock_error
            )

        self.assertEqual(
            expected_plugin_handles_failure,
            actual_plugin_handles_failure,
            'Expected plugin{} to handle the test run, but it did{}.'.format(
                ' to' if expected_plugin_handles_failure else '',
                '' if actual_plugin_handles_failure else ' not'
            )
        )
        self._assert_flaky_attributes_contains(
            {
                FlakyNames.CURRENT_RUNS: current_runs + 1,
                FlakyNames.CURRENT_ERRORS: current_errors
            }
        )
        expected_test_case_calls = [call.address(), call.address()]
        if expected_plugin_handles_failure:
            expected_test_case_calls.append(call.run(self._mock_test_result))
            expected_stream_calls = [call.writelines([
                self._mock_test_method_name,
                ' failed ({} runs remaining out of {}).'.format(
                    max_runs - current_runs - 1, max_runs
                ),
                '\n\t',
                unicode(self._mock_error[0]),
                '\n\t',
                unicode(self._mock_error[1].message),
                '\n\t',
                unicode(self._mock_error[2]),
                '\n'
            ])]
        else:
            expected_stream_calls = [call.writelines([
                self._mock_test_method_name,
                ' failed; it passed {} out of the required {} times.'.format(
                    current_passes,
                    min_passes
                ),
                '\n\t',
                unicode(self._mock_error[0]),
                '\n\t',
                unicode(self._mock_error[1].message),
                '\n\t',
                unicode(self._mock_error[2]),
                '\n'
            ])]
        self.assertEqual(
            self._mock_test_case.mock_calls,
            expected_test_case_calls,
            'Unexpected TestCase calls: {} vs {}'.format(
                self._mock_test_case.mock_calls,
                expected_test_case_calls
            )
        )
        self.assertEqual(self._mock_stream.mock_calls, expected_stream_calls)

    def _test_flaky_plugin_handles_success(
        self,
        current_passes=0,
        current_runs=0,
        is_test_method=True,
        max_runs=2,
        min_passes=1
    ):
        self._expect_test_flaky(is_test_method, max_runs, min_passes)
        self._set_flaky_attribute(
            is_test_method,
            FlakyNames.CURRENT_PASSES,
            current_passes
        )
        self._set_flaky_attribute(
            is_test_method,
            FlakyNames.CURRENT_RUNS,
            current_runs
        )

        too_few_passes = current_passes + 1 < min_passes
        retries_remaining = current_runs + 1 < max_runs
        expected_plugin_handles_success = too_few_passes and retries_remaining

        self._flaky_plugin.prepareTestCase(self._mock_test_case)
        actual_plugin_handles_success = self._flaky_plugin.addSuccess(
            self._mock_test_case
        )

        self.assertEqual(
            expected_plugin_handles_success,
            actual_plugin_handles_success,
            'Expected plugin{} to handle the test run, but it did{}.'.format(
                ' to' if expected_plugin_handles_success else '',
                '' if actual_plugin_handles_success else ' not'
            )
        )
        self._assert_flaky_attributes_contains(
            {
                FlakyNames.CURRENT_PASSES: current_passes + 1,
                FlakyNames.CURRENT_RUNS: current_runs + 1,
            }
        )
        expected_test_case_calls = [call.address(), call.address()]
        expected_stream_calls = [call.writelines([
            self._mock_test_method_name,
            " passed {} out of the required {} times. ".format(
                current_passes + 1, min_passes,
            ),
        ])]
        if expected_plugin_handles_success:
            expected_test_case_calls.append(call.run(self._mock_test_result))
            expected_stream_calls.append(
                call.write(
                    'Running test again until it passes {} times.\n'.format(
                        min_passes,
                    ),
                ),
            )
        else:
            expected_stream_calls.append(call.write('Success!\n'))
        self.assertEqual(
            self._mock_test_case.mock_calls,
            expected_test_case_calls,
            'Unexpected TestCase calls = {} vs {}'.format(
                self._mock_test_case.mock_calls,
                expected_test_case_calls,
            ),
        )
        self.assertEqual(self._mock_stream.mock_calls, expected_stream_calls)

    def _test_flaky_plugin_report(self, expected_stream_value):
        mock_stream = MagicMock()
        self._mock_stream.getvalue.return_value = expected_stream_value

        self._flaky_plugin.report(mock_stream)

        self.assertEqual(
            mock_stream.mock_calls,
            [
                call.write('===Flaky Test Report===\n\n'),
                call.write(expected_stream_value),
                call.write('\n===End Flaky Test Report===\n'),
            ],
        )
