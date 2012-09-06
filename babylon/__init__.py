import hashlib
import abc

from django.core.cache import cache as django_cache
from django.db.models.signals import post_save

CACHES = {}

def register(cache, parents=None):
    """Register a cache so it can be used."""
    if not hasattr(CACHES, cache.__name__):
        CACHES[cache.__name__] = cache(CACHES)
    cache = CACHES[cache.__name__]
    if parents:
        for parent in parents:
            CACHES[parent].add_child(cache)

def get(cache, *args, **kwargs):
    """Get a cache with a certain primary instance."""
    if not str(cache):
        cache = cache.__name__
    return CACHES[cache].get(*args, **kwargs)


def register_child(cache, child):
    child = CACHES[child]
    CACHES[cache].add_child(child)


class Cache(object):
    """This is the class from which to inherit from."""
    __metaclass__ = abc.ABCMeta

    model = None
    dependencies = []
    extra_delete_args = []
    hooks = ()
    generic = False
    key_attr = 'id'
    TIMEOUT = 86400*7   

    def __init__(self, caches):
        self._parents = []
        self._children = {}
        for dependency in self.dependencies:
            cls = dependency.__name__
            if not hasattr(caches, cls):
                instance = dependency(caches)
                caches[cls] = instance
            else:
                instance = caches[cls]
            self.add_child(instance)    
        post_save.connect(self.invalidate, sender=self.model)

        self._hooks()

    def add_child(self, child):
        self._children[child.__class__] = child
        child._parents.append(self)

    def key(self, *args, **kwargs):
        key = '{}'.format(self.__class__.__name__)
        if not self.generic:
            for arg in args:
                if hasattr(arg, self.key_attr):
                    ikey = getattr(arg, self.key_attr)
                else:
                    ikey = arg
                
                key += ':{}'.format(ikey)
        return hashlib.sha1(key).hexdigest()

    def child(self, child, *args, **kwargs):
        return self._children[child].get(*args, **kwargs)

    def get(self, *args, **kwargs):
        result = django_cache.get(self.key(*args, **kwargs))
        if not result:
            result = self.generate(*args, **kwargs)
            self.set(result, *args, **kwargs)
        return result

    def set(self, data, *args, **kwargs):
        django_cache.set(self.key(*args, **kwargs),
            data, Cache.TIMEOUT)

    def delete(self, *args, **kwargs):

        for arg in self.extra_delete_args:
            django_cache.delete(self.key(*(args + (arg,)), **kwargs))
        django_cache.delete(self.key(*args, **kwargs))

    def _hooks(self):
        for model, func in self.hooks:
            post_save.connect(getattr(self, func), sender=model)

    def invalidate(self, sender, instance=None, *args, **kwargs):
        """This invalidates the cache and it's parents, and calls the
        regenerate method for all of them."""
        if instance:
            data = self.generate(instance=instance)
            if data:
                self.set(data, instance, *args, **kwargs)
            else:
                self.delete(instance, *args, **kwargs)

        elif self.model:
            for obj in self.model.objects.all():
                self.invalidate(sender, instance=obj)
        for parent in self._parents:
            parent.invalidate(None, *args, **kwargs)


    @abc.abstractmethod
    def generate(self, *args, **kwargs):
        """This method should return up to date contents of the cache."""
        return


def debug_caches():
    for k, v in CACHES.items():
        print '\n', k
        print '\tparents:', v._parents
        print '\tchildren:', v._children

