from app.celery_app import celery_app

if __name__ == "__main__":
    # Windows support for celery worker
    # On Windows, we need to use 'solo' pool or 'threads' because 'prefork' doesn't work well
    import sys
    
    argv = [
        'worker',
        '--loglevel=INFO',
        '--pool=solo' if sys.platform == 'win32' else '--pool=prefork'
    ]
    
    celery_app.worker_main(argv)
