from os.path import abspath

from injectool import add_singleton, add_resolver, SingletonResolver

from pyviews.rendering import RenderingPipeline


def use_rendering():
    add_singleton('views_folder', abspath('views'))
    add_singleton('view_ext', 'xml')
    add_resolver(RenderingPipeline, SingletonResolver())
