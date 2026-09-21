# Python 3.14 compatibility patch for Django <5.2:
# In Python 3.14+, copy(super()) returns a super proxy object rather than a new instance,
# which causes AttributeError on duplicate.dicts in django.template.context.BaseContext.__copy__.
import django.template.context


def _base_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate


django.template.context.BaseContext.__copy__ = _base_context_copy
