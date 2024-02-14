import gc
import psutil
import numpy as np
import multiprocessing as mp
from time import time, sleep
from scipy.signal import welch


class ArrayContainer():
    """
    Dummy class that contains input data and random string.
    """
    def __init__(self, data):
        self.data = data
        self.random_string = "asdf"


def _dummy_function(input_data):
    data = input_data[1]
    start = time()

    calculated_data = np.array([]).reshape(0, 108)

    for chunk in data:
        sleep(0.01)
        mean = np.average(chunk.data, axis=1)
        std = np.std(chunk.data, axis=1)
        minimum = np.min(chunk.data, axis=1)
        maximum = np.max(chunk.data, axis=1)
        freq, psd = welch(x=chunk.data, fs=256, window='hann', nperseg=256,
                          noverlap=256 // 2, scaling='density')
        res = np.polynomial.polynomial.polyfit(x=freq[1:48], y=psd.T[1:48, :],
                                               deg=1)
        tmp = np.concatenate((mean, std, minimum, maximum, res[0], res[1]))
        calculated_data = np.vstack((calculated_data, tmp))

    # print(f"Function {index} took {time() - start}")

    return input_data[0], calculated_data


def _dummy_function_q(index, data, queue):
    start = time()

    calculated_data = np.array([]).reshape(0, 108)

    for chunk in data:
        sleep(0.01)
        mean = np.average(chunk.data, axis=1)
        std = np.std(chunk.data, axis=1)
        minimum = np.min(chunk.data, axis=1)
        maximum = np.max(chunk.data, axis=1)
        freq, psd = welch(x=chunk.data, fs=256, window='hann', nperseg=256,
                          noverlap=256 // 2, scaling='density')
        res = np.polynomial.polynomial.polyfit(x=freq[1:48], y=psd.T[1:48, :],
                                               deg=1)
        tmp = np.concatenate((mean, std, minimum, maximum, res[0], res[1]))
        calculated_data = np.vstack((calculated_data, tmp))

    # print(f"Function {index} took {time() - start}")

    queue.put((index, calculated_data))


def slicer(seq, n):
    result = []
    for i in range(0, len(seq), n):
        slice_item = slice(i, i + n, 1)
        result.append(seq[slice_item])
    return result


def main():
    print(f'---Initialisation---\n'
          f'No data\t\t\t\tRAM usage: '
          f'{psutil.virtual_memory()[3]/1000000000:.5f} GB')

    # 3d matrix [10*num_cores, 1000 - 3000 chunks, 18 rows, 256 features]
    input_data = [
        [ArrayContainer(np.random.rand(18, 256))
         for _ in range(np.random.randint(1000, 3000, 1)[0])]
        for _ in range((mp.cpu_count() * 10) + (mp.cpu_count() // 2))]
    print(f'Data created\t\tRAM usage: '
          f'{psutil.virtual_memory()[3]/1000000000:.5f} GB')

    print('---Start of Analysis---')
    # No multiprocessing
    print(f'No multiprocessing\t'
          f'RAM start: {psutil.virtual_memory()[3]/1000000000:.5f} GB', end='')
    start_time = time()
    results = []
    for i, matrix in enumerate(input_data):
        results.append(_dummy_function((i, matrix)))
    print(f'\tRAM end: {psutil.virtual_memory()[3]/1000000000:.5f} GB'
          f'\tRuntime: {time() - start_time:.5f} sec')
    del results
    gc.collect()

    for loop in range(3):
        print(f'Trial: {loop}')

        # Multiprocessing Manager Queue
        print(f'Manager chunked\t\t'
              f'RAM start: {psutil.virtual_memory()[3]/1000000000:.5f} GB',
              end='')
        start_time = time()
        with mp.Manager() as manager:
            queue = manager.Queue(mp.cpu_count())
            results = []
            for chunk in slicer(input_data, mp.cpu_count()):
                tmp_results = []
                for i in range(len(chunk)):
                    process = mp.Process(target=_dummy_function_q,
                                         args=(i, chunk[i], queue))
                    process.start()
                for _ in range(len(chunk)):
                    tmp_results.append(queue.get())
                results.append(sorted(tmp_results, key=lambda x: x[0]))
        print(f'\tRAM end: {psutil.virtual_memory()[3]/1000000000:.5f} GB'
              f'\tRuntime: {time() - start_time:.5f} sec')
        del results
        gc.collect()

        # Multiprocessing Pool map
        print(f'Pool map\t\t\t'
              f'RAM start: {psutil.virtual_memory()[3]/1000000000:.5f} GB',
              end='')
        start_time = time()
        with mp.Pool(processes=mp.cpu_count()) as mp_pool:
            results = mp_pool.map(_dummy_function,
                                  zip(list(range(len(input_data))),
                                      input_data))
        print(f'\tRAM end: {psutil.virtual_memory()[3]/1000000000:.5f} GB'
              f'\tRuntime: {time() - start_time:.5f} sec')
        del results
        gc.collect()

        # Multiprocessing Queue
        print(f'Queue\t\t\t\t'
              f'RAM start: {psutil.virtual_memory()[3]/1000000000:.5f} GB',
              end='')
        start_time = time()
        queue = mp.Queue(mp.cpu_count())
        results = []
        for i, data in enumerate(input_data):
            process = mp.Process(target=_dummy_function_q,
                                 args=(i, data, queue))
            process.start()
        tmp_ram = psutil.virtual_memory()[3]/1000000000
        for _ in range(len(input_data)):
            results.append(queue.get())
        results = sorted(results, key=lambda x: x[0])
        print(f'\tRAM end: {psutil.virtual_memory()[3]/1000000000:.5f} GB'
              f'\tRuntime: {time() - start_time:.5f} sec, '
              f'\tRAM processes created: {tmp_ram:.5f} GB')
        del results
        del tmp_ram
        gc.collect()

        # Multiprocessing Manager Queue no chunk
        print(f'Manager\t\t\t\t'
              f'RAM start: {psutil.virtual_memory()[3]/1000000000:.5f} GB',
              end='')
        start_time = time()
        with mp.Manager() as manager:
            queue = manager.Queue(mp.cpu_count())
            results = []
            for i, data in enumerate(input_data):
                process = mp.Process(target=_dummy_function_q,
                                     args=(i, data, queue))
                process.start()
            tmp_ram = psutil.virtual_memory()[3]/1000000000
            for _ in range(len(input_data)):
                results.append(queue.get())
            results = sorted(results, key=lambda x: x[0])
        print(f'\tRAM end: {psutil.virtual_memory()[3]/1000000000:.5f} GB'
              f'\tRuntime: {time() - start_time:.5f} sec, '
              f'\tRAM processes created: {tmp_ram:.5f} GB')
        del results
        del tmp_ram
        gc.collect()


if __name__ == "__main__":
    main()
