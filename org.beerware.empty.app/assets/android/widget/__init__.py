def __getattr__(*argv):
    print(argv)
    return __import__(__name__)
