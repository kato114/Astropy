"""Test behavior related to masked tables"""

from .. import Column, MaskedColumn, Table

import pytest
import numpy as np
import numpy.ma as ma


class SetupData(object):
    def setup_method(self, method):
        self.a = MaskedColumn('a', [1, 2, 3], fill_value=1)
        self.b = MaskedColumn('b', [4, 5, 6], mask=True)
        self.c = MaskedColumn('c', [7, 8, 9], mask=False)
        self.d_mask = np.array([False, True, False])
        self.d = MaskedColumn('d', [7, 8, 7], mask=self.d_mask)
        self.t = Table([self.a, self.b], masked=True)
        self.ca = Column('ca', [1, 2, 3])


class TestFillValue(SetupData):
    """Test setting and getting fill value in MaskedColumn and Table"""

    def test_init_set_fill_value(self):
        """Check that setting fill_value in the MaskedColumn init works"""
        assert self.a.fill_value == 1

    def test_set_get_fill_value_for_bare_column(self):
        """Check set and get of fill value works for bare Column"""
        self.d.fill_value = -999
        assert self.d.fill_value == -999
        assert np.all(self.d.filled() == [7, -999, 7])

    def test_table_column_mask_not_ref(self):
        """Table column mask is not ref of original column mask"""
        self.b.fill_value = -999
        assert self.t['b'].fill_value != -999

    def test_set_get_fill_value_for_table_column(self):
        """Check set and get of fill value works for Column in a Table"""
        self.t['b'].fill_value = 1
        assert self.t['b'].fill_value == 1
        assert np.all(self.t['b'].filled() == [1, 1, 1])
        assert self.t._data['b'].fill_value == 1

    def test_data_attribute_fill_and_mask(self):
        """Check that .data attribute preserves fill_value and mask"""
        self.t['b'].fill_value = 1
        self.t['b'].mask = [True, False, True]
        assert self.t['b'].data.fill_value == 1
        assert np.all(self.t['b'].data.mask == [True, False, True])


class TestMaskedColumnInit(SetupData):
    """Initialization of a masked column"""

    def test_set_mask_and_not_ref(self):
        """Check that mask gets set properly and that it is a copy, not ref"""
        assert np.all(self.a.mask == False)
        assert np.all(self.b.mask == True)
        assert np.all(self.c.mask == False)
        assert np.all(self.d.mask == self.d_mask)
        self.d.mask[0] = True
        assert not np.all(self.d.mask == self.d_mask)

    def test_set_mask_from_list(self):
        """Set mask from a list"""
        mask_list = [False, True, False]
        a = MaskedColumn('a', [1, 2, 3], mask=mask_list)
        assert np.all(a.mask == mask_list)

    def test_override_existing_mask(self):
        """Override existing mask values"""
        mask_list = [False, True, False]
        b = MaskedColumn('b', self.b, mask=mask_list)
        assert np.all(b.mask == mask_list)

    def test_incomplete_mask_spec(self):
        """Incomplete mask specification (mask values cycle through available)"""
        mask_list = [False, True]
        b = MaskedColumn('b', length=4, mask=mask_list)
        assert np.all(b.mask == mask_list + mask_list)


class TestTableInit(SetupData):
    """Initializing a table"""

    def test_mask_true_if_any_input_masked(self):
        """Masking is True if any input is masked"""
        t = Table([self.ca, self.a])
        assert t.masked is True
        t = Table([self.ca])
        assert t.masked is False
        t = Table([self.ca, ma.array([1, 2, 3])])
        assert t.masked is True


class TestAddColumn(object):

    def test_add_masked_column_to_masked_table(self):
        t = Table(masked=True)
        assert t.masked
        t.add_column(MaskedColumn('a', [1,2,3], mask=[0,1,0]))
        assert t.masked
        t.add_column(MaskedColumn('b', [4,5,6], mask=[1,0,1]))
        assert t.masked
        assert np.all(t['a'] == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,1,0], bool))
        assert np.all(t['b'] == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_masked_column_to_non_masked_table(self):
        t = Table(masked=False)
        assert not t.masked
        t.add_column(Column('a', [1,2,3]))
        assert not t.masked
        t.add_column(MaskedColumn('b', [4,5,6], mask=[1,0,1]))
        assert t.masked
        assert np.all(t['a'] == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,0,0], bool))
        assert np.all(t['b'] == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_non_masked_column_to_masked_table(self):
        t = Table(masked=True)
        assert t.masked
        t.add_column(Column('a', [1,2,3]))
        assert t.masked
        t.add_column(MaskedColumn('b', [4,5,6], mask=[1,0,1]))
        assert t.masked
        assert np.all(t['a'] == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,0,0], bool))
        assert np.all(t['b'] == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([1,0,1], bool))


class TestAddRow(object):

    def test_add_masked_row_to_masked_table_iterable(self):
        t = Table(masked=True)
        t.add_column(MaskedColumn('a', [1], mask=[0]))
        t.add_column(MaskedColumn('b', [4], mask=[1]))
        t.add_row([2,5], mask=[1,0])
        t.add_row([3,6], mask=[0,1])
        assert t.masked
        assert np.all(np.array(t['a']) == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,1,0], bool))
        assert np.all(np.array(t['b']) == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_masked_row_to_masked_table_mapping1(self):
        t = Table(masked=True)
        t.add_column(MaskedColumn('a', [1], mask=[0]))
        t.add_column(MaskedColumn('b', [4], mask=[1]))
        t.add_row({'b':5, 'a':2}, mask={'a':1, 'b':0})
        t.add_row({'a':3, 'b':6}, mask={'b':1, 'a':0})
        assert t.masked
        assert np.all(np.array(t['a']) == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,1,0], bool))
        assert np.all(np.array(t['b']) == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_masked_row_to_masked_table_mapping2(self):
        # When adding values to a masked table, if the mask is specified as a
        # dict, then values not specified will have mask values set to True
        t = Table(masked=True)
        t.add_column(MaskedColumn('a', [1], mask=[0]))
        t.add_column(MaskedColumn('b', [4], mask=[1]))
        t.add_row({'b':5}, mask={'b':0})
        t.add_row({'a':3}, mask={'a':0})
        assert t.masked
        assert t['a'][0] == 1 and t['a'][2] == 3
        assert np.all(t['a'].mask == np.array([0,1,0], bool))
        assert t['b'][1] == 5
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_masked_row_to_masked_table_mapping3(self):
        # When adding values to a masked table, if mask is not passed to
        # add_row, then the mask should be set to False if values are present
        # and True if not.
        t = Table(masked=True)
        t.add_column(MaskedColumn('a', [1], mask=[0]))
        t.add_column(MaskedColumn('b', [4], mask=[1]))
        t.add_row({'b':5})
        t.add_row({'a':3})
        assert t.masked
        assert t['a'][0] == 1 and t['a'][2] == 3
        assert np.all(t['a'].mask == np.array([0,1,0], bool))
        assert t['b'][1] == 5
        assert np.all(t['b'].mask == np.array([1,0,1], bool))

    def test_add_masked_row_to_masked_table_mismatch(self):
        t = Table(masked=True)
        t.add_column(MaskedColumn('a', [1], mask=[0]))
        t.add_column(MaskedColumn('b', [4], mask=[1]))
        with pytest.raises(TypeError) as exc:
            t.add_row([2,5], mask={'a':1, 'b':0})
        assert exc.value.args[0] == "Mismatch between type of vals and mask"
        with pytest.raises(TypeError) as exc:
            t.add_row({'b':5, 'a':2}, mask=[1,0])
        assert exc.value.args[0] == "Mismatch between type of vals and mask"

    def test_add_masked_row_to_non_masked_table_iterable(self):
        t = Table(masked=False)
        t.add_column(Column('a', [1]))
        t.add_column(Column('b', [4]))
        assert not t.masked
        t.add_row([2,5])
        assert not t.masked
        t.add_row([3,6], mask=[0,1])
        assert t.masked
        assert np.all(np.array(t['a']) == np.array([1,2,3]))
        assert np.all(t['a'].mask == np.array([0,0,0], bool))
        assert np.all(np.array(t['b']) == np.array([4,5,6]))
        assert np.all(t['b'].mask == np.array([0,0,1], bool))
