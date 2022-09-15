import numpy as np
import pandas as pd
import pytest
from numpy import testing as nptest
from pandas import testing as tm

from openoa.utils._converters import (
    _list_of_len,
    df_to_series,
    series_to_df,
    series_method,
    dataframe_method,
    convert_args_to_lists,
    multiple_df_to_single_df,
)


test_df1 = pd.DataFrame(
    np.arange(15).reshape(5, 3, order="F"), columns=["a", "b", "c"], dtype=float
)
test_series_a1 = pd.Series(range(5), name="a", dtype=float)
test_series_b1 = pd.Series(range(5, 10), name="b", dtype=float)
test_series_c1 = pd.Series(range(10, 15), name="c", dtype=float)
test_df_list1 = [test_series_a1.to_frame(), test_series_b1.to_frame(), test_series_c1.to_frame()]

test_df2 = test_df1.copy()
test_df2.loc[5] = [15.0, np.nan, np.nan]
test_series_a2 = test_series_a1.copy()
test_series_a2.loc[5] = 15.0
test_df_list2 = [test_series_a2.to_frame(), test_series_b1.to_frame(), test_series_c1.to_frame()]

test_df3 = test_df2.copy()
test_df3.index.name = "index"
test_align_col3 = "index"
test_df_list3 = [
    test_df3[["a"]].reset_index(drop=False),
    test_df3[["b"]].reset_index(drop=False),
    test_df3[["c"]].reset_index(drop=False),
]


def test_list_of_len():
    """Tests the `_list_of_len` method."""

    # Test for a 1 element list
    x = [1]
    length = 4
    y = [1, 1, 1, 1]
    y_test = _list_of_len(x, length)
    assert y == y_test

    # Test for a multi-element list with the length as a multiple of the length of the list
    x = ["a", "b", "C"]
    length = 6
    y = ["a", "b", "C", "a", "b", "C"]
    y_test = _list_of_len(x, length)
    assert y == y_test

    # Test for a multi-element list that should have a resulting unequal number of repeated elements
    x = [1, "4", 7]
    length = 4
    y = [1, "4", 7, 1]
    y_test = _list_of_len(x, length)
    assert y == y_test


def test_convert_args_to_lists():
    """Tests the `convert_args_to_lists` method."""

    # Test for a list that already contains lists
    x = [["a"], [5, 6]]
    length = 2
    y = [["a"], [5, 6]]
    y_test = convert_args_to_lists(length, *x)
    assert y == y_test

    # Test for a list of single element arguments
    x = ["a", 5, 6]
    length = 2
    y = [["a", "a"], [5, 5], [6, 6]]
    y_test = convert_args_to_lists(length, *x)
    assert y == y_test

    # Test for list of mixed length elements
    x = ["a", 5, [6]]
    length = 2
    y = [["a", "a"], [5, 5], [6]]
    y_test = convert_args_to_lists(length, *x)
    assert y == y_test


def test_df_to_series():
    """Tests the `df_to_series` method."""

    # Test that each column is returned correctly, in a few different order variations
    y = [test_series_a1, test_series_b1, test_series_c1]
    y_test = df_to_series(test_df1, "a", "b", "c")
    for el, el_test in zip(y, y_test):
        tm.assert_series_equal(el, el_test)

    y = [test_series_c1, test_series_a1]
    y_test = df_to_series(test_df1, "c", "a")
    for el, el_test in zip(y, y_test):
        tm.assert_series_equal(el, el_test)

    y = [test_series_b1]
    y_test = df_to_series(test_df1, "b")
    for el, el_test in zip(y, y_test):
        tm.assert_series_equal(el, el_test)

    # Test that None is returned for a passed None value
    y = [None, test_series_a1, None, test_series_b1, test_series_c1, None]
    y_test = df_to_series(test_df1, None, "a", None, "b", "c", None)
    for el, el_test in zip(y, y_test):
        if el is None:
            assert el_test is None
            continue
        tm.assert_series_equal(el, el_test)

    # Test for bad inputs `data`
    with pytest.raises(TypeError):
        df_to_series(test_series_a1, "a")

    with pytest.raises(TypeError):
        df_to_series(4, "a")

    # Test for a series proved to `args`
    with pytest.raises(TypeError):
        df_to_series(test_df1, "a", test_series_b1)

    # Test for missing columns
    with pytest.raises(ValueError):
        df_to_series(test_df1, "a", "d")


def test_multiple_df_to_single_df():
    """Tests the `multiple_df_to_single_df` method."""

    # Test a basic working case with single column DataFrames
    y = test_df1
    y_test = multiple_df_to_single_df(*test_df_list1)
    tm.assert_frame_equal(y, y_test)

    # Test a basic working case with different length inputs
    y = test_df2
    y_test = multiple_df_to_single_df(*test_df_list2)
    tm.assert_frame_equal(y, y_test)

    # Test a basic working case with an `align_col` argument
    y = test_df3
    y_test = multiple_df_to_single_df(*test_df_list3, align_col=test_align_col3)
    tm.assert_frame_equal(y, y_test)
    not tm.assert_frame_equal(test_df2, y_test)

    # Ensure non DataFrame arguments fail
    with pytest.raises(TypeError):
        multiple_df_to_single_df(test_series_a1, *test_df_list1)

    # Check that a missing `align_col` fails
    with pytest.raises(ValueError):
        multiple_df_to_single_df(*test_df_list3, align_col="Index")
