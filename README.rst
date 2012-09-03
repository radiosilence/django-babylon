django-babylon
==============

Ok so I figured cache invalidation was a royal pain in the arse, and that one
of the current best ways is to cache infinitely and only invalidate when the
associated data is stale. But! How do we know when it is stale?

Effectively the point of this project is to give you a way to formally define
caches with meta information such as other caches they depend on (so you can
do the "Russian Doll" style caching that 37 Signals went on about), models that
caches directly depend upon, other models that might invalidate the cache, and
other useful stuff.

There are several other concepts that I thought up too, such as "hooks".

Of course I will expand the documentation because this project is blatantly
really useful for defining a decent caching scheme instead of shitting out some
half baked attempt that confuses people and gives everyone stale data all the
time.

To-Do
-----

 * Template tags to access HTML templates.
 * Documentation
 * Tests
 * Sorting out how best to trick fucking python-memcached into doing infinite
   caching.