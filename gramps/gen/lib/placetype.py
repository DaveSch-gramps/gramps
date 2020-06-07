#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015,2017  Nick Hall
# Copyright (C) 2019       Paul Culley
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

"""
Place Type class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .tableobj import TableObject
from .placegrouptype import PlaceGroupType as p_g
from .namelang import NameLang
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


DM_NAME = 0                 # index into DATAMAP tuple
DM_GRP = 1                  # index into DATAMAP tuple
DM_SHOW = 2                 # index into DATAMAP tuple


#-------------------------------------------------------------------------
#
# Place Type
#
#-------------------------------------------------------------------------
class PlaceType(TableObject):
    """
    Place Type class.

    This class is for keeping information about place types.
    The place type is referenced via a 'handle' similar to other Gramps
    TableObject types.
        The handle must be unique, but is not constructed in the usual way.
        * For original Gramps place types the handle is the XML string of the
          type.
        * For types created from an external system, (e.g. GOV types) the
          handle should be clearly identifiable as belonging to that system.
          For GOV we will use GOV_xxx where xxx is the number assigned to the
          GOV place type
        * For manually entered fully custom types, we will use the initially
          entered name string, modified if necessary to make it unique.

    The types are further categorized into groups.  Some groups are core,
    others are assigned by the user or addon.

    Types can have several names, associated with each language, or no language
    which will be used if no language match is available.

    Types can be hidden from the GUI type selector menu

    Types can have a color, used in Geography views..

    Types can also have associated Countries, unused for now.
    """
    # CUSTOM is also a seperator between numbered and completely custom places
    CUSTOM = "CUSTOM"       # 0 original value
    UNKNOWN = "Unknown"     # -1 original value
    COUNTRY = "Country"     # 1
    STATE = "State"         # 2
    COUNTY = "County"       # 3
    CITY = "City"           # 4
    PARISH = "Parish"       # 5
    LOCALITY = "Locality"   # 6
    STREET = "Street"       # 7
    PROVINCE = "Province"   # 8
    REGION = "Region"       # 9
    DEPARTMENT = "Department"       # 10
    NEIGHBORHOOD = "Neighborhood"   # 11
    DISTRICT = "District"   # 12
    BOROUGH = "Borough"     # 13
    MUNICIPALITY = "Municipality"   # 14
    TOWN = "Town"           # 15
    VILLAGE = "Village"     # 16
    HAMLET = "Hamlet"       # 17
    FARM = "Farm"           # 18
    BUILDING = "Building"   # 19
    NUMBER = "Number"       # 20

    _DEFAULT = UNKNOWN
    _CUSTOM = CUSTOM

    # The data map (dict) contains a tuple with key as a type (int)
    #   text (string) - the users name for this type
    #   groups (int) bit field describing the groups the type belongs to.
    #   visible (bool) - shows up in menu if true
    # the values shown here (with positive keys) are the standard ones.
    # This is updated with user or app level changes and is stored in the db
    # as metadata.
    # The items with positive keys, cannot be deleted via the GUI
    # Note: these must remain in the original 
    DATAMAP = {
        UNKNOWN : (_("Unknown"), p_g(p_g.NONE), True),
        CUSTOM : ('', p_g(p_g.NONE), False),
        COUNTRY : (_("Country"), p_g(p_g.COUNTRY), True),
        STATE : (_("State"), p_g(p_g.REGION), True),
        COUNTY : (_("County"), p_g(p_g.REGION), True),
        CITY : (_("City"), p_g(p_g.PLACE), True),
        PARISH : (_("Parish"), p_g(p_g.REGION), True),
        LOCALITY : (_("Locality"), p_g(p_g.PLACE), True),
        STREET : (_("Street"), p_g(p_g.NONE), True),
        PROVINCE : (_("Province"), p_g(p_g.REGION), True),
        REGION : (_("Region"), p_g(p_g.REGION), True),
        DEPARTMENT : (_("Department"), p_g(p_g.REGION), True),
        NEIGHBORHOOD : (_("Neighborhood"), p_g(p_g.PLACE), True),
        DISTRICT : (_("District"), p_g(p_g.PLACE), True),
        BOROUGH : (_("Borough"), p_g(p_g.PLACE), True),
        MUNICIPALITY : (_("Municipality"), p_g(p_g.PLACE), True),
        TOWN : (_("Town"), p_g(p_g.PLACE), True),
        VILLAGE : (_("Village"), p_g(p_g.PLACE), True),
        HAMLET : (_("Hamlet"), p_g(p_g.PLACE), True),
        FARM : (_("Farm"), p_g(p_g.PLACE), True),
        BUILDING : (_("Building"), p_g(p_g.BUILDING), True),
        NUMBER : (_("Number"), p_g(p_g.NONE), True),
    }

    # create a name to handle dict from the DATAMAP
    str_to_handle = {}
    # include translated names, checking that they are unique,
    # and adjusting if not
    for (hndl, tup) in DATAMAP.items():
        cnt = 1
        while tup[0] in str_to_handle:
            tr_name = "%s_%d" % (tup[0], cnt)
            tup = DATAMAP[hndl] = (tr_name, tup[1], tup[2])
            cnt += 1
        str_to_handle[tup[0]] = hndl

    def __init__(self, **kwargs):
        """
        Create a new PlaceType instance, copying from the source if present.

        :param source: source data to initialize the type
        :type source: PlaceType, or int or string or tuple
        """
        self.handle = self.UNKNOWN
        self.name_list = []
        self.country_list = []
        self.desc = ''
        self.color = "#0000FFFF0000"  # Green
        self.group = p_g(p_g.PLACE)
        self.show = True
        self.change = 0
        for key in kwargs:
            if key == 'name':
                self.add_name(kwargs[key])
                continue
            if key == 'country_list':
                self.add_country(kwargs[key])
                continue
            if key in ["handle", "color", "group", "desc", "show"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError(
                    "PlaceType does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.

        :returns: Returns the serialized tuple of data.
        :rtype: tuple
        """
        return (self.handle,
                [item.serialize() for item in self.name_list],
                [item.serialize() for item in self.country_list],
                self.desc,
                self.color,
                self.group,
                self.show,
                self.change)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.

        :param data: serialized tuple of data from an object.
        :type data: tuple
        :returns: Returns the PlaceType containing the unserialized data.
        :rtype: PlaceType
        """
        (self.handle, names, countries, self.desc, self.color, self.group,
         self.show, self.change) = data
        self.name_list = [NameLang().unserialize(name) for name in names]
        self.country_list = [NameLang().unserialize(obj) for obj in countries]
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Place Type"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "handle": {"type": "string",
                           "maxLength": 50,
                           "title": _("Handle")},
                "name_list": {"type": "array",
                              "items": NameLang.get_schema(),
                              "title": _("Names")},
                "country_list": {"type": "array",
                                 "items": NameLang.get_schema(),
                                 "title": _("Countries")},
                "desc": {"type": "string",
                         "maxLength": 50,
                         "title": _("Description")},
                "color": {"type": "string",
                          "maxLength": 13,
                          "title": _("Color")},
                "group": {"type": "array",
                          "items": p_g.get_schema(),
                          "title": _("Group")},
                "show": {"type": "integer",
                         "minimum": 0,
                         "title": _("Show")},
                "change": {"type": "integer",
                           "title": _("Last changed")}
            }
        }

#     @classmethod
#     def reset_to_defaults(cls):
#         """ Reset the maps to their default value
#         """
#         cls.DATAMAP = dict(cls._DATAMAP)
#         cls.status = 0

#     def is_equivalent(self, other):
#         """
#         Return if this PlaceType is equivalent, that is agrees in type and
#         date, to other.
# 
#         :param other: The PlaceType to compare this one to.
#         :type other: PlaceType
#         :returns: Constant indicating degree of equivalence.
#         :rtype: int
#         """
#         if self.handle != other.value or self.date != other.date:
#             return DIFFERENT
#         if self.is_equal(other):
#             return IDENTICAL
#         return EQUAL

    def __eq__(self, other):
        if isinstance(other, int):
            return self.handle == other
        return self.is_equal(other)

    def __ne__(self, other):
        if isinstance(other, int):
            return self.handle != other
        return not self.is_equal(other)

    def __str__(self):
        """ return the name of the placetype appropriate to the current
        language"""
        lang = glocale.lang[0:2]
        if self.name_list:
            name = self.name_list[0]
        else:
            name = ''
        for item in self.name_list:
            if item.lang == lang:
                return item.value
            if item.lang == '':
                name = item.value
        return name

#     def __int__(self):
#         return self.handle

    def is_empty(self):
        """ Determine if this PlaceType is empty (not changed from initial
        value)
        """
        return (self.handle == PlaceType.UNKNOWN)

#     def is_custom(self):
#         """ This type is a temporary value assigned to indicate that the type
#         is stored as a string in self.__string
# 
#         :returns: True if the temp value is in use.
#         :rtype: bool
#         """
#         return self.handle == self.CUSTOM
# 
#     def is_manual_custom(self):
#         """ This type is assigned manually; the type number should not be
#         exported in XML as it might conflict with other manual assignements
#         when importing from other databases.  In this case the types are
#         exported by type name and on import are either matched by name or
#         created anew.
# 
#         :returns: True if the value is manualy assigned.
#         :rtype: bool
#         """
#         return self.handle < self.CUSTOM
# 
#     def is_numbered(self):
#         """ This type is either a fixed Gramps type, or can reasonably be
#         expected to have a custom type number that would not change its
#         name or meaning.  An example would be GOV types.
# 
#         :returns: True if the value is in the numbered region.
#         :rtype: bool
#         """
#         return self.handle > self.CUSTOM
# 
#     def is_custom_numbered(self):
#         """ This type can reasonably be expected to have a custom type number
#         that would not change its name or meaning.  An example would be
#         GOV types.
# 
#         :returns: True if the value is in the numbered region.
#         :rtype: bool
#         """
#         return self.handle > self.CUSTOM and self.handle < 0

    def __and__(self, other):
        """ This allows the '&' between the PlaceType and PlaceGroupType
        for testing group membership.

        :param other: the PlaceType int value to compare.
        :type other: int
        :returns: int value of bitwise and, can treat as bool for testing.
        :rtype: int
        """
        return self.group == other

# 
#     def xml_str(self):
#         """
#         Return the untranslated string (e.g. suitable for XML) corresponding
#         to the type.
# 
#         :returns: XML string.
#         :rtype: string
#         """
#         if self.handle == self.CUSTOM:
#             return ''
#         if self.handle in self._I2EMAP:
#             return self._I2EMAP[self.handle]
#         return self.DATAMAP.get(self.handle,
#                                 self.DATAMAP[self.UNKNOWN])[DM_NAME]
# 
#     def set(self, value):
#         """
#         Set the value/string properties from the passed in value.
# 
#         :param value: the PlaceType, tuple, int or str to set.
#         :type value: PlaceType, tuple, int or string
#         """
#         if isinstance(value, tuple):
#             # tuple len==1 known type (val,)
#             # tuple len==2 known type if not CUSTOM (val, strg)
#             # tuple len==2 new type if CUSTOM grouped as G_PLACE
#             val = self._DEFAULT
#             if value:
#                 val = value[0]
#                 if len(value) == 2:
#                     if val == self.CUSTOM and value[1]:
#                         self.__string = value[1]        # save for later
#                         return
#                 if val in self.DATAMAP:
#                     self.handle = val
#                     return
#             self.handle = val
#             if val > self.CUSTOM:  # is it one of the GOV or standard types?
#                 # Add to the place types.
#                 name = self.valid_name(value[1], p_type=val)
#                 self.DATAMAP[val] = (name, (
#                     value[2] if len(value) == 3 else self.G_PLACE), True)
#                 if not self.status:
#                     self.status = 1
#         elif isinstance(value, int):
#             self.handle = value
#         elif isinstance(value, self.__class__):
#             self.handle = value.value
#         elif isinstance(value, str):
#             self.set_from_xml_str(value)
#         else:
#             raise ValueError
# 
#     def register_custom(self):
#         """
#         Save the manual CUSTOM value in our datamap with a G_PLACE
#         grouping and a newly chosen negative int value.
#         We assume that the string is not already in the datamap, which should
#         be the case if using the usual MonitoredDataType combo to create the
#         place type.
#         We don't save changes here, so must save in db elsewhere.
#         """
#         self.handle = self.new()
#         name = self.valid_name(self.__string, p_type=self.handle)
#         self.DATAMAP[self.handle] = (name, self.G_PLACE, True)
#         if not self.status:
#             self.status = 1
# 
#     def get(self):
#         """ supports MonitoredDataType
# 
#         :returns: self (PlaceType).
#         :rtype: PlaceType
#         """
#         return self
    def add_name(self, name):
        """
        Add a name to the PlaceType

        :param name: name and language to add.
        :type name: NameLang
        """
        if name not in self.name_list:
            self.name_list.append(name)

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this PlaceType.

        Lost: type, date of acquisition.

        :param acquisition: the PlaceType to merge with.
        :type acquisition: PlaceType
        """
        self._merge_citation_list(acquisition)
        for name in acquisition.name_list:
            self.add_name(name)

#     @classmethod
#     def new(cls):
#         """
#         Pick a new type value to use in assigning a place type
#         It should not conflict with currently assigned types
#         Will start with largest number that fits in single int symbol
#         and work down.
# 
#         :returns: a type value for potential use as the int PlaceType.
#         :rtype: int
#         """
#         for val in range(-0x3fffffff, cls.CUSTOM, 1):
#             if val not in cls.DATAMAP:
#                 return val
#         raise ValueError

    def get_custom(self):
        """ for compatibility with GrampsType

        :returns: The CUSTOM type value.
        :rtype: int
        """
        return self.CUSTOM

#     @classmethod
#     def add_group(cls, name):
#         """ adds a new group, usually based on hierarchy types.  Only supports
#         30 - (standard base groups) possible additional groups.
#         We don't save changes here, so must save in db elsewhere.
#         If group already exists, no change
# 
#         :param name: the new group name.
#         :type p_type: string
#         :returns: the group number
#         :rtype: int
#         """
#         nam_low = name.lower()
#         for typ, tup in cls.GROUPMAP.items():
#             if nam_low == tup[0].lower() or nam_low == tup[1].lower():
#                 return typ
#         for gnum in range(cls.G_OTHER + 1, 30):
#             if (1 << gnum) not in cls.GROUPMAP:
#                 cls.GROUPMAP[1 << gnum] = (name, name)
#                 if not cls.status:
#                     cls.status = 1
#                 return 1 << gnum
#         raise AttributeError
# 
#     @classmethod
#     def set_db_data(cls, data):
#         """
#         loads customized place type data from the db
#         If the current state is default, then loads it all.
#         Otherwise the db place type data is merged into the current state;
#         this happens when we load a second db.
# 
#         :param data: The customized place type data
#         :type data: tuple
#         """
#         if not data:
#             return
#         if not cls.status:
#             # default state
#             cls.DATAMAP = data[0]
#             cls.GROUPMAP = data[1]
#             cls.status = 1
#             return
#         groupmap = data[1]
#         datamap = data[0]
#         db_group_to_group = {}
#         for typ, tup in groupmap.items():
#             # add/merge the groups, saving the new group numbers in dict
#             db_group_to_group[typ] = cls.add_group(tup[1])
#         for typ, ntup in datamap.items():
#             # add/merge the types
#             if typ > PlaceType.CUSTOM:
#                 # type number is good
#                 if typ in cls.DATAMAP:
#                     continue  # found it, no change to DATAMAP
#                 n_typ = typ
#             else:
#                 # type number is invalid, use name
#                 _ok = False
#                 for tup in cls.DATAMAP.values():
#                     if ntup[DM_NAME].lower() == tup[DM_NAME].lower():
#                         _ok = True  # found it, need to continue outer loop
#                         break
#                 else:
#                     # must be new type
#                     n_typ = cls.new()
#                 if _ok:     # if we found the type, no change to DATAMAP
#                     continue
#             name = cls.valid_name(ntup[DM_NAME], p_type=n_typ)
#             groups = 0  # start with no groups
#             for grp in db_group_to_group:
#                 if grp & ntup[DM_GRP]:  # if type is member of group
#                     # set our group with our group # as converted from db #
#                     groups |= db_group_to_group[grp]
#             cls.DATAMAP[n_typ] = (name, groups, True)
#         cls.status += 1  # keep track of state, number of open dbs
# 
#     @classmethod
#     def get_db_data(cls, close):
#         """
#         Gets customized place type data into a tuple for the db
# 
#         :param close: True if the db is closing
#         :type close: bool
#         :returns: tuple object to store in db metadata
#         :rtype: tuple
#         """
#         ret_data = (cls.DATAMAP, cls.GROUPMAP)
#         if close:
#             if cls.status:
#                 cls.status -= 1
#                 if cls.status == 0:
#                     PlaceType.reset_to_defaults()
#         return ret_data
# 
#     value = property(__int__, set, None, "Returns or sets integer value")
