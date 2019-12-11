from injectool import use_container
from pytest import fixture


@fixture
def container_fixture(request):
    """runs test in own dependency container"""
    with use_container() as container:
        request.cls.container = container
        yield container
