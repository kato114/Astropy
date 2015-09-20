from os.path import abspath, dirname, join

from ..table import Table
from ... import extern

EXTERN_DIR = abspath(dirname(extern.__file__))

REFERENCE = """
<html>
 <head>
  <meta charset="utf-8"/>
  <meta content="text/html;charset=UTF-8" http-equiv="Content-type"/>
  <style>
  </style>
  <link href="%(datatables_url)s/css/jquery.dataTables.min.css" rel="stylesheet" type="text/css"/>
  <script src="%(jquery_url)s/jquery-1.11.3.min.js">
  </script>
  <script src="%(datatables_url)s/js/jquery.dataTables.min.js">
  </script>
 </head>
 <body>
  <script>
$(document).ready(function() {
    $('#test').dataTable({
     "iDisplayLength": 50,
     "aLengthMenu": [[10, 25, 50, 100, 500, 1000, -1], [10, 25, 50, 100, 500, 1000, 'All']],
     "pagingType": "full_numbers"
    });
} );  </script>
  <table class="%(table_class)s" id="test">
   <thead>
    <tr>
     <th>a</th>
     <th>b</th>
    </tr>
   </thead>
   <tr>
    <td>1</td>
    <td>a</td>
   </tr>
   <tr>
    <td>2</td>
    <td>b</td>
   </tr>
   <tr>
    <td>3</td>
    <td>c</td>
   </tr>
  </table>
 </body>
</html>
"""


def test_write_jsviewer(tmpdir):
    t = Table()
    t['a'] = [1, 2, 3]
    t['b'] = ['a', 'b', 'c']
    t['a'].unit = 'm'

    tmpfile = tmpdir.join('test.html').strpath

    t.write(tmpfile, format='jsviewer', table_id='test')
    ref = REFERENCE % dict(
        table_class='display compact',
        datatables_url='https://cdn.datatables.net/1.10.9',
        jquery_url='https://code.jquery.com'
    )
    with open(tmpfile) as f:
        assert f.read().strip() == ref.strip()

    t.write(tmpfile, format='jsviewer', table_id='test',
            table_class='display hover')
    ref = REFERENCE % dict(
        table_class='display hover',
        datatables_url='https://cdn.datatables.net/1.10.9',
        jquery_url='https://code.jquery.com'
    )
    with open(tmpfile) as f:
        assert f.read().strip() == ref.strip()


def test_write_jsviewer_local(tmpdir):
    t = Table()
    t['a'] = [1, 2, 3]
    t['b'] = ['a', 'b', 'c']
    t['a'].unit = 'm'

    tmpfile = tmpdir.join('test.html').strpath

    t.write(tmpfile, format='jsviewer', table_id='test',
            jskwargs={'use_local_files': True})
    ref = REFERENCE % dict(
        table_class='display compact',
        datatables_url='file://' + EXTERN_DIR,
        jquery_url='file://' + join(EXTERN_DIR, 'js')
    )
    with open(tmpfile) as f:
        assert f.read().strip() == ref.strip()
