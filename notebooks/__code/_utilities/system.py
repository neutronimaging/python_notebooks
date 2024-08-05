import os
import psutil
import gc


def get_memory_usage():
    """
    Calculate the total memory usage of the current process and its children.

    Returns
    -------
    float
        Total memory usage in MB.
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_usage_mb = mem_info.rss / (1024 ** 2)  # Convert bytes to MB

    # Include memory usage of child processes
    for child in process.children(recursive=True):
        try:
            mem_info = child.memory_info()
            mem_usage_mb += mem_info.rss / (1024 ** 2)
        except psutil.NoSuchProcess:
            continue

    return mem_usage_mb


def print_memory_usage(message="", end="\n"):
    """
    Print the total memory usage.
    """
    mem_usage = get_memory_usage()

    if mem_usage < 999:
        units = 'MB'
    else:
        mem_usage /= 1000
        units = 'GB'
    print(f"{message}: total memory usage = {mem_usage:.2f}{units}", end=end)


def delete_object(object=None):
    '''delete object from memory '''
    object = None
    gc.collect()
    