import numpy as np

READ_DOCSTRING = """
    Read the input ``table`` and return the table.  Most of
    the default behavior for various parameters is determined by the Reader
    class.

    See also:

    - http://docs.astropy.org/en/stable/io/ascii/
    - http://docs.astropy.org/en/stable/io/ascii/read.html

    Parameters
    ----------
    table : str, file-like, list, `pathlib.Path` object
        Input table as a file name, file-like object, list of strings,
        single newline-separated string or `pathlib.Path` object .
    guess : bool
        Try to guess the table format. Defaults to None.
    format : str, `~astropy.io.ascii.BaseReader`
        Input table format
    Inputter : `~astropy.io.ascii.BaseInputter`
        Inputter class
    Outputter : `~astropy.io.ascii.BaseOutputter`
        Outputter class
    delimiter : str
        Column delimiter string
    comment : str
        Regular expression defining a comment line in table
    quotechar : str
        One-character string to quote fields containing special characters
    header_start : int
        Line index for the header line not counting comment or blank lines.
        A line with only whitespace is considered blank.
    data_start : int
        Line index for the start of data not counting comment or blank lines.
        A line with only whitespace is considered blank.
    data_end : int
        Line index for the end of data not counting comment or blank lines.
        This value can be negative to count from the end.
    converters : dict
        Dictionary of converters
    data_Splitter : `~astropy.io.ascii.BaseSplitter`
        Splitter class to split data columns
    header_Splitter : `~astropy.io.ascii.BaseSplitter`
        Splitter class to split header columns
    names : list
        List of names corresponding to each data column
    include_names : list
        List of names to include in output.
    exclude_names : list
        List of names to exclude from output (applied after ``include_names``)
    fill_values : tuple, list of tuple
        specification of fill values for bad or missing table values
    fill_include_names : list
        List of names to include in fill_values.
    fill_exclude_names : list
        List of names to exclude from fill_values (applied after ``fill_include_names``)
    fast_reader : bool, str or dict
        Whether to use the C engine, can also be a dict with options which
        defaults to `False`; parameters for options dict:

        use_fast_converter: bool
            enable faster but slightly imprecise floating point conversion method
        parallel: bool or int
            multiprocessing conversion using ``cpu_count()`` or ``'number'`` processes
        exponent_style: str
            One-character string defining the exponent or ``'Fortran'`` to auto-detect
            Fortran-style scientific notation like ``'3.14159D+00'`` (``'E'``, ``'D'``, ``'Q'``),
            all case-insensitive; default ``'E'``, all other imply ``use_fast_converter``
        chunk_size : int
            If supplied with a value > 0 then read the table in chunks of
            approximately ``chunk_size`` bytes. Default is reading table in one pass.
        chunk_generator : bool
            If True and ``chunk_size > 0`` then return an iterator that returns a
            table for each chunk.  The default is to return a single stacked table
            for all the chunks.

    encoding : str
        Allow to specify encoding to read the file (default= ``None``).

    Returns
    -------
    dat : `~astropy.table.Table` OR <generator>
        Output table

    """

# Specify allowed types for core read() keyword arguments.
#   The commented-out kwargs are too flexible for a useful check
#   'list-list' is basically an iterable that is not a string.
READ_KWARG_TYPES = {
    # 'table'
    'guess': bool,
    # 'format'
    # 'Reader'
    # 'Inputter'
    # 'Outputter'
    'delimiter': (str, np.str_),
    'comment': (str, np.str_),
    'quotechar': (str, np.str_),
    'header_start': (int, np.integer),
    'data_start': (int, np.integer, str, np.str_),  # CDS allows 'guess'
    'data_end': (int, np.integer),
    'converters': dict,
    # 'data_Splitter'
    # 'header_Splitter'
    'names': 'list-like',
    'include_names': 'list-like',
    'exclude_names': 'list-like',
    'fill_values': 'list-like',
    'fill_include_names': 'list-like',
    'fill_exclude_names': 'list-like',
    'fast_reader': (bool, np.bool_, str, np.str_, dict),
    'encoding': (str, np.str_),
}


WRITE_DOCSTRING = """
    Write the input ``table`` to ``filename``.  Most of the default behavior
    for various parameters is determined by the Writer class.

    See also:

    - http://docs.astropy.org/en/stable/io/ascii/
    - http://docs.astropy.org/en/stable/io/ascii/write.html

    Parameters
    ----------
    table : `~astropy.io.ascii.BaseReader`, array_like, str, file_like, list
        Input table as a Reader object, Numpy struct array, file name,
        file-like object, list of strings, or single newline-separated string.
    output : str, file_like
        Output [filename, file-like object]. Defaults to``sys.stdout``.
    format : str
        Output table format. Defaults to 'basic'.
    delimiter : str
        Column delimiter string
    comment : str, bool
        String defining a comment line in table.  If `False` then comments
        are not written out.
    quotechar : str
        One-character string to quote fields containing special characters
    formats : dict
        Dictionary of format specifiers or formatting functions
    strip_whitespace : bool
        Strip surrounding whitespace from column values.
    names : list
        List of names corresponding to each data column
    include_names : list
        List of names to include in output.
    exclude_names : list
        List of names to exclude from output (applied after ``include_names``)
    fast_writer : bool, str
        Whether to use the fast Cython writer.  Can be `True` (use fast writer
        if available), `False` (do not use fast writer), or ``'force'`` (use
        fast writer and fail if not available, mostly for testing).
    overwrite : bool
        If ``overwrite=None`` (default) and the file exists, then a
        warning will be issued. In a future release this will instead
        generate an exception. If ``overwrite=False`` and the file
        exists, then an exception is raised.
        This parameter is ignored when the ``output`` arg is not a string
        (e.g., a file object).

    """
# Specify allowed types for core write() keyword arguments.
#   The commented-out kwargs are too flexible for a useful check
#   'list-list' is basically an iterable that is not a string.
WRITE_KWARG_TYPES = {
    # 'table'
    # 'output'
    'format': (str, np.str_),
    'delimiter': (str, np.str_),
    'comment': (str, np.str_, bool, np.bool_),
    'quotechar': (str, np.str_),
    'header_start': (int, np.integer),
    'formats': dict,
    'strip_whitespace': (bool, np.bool_),
    'names': 'list-like',
    'include_names': 'list-like',
    'exclude_names': 'list-like',
    'fast_writer': (bool, np.bool_, str, np.str_),
    'overwrite': (bool, np.bool_),
}
