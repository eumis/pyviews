from pyviews.application import setup_settings, compile_app

def run_sandbox():
    setup_settings()
    app = compile_app()
    app.run()

if __name__ == '__main__':
    run_sandbox()
