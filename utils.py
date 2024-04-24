def timer(func):
    """
    To check elasped execution time of given func.
    
    """
    import time

    def sec2timestr(t):
        ms = int(t * 1000) % 1000
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
        return f"{time_str}.{ms}"
    
    def wrapper(*args, **kwargs):
        st = time.time()
        print(f"[Start Time] ", sec2timestr(st))
        result = func(*args, **kwargs)
        et = time.time()
        print(f"[Finish Time]", sec2timestr(et))
        print(f"Function '{func.__name__}' executed in {et-st:.4f} seconds")
        return result
    return wrapper


def load_pickle(filename):
    try:
        with open(filename, 'rb') as file:
            import pickle
            data = pickle.load(file)
    except FileNotFoundError:
        data = {}
    return data


def save_pickle(data, filename):
    with open(filename, 'wb') as file:
        import pickle
        pickle.dump(data, file)