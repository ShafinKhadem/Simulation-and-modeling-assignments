# %%
import csv
import numpy as np
from collections import deque, Counter
from enum import Flag, auto
import warnings

np.random.seed(10)
INF = 10000000000

simulation_time = 10000
cnt_floor = 12
cnt_elevator = 4
elevator_capacity = 12
max_batch_size = 6
hold_time = 15
interfloor_time = 5
time_to_open = 3
time_to_close = 3
time_to_embark = 3
time_to_disembark = 3
mean_interarrival_minute = 1.5

# simulation_time = int(input('simulation_time: '))
# cnt_floor = int(input('cnt_floor: '))
# cnt_elevator = int(input('cnt_elevator: '))
# elevator_capacity = int(input('elevator_capacity: '))
# max_batch_size = int(input('max_batch_size: '))
# hold_time = int(input('hold_time: '))
# interfloor_time = int(input('interfloor_time: '))
# time_to_open = int(input('time_to_open: '))
# time_to_close = int(input('time_to_close: '))
# time_to_embark = int(input('time_to_embark: '))
# time_to_disembark = int(input('time_to_disembark: '))
# mean_interarrival_minute = float(input('mean_interarrival_minute: '))


def rand_interarrival_time():
    return int(np.random.exponential(mean_interarrival_minute) * 60)


def rand_batch_size():
    return np.random.binomial(max_batch_size - 1, 0.5) + 1


def rand_destinations(size):
    return np.random.randint(2, cnt_floor + 1, size).tolist()


# %%
def simulate():
    cnt_customer = 0
    queue_lengths = []
    delay_times = []
    elevator_time = []
    delivery_time = []
    load_size = [0] * cnt_elevator
    available_time = [0] * cnt_elevator
    operation_time = [0] * cnt_elevator
    cnt_max_load = [0] * cnt_elevator
    cnt_stop = [0] * cnt_elevator

    arrival_time = []
    destinations = []

    queue = deque()
    next_queue_time = 0
    availability = [True] * cnt_elevator
    latest_customer_entry_time = [-INF] * cnt_elevator
    next_ground_open_time = [0] * cnt_elevator
    passengers = [[] for i in range(cnt_elevator)]
    pending_entries = [deque() for i in range(cnt_elevator)]

    next_arrival_time = rand_interarrival_time()

    def elevator_journey(elevator_idx, tik):
        availability[elevator_idx] = False
        latest_customer_entry_time[elevator_idx] = -INF

        def forward_end(tiks):
            nonlocal tik
            tik += tiks
            operation_time[elevator_idx] += tiks
            return tik > simulation_time

        if forward_end(time_to_close):
            return
        customers = passengers[elevator_idx]
        load_size[elevator_idx] += len(customers)
        cnt_max_load[elevator_idx] += len(customers) == elevator_capacity
        disembarked = 0
        nonlocal cnt_customer
        for floor in range(2, cnt_floor + 1):
            if forward_end(interfloor_time):
                return
            opened = False
            for customer in customers:
                if destinations[customer] == floor:
                    if not opened:
                        if forward_end(time_to_open):
                            return
                        cnt_stop[elevator_idx] += 1
                        opened = True
                    if forward_end(time_to_disembark):
                        return
                    delivery_time[customer] = tik - arrival_time[customer]
                    elevator_time[customer] = delivery_time[customer] - \
                        delay_times[customer]
                    cnt_customer += 1
                    disembarked += 1
            if opened:
                if forward_end(time_to_close):
                    return
            if disembarked == len(customers):
                time_to_ground = interfloor_time * (floor - 1)
                if forward_end(time_to_ground):
                    return
                break
        customers.clear()
        next_ground_open_time[elevator_idx] = tik + time_to_open

    for clock in range(1, simulation_time + 1):
        if clock == next_arrival_time:
            next_arrival_time = clock + rand_interarrival_time()
            arrived_before = len(destinations)
            batch_size = rand_batch_size()
            arrival_time += [clock] * batch_size
            elevator_time += [0] * batch_size
            delivery_time += [0] * batch_size
            destinations += rand_destinations(batch_size)
            for i in range(batch_size):
                customer = arrived_before + i
                for i in range(cnt_elevator):
                    if not queue and availability[i]:
                        enterPassenger(i, customer)
                        break
                else:
                    queue.append(customer)
        if queue and next_queue_time <= clock:
            for i in range(cnt_elevator):
                if availability[i]:
                    next_queue_time = clock + time_to_embark
                    pending_entries[i].append(next_queue_time)
                    break

        for i in range(cnt_elevator):
            for entry in pending_entries[i]:
                enterPassenger(i, queue.popleft())
            pending_entries[i].clear()

        def enterPassenger(elevator_idx, passenger):
            passengers[elevator_idx].append(passenger)
            if len(passengers[elevator_idx]) == elevator_capacity:
                availability[elevator_idx] = False
            latest_customer_entry_time[elevator_idx] = clock
            delay_times.append(clock - arrival_time[passenger])

        queue_lengths.append(len(queue))
        for i in range(cnt_elevator):
            if latest_customer_entry_time[i] == clock - hold_time:
                elevator_journey(i, clock)
            available_time[i] += availability[i]

            if next_ground_open_time[i] == clock:
                availability[i] = True

    return {
        'cnt_customer': cnt_customer,
        'max_queue_length': max(queue_lengths),
        'avg_queue_length': np.mean(queue_lengths),
        'max_delay_time': max(delay_times or [0]),
        'avg_delay_time': np.mean(delay_times or [0]),
        'max_elevator_time': max(elevator_time or [0]),
        'avg_elevator_time': np.mean([i for i in elevator_time if i] or [0]),
        'max_delivery_time': max(delivery_time or [0]),
        'avg_delivery_time': np.mean([i for i in delivery_time if i] or [0]),
        'load_size': np.array(load_size),
        'operation_time': np.array(operation_time),
        'avaliable_time': np.array(available_time),
        'number_of_max_loads': np.array(cnt_max_load),
        'number_of_stops': np.array(cnt_stop)
    }


# %%
output = csv.DictWriter(open('output.csv', "w", newline=''),
                        quoting=csv.QUOTE_NONNUMERIC,
                        fieldnames=[
                            'simulation_no',
                            'cnt_customer',
                            'max_queue_length',
                            'avg_queue_length',
                            'max_delay_time',
                            'avg_delay_time',
                            'max_elevator_time',
                            'avg_elevator_time',
                            'max_delivery_time',
                            'avg_delivery_time',
                            'load_size',
                            'operation_time',
                            'avaliable_time',
                            'number_of_max_loads',
                            'number_of_stops',
                        ])
output.writeheader()
cnt_simulate = 10
sum_result = Counter()
for i in range(cnt_simulate):
    result = simulate()
    result['simulation_no'] = i + 1
    output.writerow(result)
    sum_result.update(result)
avg_result = {k: v / cnt_simulate for k, v in sum_result.items()}
avg_result['simulation_no'] = 'average'
output.writerow(avg_result)
print(avg_result)
