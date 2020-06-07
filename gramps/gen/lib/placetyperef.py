#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Place Type reference class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .datebase import DateBase
from .citationbase import CitationBase
from .refbase import RefBase
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


#-------------------------------------------------------------------------
#
# Place Type
#
#-------------------------------------------------------------------------
class PlaceTypeRef(SecondaryObject, RefBase, CitationBase, DateBase):

    def __init__(self, source=None, **kwargs):
        """
        Create a new PlaceType instance, copying from the source if present.

        :param source: source data to initialize the type
        :type source: PlaceType, or int or string or tuple
        """
        RefBase.__init__(self, source)
        DateBase.__init__(self, source)
        CitationBase.__init__(self, source)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.

        :returns: Returns the serialized tuple of data.
        :rtype: tuple
        """
        return (
            RefBase.serialize(self),
            DateBase.serialize(self),
            CitationBase.serialize(self),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.

        :param data: serialized tuple of data from an object.
        :type data: tuple
        :returns: Returns the PlaceType containing the unserialized data.
        :rtype: PlaceType
        """
        (ref, date, citation_list) = data
        RefBase.unserialize(self, ref)
        DateBase.unserialize(self, date)
        CitationBase.unserialize(self, citation_list)
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .date import Date
        return {
            "type": "object",
            "title": _("Place Type Ref"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "ref": {"type": "string",
                        "title": _("Handle"),
                        "maxLength": 50},
                "date": {"oneOf": [{"type": "null"}, Date.get_schema()],
                         "title": _("Date")},
                "citation_list": {"type": "array",
                                  "title": _("Citations"),
                                  "items": {"type": "string",
                                            "maxLength": 50}},
            }
        }

    @staticmethod
    def get_text_data_list():
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return []

    @staticmethod
    def get_text_data_child_list():
        """
        Return the list of child objects that may carry textual data.

        :returns: list of child objects that may carry textual data.
        :rtype: list
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: Returns the list of (classname, handle) tuples for referenced
                  objects.
        :rtype: list
        """
        return self.get_referenced_citation_handles()

    @staticmethod
    def get_handle_referents():
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []
