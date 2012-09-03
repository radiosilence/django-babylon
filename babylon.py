import hashlib

from django.core.cache import cache as django_cache
from django.db.models.signals import post_save

CACHES = {}

def register(cache):
    if not hasattr(CACHES, cache.__name__):
        CACHES[cache.__name__] = cache(CACHES)

def get(cache, instance):
    if not str(cache):
        cache = cache.__name__
    return CACHES[cache].get(instance)


class Cache(object):
    model = None
    dependencies = []
    hooks = ()
    generic = False
    TIMEOUT = 86400

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
            self._children[cls] = instance
            instance._parents.append(self)
        post_save.connect(self.invalidate, sender=self.model)

        self._hooks()

    def key(self, instance):
        key = '{}:{}'.format(self.__class__.__name__, instance.pk)
        return hashlib.sha1(key).hexdigest()

    def child(self, child, instance):
        return self._children[child].get(instance)

    def get(self, instance):
        result = django_cache.get(self.key(instance))
        if not result:
            result = self.generate(instance)
            self.set(instance, result)
        return result

    def set(self, instance, data):
        django_cache.set(self.key(instance), data, Cache.TIMEOUT)

    def _hooks(self):
        for model, func in self.hooks:
            post_save.connect(getattr(self, func), sender=model)

    def invalidate(self, sender, instance, **kwargs):
       self.set(instance, self.generate(instance))
       for parent in self._parents:
            parent.invalidate(instance)

    def generate(self, instance):
        raise Exception('You MUST override this method and return the data '
            + 'that this cache represents!')