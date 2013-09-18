
# astropy/units/format/cds_parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = 'o\xc2\x11\xf7/(Q\xfc?\xf7\xd2\xbf\xf9Q\xfez'
    
_lr_action_items = {u'DIVISION':([0,4,6,9,10,11,12,13,17,18,20,23,26,27,29,31,32,35,36,],[1,-10,-16,1,-15,-18,1,26,-24,-23,-14,-17,1,1,-11,-22,-19,-12,-13,]),u'PRODUCT':([4,11,13,23,29,32,],[-10,-18,27,-17,-11,-19,]),u'SIGN':([0,10,11,28,30,],[5,22,5,22,22,]),u'OPEN_PAREN':([0,1,6,9,10,12,17,18,20,26,27,31,35,36,],[9,9,-16,9,-15,9,-24,-23,-14,9,9,-22,-12,-13,]),u'UINT':([0,5,7,11,16,21,22,24,],[10,-20,18,-21,28,30,31,32,]),u'CLOSE_PAREN':([2,4,8,11,13,15,19,23,29,32,33,34,],[-5,-10,-4,-18,-7,-8,29,-17,-11,-19,-9,-6,]),u'X':([6,10,17,18,],[16,21,-24,-23,]),'$end':([2,3,4,6,8,10,11,12,13,14,15,17,18,20,23,25,29,31,32,33,34,35,36,],[-5,0,-10,-16,-4,-15,-18,-3,-7,-2,-8,-24,-23,-14,-17,-1,-11,-22,-19,-9,-6,-12,-13,]),u'UNIT':([0,1,6,9,10,12,17,18,20,26,27,31,35,36,],[11,11,-16,11,-15,11,-24,-23,-14,11,11,-22,-12,-13,]),u'UFLOAT':([0,5,7,],[-21,-20,17,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {u'division_of_units':([0,9,12,26,27,],[2,2,2,2,2,]),u'main':([0,],[3,]),u'unit_with_power':([0,1,9,12,26,27,],[4,4,4,4,4,4,]),u'signed_float':([0,],[6,]),u'sign':([0,11,],[7,24,]),u'product_of_units':([0,9,12,26,27,],[8,8,8,8,8,]),u'signed_int':([10,28,30,],[20,35,36,]),u'factor':([0,],[12,]),u'unit_expression':([0,1,9,12,26,27,],[13,15,13,13,13,13,]),u'numeric_power':([11,],[23,]),u'combined_units':([0,9,12,26,27,],[14,19,25,33,34,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> main","S'",1,None,None,None),
  (u'main -> factor combined_units',u'main',2,'p_main','astropy/units/format/cds.py',164),
  (u'main -> combined_units',u'main',1,'p_main','astropy/units/format/cds.py',165),
  (u'main -> factor',u'main',1,'p_main','astropy/units/format/cds.py',166),
  (u'combined_units -> product_of_units',u'combined_units',1,'p_combined_units','astropy/units/format/cds.py',176),
  (u'combined_units -> division_of_units',u'combined_units',1,'p_combined_units','astropy/units/format/cds.py',177),
  (u'product_of_units -> unit_expression PRODUCT combined_units',u'product_of_units',3,'p_product_of_units','astropy/units/format/cds.py',183),
  (u'product_of_units -> unit_expression',u'product_of_units',1,'p_product_of_units','astropy/units/format/cds.py',184),
  (u'division_of_units -> DIVISION unit_expression',u'division_of_units',2,'p_division_of_units','astropy/units/format/cds.py',193),
  (u'division_of_units -> unit_expression DIVISION combined_units',u'division_of_units',3,'p_division_of_units','astropy/units/format/cds.py',194),
  (u'unit_expression -> unit_with_power',u'unit_expression',1,'p_unit_expression','astropy/units/format/cds.py',203),
  (u'unit_expression -> OPEN_PAREN combined_units CLOSE_PAREN',u'unit_expression',3,'p_unit_expression','astropy/units/format/cds.py',204),
  (u'factor -> signed_float X UINT signed_int',u'factor',4,'p_factor','astropy/units/format/cds.py',213),
  (u'factor -> UINT X UINT signed_int',u'factor',4,'p_factor','astropy/units/format/cds.py',214),
  (u'factor -> UINT signed_int',u'factor',2,'p_factor','astropy/units/format/cds.py',215),
  (u'factor -> UINT',u'factor',1,'p_factor','astropy/units/format/cds.py',216),
  (u'factor -> signed_float',u'factor',1,'p_factor','astropy/units/format/cds.py',217),
  (u'unit_with_power -> UNIT numeric_power',u'unit_with_power',2,'p_unit_with_power','astropy/units/format/cds.py',234),
  (u'unit_with_power -> UNIT',u'unit_with_power',1,'p_unit_with_power','astropy/units/format/cds.py',235),
  (u'numeric_power -> sign UINT',u'numeric_power',2,'p_numeric_power','astropy/units/format/cds.py',244),
  (u'sign -> SIGN',u'sign',1,'p_sign','astropy/units/format/cds.py',250),
  (u'sign -> <empty>',u'sign',0,'p_sign','astropy/units/format/cds.py',251),
  (u'signed_int -> SIGN UINT',u'signed_int',2,'p_signed_int','astropy/units/format/cds.py',260),
  (u'signed_float -> sign UINT',u'signed_float',2,'p_signed_float','astropy/units/format/cds.py',266),
  (u'signed_float -> sign UFLOAT',u'signed_float',2,'p_signed_float','astropy/units/format/cds.py',267),
]
