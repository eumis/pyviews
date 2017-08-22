from pyviews.application import setup_ioc, compile_app

def run_sandbox():
    setup_ioc()
    app = compile_app()
    app.run()

if __name__ == '__main__':
    run_sandbox()
