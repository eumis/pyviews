from pyviews.application import setup_ioc, setup_injection, compile_app

def run_sandbox():
    setup_ioc()
    setup_injection()
    app = compile_app()
    app.run()

if __name__ == '__main__':
    run_sandbox()
