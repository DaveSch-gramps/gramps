#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015        Nick Hall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__all__ = ["PlaceTypeSelector"]

from gi.repository import Gtk
#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.placetypeselector")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import NameLang, PlaceType, PlaceGroupType, PlaceTypeRef
from gramps.gen.utils.location import placetype_from_str
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


#-------------------------------------------------------------------------
#
# PlaceTypeSelector class
#
#-------------------------------------------------------------------------
class PlaceTypeSelector():
    """ Class that sets up a comboentry for the place types """

    def __init__(self, db, combo, ptyperef, changed=None, sidebar=False):
        """
        Constructor for the PlaceTypeSelector class.

        Note:the ptyperef must be a PlaceTypeRef class, however, the .ref
        attribute must be the translated string to display.  This is best
        handled by using the prep_placetype_list_for_edit function below.

        :param combo: Existing ComboBox widget to use with has_entry=True.
        :type combo: Gtk.ComboBox
        :param ptyperef: The object to fill/modify
        :type ptyperef: PlaceTypeRef object
        :param db: the database
        :type db: based on DbReadBase, DbWriteBase
        :param changed: To update an external element when we change value
        :type callback: method
        """

        self.ptyperef = ptyperef
        self.changed = changed
        self.combo = combo
        self.db = db
        # get completion store and menu
        store, menu = get_menu(db)
        # fill out completion
        e_completion = Gtk.EntryCompletion()
        e_completion.set_model(store)
        e_completion.set_minimum_key_length(1)
        e_completion.set_text_column(0)
        entry = combo.get_child()
        entry.set_completion(e_completion)
        entry.set_text(ptyperef.ref)

        # Create a model and fill it with a two or three-level tree
        # corresponding to the menu.
        # If the active key is in an items list, the group under that parent
        # is expanded.
        # Items not under a parent group are also supported.
        store = Gtk.TreeStore(str, bool)
        for (heading, items) in menu:
            if ptyperef.ref in items or not heading:
                parent = None
            else:
                parent = store.append(None, row=[_(heading), False])
            for item in items:
                if not isinstance(item, tuple):
                    store.append(parent, row=[item, True])
                    continue
                heading_2, items_2 = item
                parent_2 = store.append(parent, row=[heading_2, False])
                for item_2 in items_2:
                    store.append(parent_2, row=[item_2, True])
        combo.set_model(store)
        combo.set_entry_text_column(0)

        combo.connect('changed', self.on_change)
        if not sidebar:
            combo.set_sensitive(not db.readonly)

    def on_change(self, combo):
        value = combo.get_child().get_text().strip()
        self.ptyperef.ref = value
        if self.changed:
            self.changed()

    def update(self):
        if self.ptyperef is not None:
            self.combo.get_child().set_text(self.ptyperef.ref)

def prep_placetype_list_for_edit(db, place):
    """
    This gets the place type information from the db and converts it into the
    translated string, replaceing the .ref in the PlaceTypeRef class.
    This allows the editors to work on the data all at once, and only
    commit the changes (both new placetypes and place changes) at the OK.
    """
    if not place.get_types():  # needed to handle 'Add' in editor
        p_type = PlaceTypeRef()
        p_type.ref = PlaceType.DATAMAP[PlaceType.UNKNOWN][0]
        place.type_list.append(p_type)
        return
    for ptype in place.get_types():
        if ptype.ref == PlaceType.CUSTOM:
            ptype.ref = ''
            continue
        p_type = db.get_placetype_from_handle(ptype.ref)
        ptype.ref = str(p_type)


def get_menu(db):
    """ This creates a place type menu structure suitable for
    StandardCustomSelector.
    It processes the DATAMAP and db data into a menu.  Both of these are
    updated from the db as needed when types or groups are changed.
    This is called by the StandardCustomSelector.

    :returns: A menu suitable for StandardCustomSelector.
    :rtype: list
    """
    menu = []   # the whole menu
    store = Gtk.ListStore(str)  # a completion list
    items = []  # list if items in a menu heading
    types = {}  # dict of key=hndl, data=PlaceTypes
    # do common items
    common_only = True
    for typ, tup in PlaceType.DATAMAP.items():
        if typ != PlaceType.CUSTOM:
            if tup[2]:  # if allowed to show in menu
                items.append(tup[0])
            store.append(row=[tup[0]])
            types[typ] = PlaceType(handle=typ, name=NameLang(value=tup[0]),
                                   group=tup[1], show=tup[2])
    for ptype in db.iter_placetypes():
        if ptype.handle in types:
            types[ptype.handle] = ptype  # override DATAMAP values
            continue
        types[ptype.handle] = ptype
        common_only = False
        store.append(row=[str(ptype)])
    if common_only:
        return (store, [(None, items)])
    menu.append((_("Common"), items))
    types = sorted([typ for typ in types.values()], key=lambda typ: str(typ))
    # assemble groups
    groups = []
    for item in db.get_placegroup_types():
        groups.append(PlaceGroupType(item))
    for item in PlaceGroupType._I2SMAP:
        if item == PlaceGroupType.CUSTOM:
            continue
        groups.append(PlaceGroupType(item))
    # now do all the other defined groups.
    for grp in groups:
        cont = False
        _mt = True
        items = []
        for typ in types:
            # exclude UNKNOWN, hidden items, and CUSTOM
            if (typ.show and typ & grp):
                items.append(str(typ))
                if typ.handle not in PlaceType.DATAMAP:
                    _mt = False
                if len(items) == 20:    # Add 'cont.' for large groups
                    if cont:
                        # translators: used to add levels to a menu
                        # as in "Items continued" but abbreviated for brevity
                        menu.append((_("%s cont.") % str(grp), items))
                    else:
                        menu.append((str(grp), items))
                    cont = True
                    items = []
        if items and not _mt:
            if cont:
                menu.append((_("%s cont.") % str(grp), items))
            else:
                menu.append((str(grp), items))
    return store, menu


def update_placetypes(db, place):
    """
    This is used to update any place type changes in the db based on the
    PlaceTypeRefs in the Place.  Used when saving in the GUI PlaceType editors.

    The refs are assumed to actualy be tuples (handl, name) during the editor
    work.  This puts them back to handles.
    """
    for p_type in place.get_types():
        p_type.ref = placetype_from_str(db, p_type.ref)
