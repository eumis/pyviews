import injectool
from pytest import fixture


def pytest_configure(config):
    injectool.set_default_container(injectool.Container())


@fixture
def container_fixture(request):
    """runs test in own dependency container"""
    with injectool.use_container() as container:
        if request.cls:
            request.cls.container = container
        yield container
