from random import random
import numpy as np
from queue import Queue
from statistics import median
from matplotlib import pyplot as plt


INF = 10000000000

mean_A = float(input("Mean interarrival time (minutes): "))
mean_S_init = float(input("Mean service time (minutes): "))
n = int(input("Number of customers: "))
uniform_A = [random() for i in range(n)]
uniform_S = [random() for i in range(n)]


def exponential_random(beta):
    return -beta*np.log(random())


def simulate(mean_A, mean_S, n, show_statistics=False):
    # A = [exponential_random(mean_A) for i in range(n)]
    # S = [exponential_random(mean_S) for i in range(n)]
    A = [-mean_A*np.log(i) for i in uniform_A]
    S = [-mean_S*np.log(i) for i in uniform_S]
    arrivals = np.cumsum(A)
    count_arrival = 0
    count_depart = 0
    queue = Queue()
    server_busy = False
    previous_time = 0
    depart_time = INF
    sum_delay = 0
    idle_time = 0
    while count_arrival < n or count_depart < n-1:
        arrival_time = arrivals[count_arrival] if count_arrival < n else INF
        if arrival_time < depart_time:
            # print(arrival_time, "arrival")
            current_time = arrival_time
            if server_busy:
                queue.put(count_arrival)
            else:
                idle_time += current_time-previous_time
                server_busy = True
                depart_time = current_time+S[count_arrival]
            count_arrival += 1
            previous_time = current_time
        else:
            # print(depart_time, "depart")
            current_time = depart_time
            if not queue.empty():
                next_customer = queue.get()
                sum_delay += current_time-arrivals[next_customer]
                depart_time += S[next_customer]
            else:
                server_busy = False
                depart_time = INF
            count_depart += 1
            previous_time = current_time
    avg_delay = sum_delay/n
    total_time = previous_time
    avg_queue_size = sum_delay/total_time
    server_utilization = (total_time-idle_time)/total_time
    print(f"Mean service time: {mean_S:.1f} minutes")
    print(f"Average delay in queue: {avg_delay:.3f} minutes")
    print(f"Average number in queue: {avg_queue_size:.3f}")
    print(f"Server utilization: {server_utilization:.3f}")
    print(f"Time simulation ended: {total_time:.3f} minutes")
    # print(f"{mean_S:.1f}, {avg_delay:.3f}, {avg_queue_size:.3f}, {server_utilization:.3f}, {total_time:.3f}, {min(A)}, {max(A):.3f}, {median(A):.3f}, {min(S)}, {max(S):.3f}, {median(S):.3f}")
    if show_statistics:
        print(f"Minimum interarrival time: {min(A)} minutes")
        print(f"Maximum interarrival time: {max(A):.3f} minutes")
        print(f"Median interarrival time: {median(A):.3f} minutes")
        print(f"Minimum service time: {min(S)} minutes")
        print(f"Maximum service time: {max(S):.3f} minutes")
        print(f"Median service time: {median(S):.3f} minutes")
        plt.figure(figsize=(13,6.5))
        plt.subplot(2,2,1)
        values, bins, _ = plt.hist(A, bins=30, weights=np.ones_like(A)/len(A))
        plt.xlabel('Interarrival time')
        plt.ylabel('Probability Density')
        plt.text(0.5, 0.5, f"$\\beta={mean_A}$",
                transform=plt.gca().transAxes)

        plt.subplot(2,2,2)
        # values, bins = np.histogram(A, bins='auto')
        plt.plot(bins[:-1], np.cumsum(values))
        plt.xlabel('Interarrival time')
        plt.ylabel('Cumulative Distribution')
        plt.text(0.5, 0.5, f"$\\beta={mean_A}$",
                transform=plt.gca().transAxes)

        plt.subplot(2,2,3)
        values, bins, _ = plt.hist(S, bins=30, weights=np.ones_like(A)/len(A))
        plt.xlabel('Service time')
        plt.ylabel('Probability Density')
        plt.text(0.5, 0.5, f"$\\beta={mean_S}$",
                transform=plt.gca().transAxes)

        plt.subplot(2,2,4)
        # values, bins = np.histogram(S, bins='auto')
        plt.plot(bins[:-1], np.cumsum(values))
        plt.xlabel('Service time')
        plt.ylabel('Cumulative Distribution')
        plt.text(0.5, 0.5, f"$\\beta={mean_S}$",
                transform=plt.gca().transAxes)
        plt.show()
    print("\n")


simulate(mean_A, mean_S_init, n, True)

for k in (0.5, 0.6, 0.7, 0.8, 0.9):
    simulate(mean_A, mean_A*k, n)
