# -*- coding: utf-8 -*-

import copy

import numpy


def distance(p_1, p_2):
    """ Calculate the distance between two given points. """
    return numpy.sqrt(numpy.sum((p_1 - p_2)**2))

class Polymer(object):
    def __init__(self, dynamics_class, link_length, reptons,  *args, **kwargs):
        """ Initialize polymer object. 

        Arguments:
        - dynamics_class: represents polymer dynamics
        - link_length: the maxmimum repton to repton distance
        - reptons: how many reptons are there in the chain
        """

        self.dynamics = dynamics_class(link_length)
        # Reptons are represented as points in 
        # space, each repton is a row in the 
        # `self.reptons` matrix
        self.positions = numpy.zeros((reptons, self.dynamics.get_dim()))
        # let's randomize the positions
        self.__randomize_reptons()


    def __randomize_reptons(self):
        """ Randomizes repton positions """
        for position in range(1, self.positions.shape[0]):
            trans = self.dynamics.select_translation(prev_trans=None)
            t_vect = self.dynamics.translations.get(trans)
            self.positions[position] = self.positions[position-1] + t_vect

    # Not working yet! That's what you get for mangling with other people's code
    # and multiple for loops.
    def __precalculate_ladders(self):
        """ Precalculate probability ladders for a given translation. """

        self.ladders = {}
        translations = self.dynamics.get_all_translations()

        rel_positions = copy.copy(translations)
        rel_positions['same'] = numpy.array([0, 0])

        for dr_key, dr in translations.items():
            self.ladders[dr_key] = {}

            for init_dr_key, init_dr in rel_positions.items():

                self.ladders[dr_key][init_dr_key] = copy.copy(translations)

                for pulled_dr_key, pulled_dr in\
                    self.ladders[dr_key][init_dr_key].items():

                    if distance(pulled_dr, init_dr + dr) > self.dynamics.link_length:

                        del self.ladders[dr_key][init_dr_key]


class Translation(object):
    """Semi-abstract base class for possible translations sets."""

    def __init__(self, link_length, *args, **kwargs):
        self.link_length = link_length
        self.translations = self.get_all_translations()
        self.limited = self._get_limited()

    def select_translation(self, prev_trans, *args, **kwargs):
        """ Returns the translation name (a dict key) that will be choosen to update the repton position.

        """
        current_translations = self.get_translations(prev_trans)
        cumulated_probs = numpy.array([self.get_rate(translation, *args, **kwargs) for translation in current_translations]).cumsum()
        rand_num = numpy.random.uniform(0, cumulated_probs[-1])
        for prob_value, connection in zip(cumulated_probs, current_translations):
            if rand_num <= prob_value:
                return connection

    def get_rate(self, translation, *args, **kwargs):
        return getattr(self, "rate_%s" % translation)(*args, **kwargs)

    def get_translations(self, prev_trans):
        if prev_trans:
            self.limited.get(prev_trans)
        return self.translations.keys()


    def _get_limited(self):
        dd = dict([(key, [])for key in self.translations])
        for trans_from in self.translations:
            for trans_to in self.translations:
                if ((self.translations.get(trans_from) - self.translations.get(trans_to))**2).sum() <= self.link_length:
                    dd[trans_from].append(trans_to)
        return dd

    def get_dim(self):
        raise NotImplementedError

class SquareTranslation(Translation):

    def get_all_translations(self):
        return {'up': numpy.array((0, 1)),
                'right': numpy.array((1, 0)),
                'down': numpy.array((0, -1)),
                'left': numpy.array((-1, 0))}


    def get_dim(self):
        # Why use the get method instead of square brackets here?
        return self.get_all_translations().get('up').size

    def rate_up(self, *args, **kwargs):
        return 0.25

    def rate_right(self, *args, **kwargs):
        return 0.25

    def rate_left(self, *args, **kwargs):
        return 0.25

    def rate_down(self, *args, **kwargs):
        return 0.25

if __name__ == "__main__":
    # Jus a test..
    p = Polymer(SquareTranslation, 1.0, 40)
    for x, y in p.positions:
        print "%.2f\t%.2f" % (x, y)
