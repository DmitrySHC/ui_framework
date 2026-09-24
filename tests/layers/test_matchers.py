import pytest

from ui_framework import assert_that, contains_string, equal_to


def test_assert_that_passes():
    assert_that("Secure Area", contains_string("Secure"))


def test_assert_that_raises_assertion_error():
    with pytest.raises(AssertionError):
        assert_that("Login", equal_to("Secure"))
