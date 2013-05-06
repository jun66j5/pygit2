# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Import from the Standard Library
from string import hexdigits

# Import from pygit2
from _pygit2 import Repository as _Repository
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE
from _pygit2 import Reference
from pygit2.utils import all


class Repository(_Repository):

    #
    # Mapping interface
    #
    def get(self, key, default=None):
        value = self.git_object_lookup_prefix(key)
        if value is None:
            return default
        else:
            return value


    def __getitem__(self, key):
        value = self.git_object_lookup_prefix(key)
        if value is None:
            raise KeyError(key)
        return value


    def __contains__(self, key):
        return self.git_object_lookup_prefix(key) is not None


    #
    # References
    #
    def create_reference(self, name, target, force=False):
        """
        Create a new reference "name" which points to an object or to another
        reference.

        Based on the type and value of the target parameter, this method tries
        to guess whether it is a direct or a symbolic reference.

        Keyword arguments:

        force
            If True references will be overridden, otherwise (the default) an
            exception is raised.

        Examples::

            repo.create_reference('refs/heads/foo', repo.head.hex)
            repo.create_reference('refs/tags/foo', 'refs/heads/master')
            repo.create_reference('refs/tags/foo', 'bbb78a9cec580')
        """
        direct = (
            type(target) is Oid
            or (
                all(c in hexdigits for c in target)
                and GIT_OID_MINPREFIXLEN <= len(target) <= GIT_OID_HEXSZ)
            )

        if direct:
            return self.create_reference_direct(name, target, force)

        return self.create_reference_symbolic(name, target, force)


    #
    # Checkout
    #
    def checkout(self, refname=None, strategy=GIT_CHECKOUT_SAFE_CREATE):
        """
        Checkout the given reference using the given strategy, and update
        the HEAD.
        The reference may be a reference name or a Reference object.
        The default strategy is GIT_CHECKOUT_SAFE_CREATE.

        To checkout from the HEAD, just pass 'HEAD'::

          >>> checkout('HEAD')

        If no reference is given, checkout from the index.

        """
        # Case 1: Checkout index
        if refname is None:
            return self.checkout_index(strategy)

        # Case 2: Checkout head
        if refname == 'HEAD':
            return self.checkout_head(strategy)

        # Case 3: Reference
        if type(refname) is Reference:
            reference = refname
            refname = refname.name
        else:
            reference = self.lookup_reference(refname)

        oid = reference.resolve().target
        treeish = self[oid]
        self.checkout_tree(treeish, strategy)
        self.head = refname
