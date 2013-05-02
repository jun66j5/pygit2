# -*- coding: UTF-8 -*-
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

"""Tests for revision walk."""

import unittest

from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import utils


# In the order given by git log
log = [
    u'2be5719152d4f82c7302b1c0932d8e5f0a4a0e98',
    u'5ebeeebb320790caf276b9fc8b24546d63316533',
    u'4ec4389a8068641da2d6578db0419484972284c8',
    u'6aaa262e655dd54252e5813c8e5acd7780ed097d',
    u'acecd5ea2924a4b900e7e149496e1f4b57976e51']

REVLOGS = [
    (u'Nico von Geyso', u'checkout: moving from i18n to master'),
    (u'Nico von Geyso', u'commit: added bye.txt and new'),
    (u'Nico von Geyso', u'checkout: moving from master to i18n'),
    (u'J. David Ibañez', u'merge i18n: Merge made by recursive.'),
    (u'J. David Ibañez', u'commit: Add .gitignore file'),
    (u'J. David Ibañez', u'checkout: moving from i18n to master'),
    (u'J. David Ibañez', u'commit: Say hello in French'),
    (u'J. David Ibañez', u'commit: Say hello in Spanish'),
    (u'J. David Ibañez', u'checkout: moving from master to i18n'),
    (u'J. David Ibañez', u'commit (initial): First commit')
]


class RevlogTestTest(utils.RepoTestCase):
    def test_log(self):
        ref = self.repo.lookup_reference('HEAD')
        for i, entry in enumerate(ref.log()):
            self.assertEqual(entry.committer.name, REVLOGS[i][0])
            self.assertEqual(entry.message, REVLOGS[i][1])


class WalkerTest(utils.RepoTestCase):

    def test_walk(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log)

    def test_reverse(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME | GIT_SORT_REVERSE)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, list(reversed(log)))

    def test_hide(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.hide(u'4ec4389a8068641da2d6578db0419484972284c8')
        self.assertEqual(len(list(walker)), 2)

    def test_hide_prefix(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.hide(u'4ec4389a')
        self.assertEqual(len(list(walker)), 2)

    def test_reset(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.reset()
        out = [ x.hex for x in walker ]
        self.assertEqual(out, [])

    def test_push(self):
        walker = self.repo.walk(log[-1], GIT_SORT_TIME)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log[-1:])
        walker.reset()
        walker.push(log[0])
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log)

    def test_sort(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.sort(GIT_SORT_TIME | GIT_SORT_REVERSE)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, list(reversed(log)))

if __name__ == '__main__':
    unittest.main()
