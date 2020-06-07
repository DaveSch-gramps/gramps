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
Name/Language class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# NameLang
#
#-------------------------------------------------------------------------
class NameLang(SecondaryObject):
    """
    NameLang class.

    This class is for keeping information about names for a language.
    """

    def __init__(self, source=None, **kwargs):
        """
        Create a new NameLang instance, copying from the source if present.
        """
        if source:
            self.value = source.value
            self.lang = source.lang
        else:
            self.value = ''
            self.lang = ''
        for key in kwargs:
            if key in ["value", "lang"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError(
                    "NameLang does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.value,
            self.lang)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.value, self.lang) = data
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
            "title": _("Name Language"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "value": {"type": "string",
                          "title": _("Text")},
                "lang": {"type": "string",
                         "title": _("Language")},
            }
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: list of all textual attributes of the object.
        :rtype: list
        """
        return [self.value]

    def is_empty(self):
        """ Determine if this NameLang is empty (not changed from initial
        value)
        """
        return (self.value == '' and self.lang == '')

    def is_equivalent(self, other):
        """
        Return if this name is equivalent, that is agrees in type and
        value, to other.

        :param other: The eventref to compare this one to.
        :type other: NameLang
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if(self.value != other.value or self.lang != other.lang):
            return DIFFERENT
        if self.is_equal(other):
            return IDENTICAL
        return EQUAL

    def __eq__(self, other):
        return self.is_equal(other)

    def __ne__(self, other):
        return not self.is_equal(other)

    def set_value(self, value):
        """
        Set the name for the NameLang instance.
        """
        self.value = value

    def get_value(self):
        """
        Return the name for the NameLang instance.
        """
        return self.value

    def set_language(self, lang):
        """
        Set the language for the NameLang instance.
        """
        self.lang = lang

    def get_language(self):
        """Return the language for the NameLang instance."""
        return self.lang
