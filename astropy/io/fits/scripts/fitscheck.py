# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
``fitscheck`` is a command line script based on astropy.io.fits for verifying
and updating the CHECKSUM and DATASUM keywords of .fits files.  ``fitscheck``
can also detect and often fix other FITS standards violations.  ``fitscheck``
facilitates re-writing the non-standard checksums originally generated by
astropy.io.fits with standard checksums which will interoperate with CFITSIO.

``fitscheck`` will refuse to write new checksums if the checksum keywords are
missing or their values are bad.  Use ``--force`` to write new checksums
regardless of whether or not they currently exist or pass.  Use
``--ignore-missing`` to tolerate missing checksum keywords without comment.

Example uses of fitscheck:

1. Verify and update checksums, tolerating non-standard checksums, updating to
   standard checksum::

    $ fitscheck --checksum either --write *.fits

2. Write new checksums,  even if existing checksums are bad or missing::

    $ fitscheck --write --force *.fits

3. Verify standard checksums and FITS compliance without changing the files::

    $ fitscheck --compliance *.fits

4. Verify original nonstandard checksums only::

    $ fitscheck --checksum nonstandard *.fits

5. Only check and fix compliance problems,  ignoring checksums::

    $ fitscheck --checksum none --compliance --write *.fits

6. Verify standard interoperable checksums::

    $ fitscheck *.fits

7. Delete checksum keywords::

    $ fitscheck --checksum none --write *.fits
"""


import logging
import optparse
import sys
import textwrap
import warnings

from ... import fits


log = logging.getLogger('fitscheck')


warnings.filterwarnings('error', message='Checksum verification failed')
warnings.filterwarnings('error', message='Datasum verification failed')
warnings.filterwarnings('ignore', message='Overwriting existing file')


def handle_options(args):
    if not len(args):
        args = ['-h']

    parser = optparse.OptionParser(usage=textwrap.dedent("""
        fitscheck [options] <.fits files...>

        .e.g. fitscheck example.fits

        Verifies and optionally re-writes the CHECKSUM and DATASUM keywords
        for a .fits file.
        Optionally detects and fixes FITS standard compliance problems.
        """.strip()))

    parser.add_option(
        '-k', '--checksum', dest='checksum_kind',
        type='choice', choices=['standard', 'nonstandard', 'either', 'none'],
        help='Choose FITS checksum mode or none.  Defaults standard.',
        default='standard', metavar='[standard | nonstandard | either | none]')

    parser.add_option(
        '-w', '--write', dest='write_file',
        help='Write out file checksums and/or FITS compliance fixes.',
        default=False, action='store_true')

    parser.add_option(
        '-f', '--force', dest='force',
        help='Do file update even if original checksum was bad.',
        default=False, action='store_true')

    parser.add_option(
        '-c', '--compliance', dest='compliance',
        help='Do FITS compliance checking; fix if possible.',
        default=False, action='store_true')

    parser.add_option(
        '-i', '--ignore-missing', dest='ignore_missing',
        help='Ignore missing checksums.',
        default=False, action='store_true')

    parser.add_option(
        '-v', '--verbose', dest='verbose', help='Generate extra output.',
        default=False, action='store_true')

    global OPTIONS
    OPTIONS, fits_files = parser.parse_args(args)

    if OPTIONS.checksum_kind == 'none':
        OPTIONS.checksum_kind = False

    return fits_files


def setup_logging():
    if OPTIONS.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)


def verify_checksums(filename):
    """
    Prints a message if any HDU in `filename` has a bad checksum or datasum.
    """

    errors = 0
    try:
        hdulist = fits.open(filename, checksum=OPTIONS.checksum_kind)
    except UserWarning as w:
        remainder = '.. ' + ' '.join(str(w).split(' ')[1:]).strip()
        # if "Checksum" in str(w) or "Datasum" in str(w):
        log.warn('BAD %r %s' % (filename, remainder))
        return 1
    if not OPTIONS.ignore_missing:
        for i, hdu in enumerate(hdulist):
            if not hdu._checksum:
                log.warn('MISSING %r .. Checksum not found in HDU #%d' %
                         (filename, i))
                return 1
            if not hdu._datasum:
                log.warn('MISSING %r .. Datasum not found in HDU #%d' %
                         (filename, i))
                return 1
    if not errors:
        log.info('OK %r' % filename)
    return errors


def verify_compliance(filename):
    """Check for FITS standard compliance."""

    hdulist = fits.open(filename)
    try:
        hdulist.verify('exception')
    except fits.VerifyError as e:
        log.warn('NONCOMPLIANT %r .. %s' %
                 (filename), str(e).replace('\n', ' '))
        return 1
    return 0


def update(filename):
    """
    Sets the ``CHECKSUM`` and ``DATASUM`` keywords for each HDU of `filename`.

    Also updates fixes standards violations if possible and requested.
    """

    hdulist = fits.open(filename)
    try:
        output_verify = 'silentfix' if OPTIONS.compliance else 'ignore'
        hdulist.writeto(filename, checksum=OPTIONS.checksum_kind, clobber=True,
                        output_verify=output_verify)
    except fits.VerifyError:
        pass  # unfixable errors already noted during verification phase
    finally:
        hdulist.close()


def process_file(filename):
    """
    Handle a single .fits file,  returning the count of checksum and compliance
    errors.
    """

    try:
        checksum_errors = verify_checksums(filename)
        if OPTIONS.compliance:
            compliance_errors = verify_compliance(filename)
        else:
            compliance_errors = 0
        if OPTIONS.write_file and checksum_errors == 0 or OPTIONS.force:
            update(filename)
        return checksum_errors + compliance_errors
    except Exception as e:
        log.error('EXCEPTION %r .. %s' % (filename, e))
        return 1


def main():
    """
    Processes command line parameters into options and files,  then checks
    or update FITS DATASUM and CHECKSUM keywords for the specified files.
    """

    errors = 0
    fits_files = handle_options(sys.argv[1:])
    setup_logging()
    for filename in fits_files:
        errors += process_file(filename)
    if errors:
        log.warn('%d errors' % errors)
    return int(bool(errors))
