import json
import timeit, multiprocessing
import socket
from flask import Flask, jsonify, request
from random import random
app = Flask(__name__)

HOST, PORT = "localhost", 31416

jsonfile = "statisticsdata.json" #Get JSON file
username_s = "" #Get username
count = 0   #Get count

#Calculating the PI
def partition(n, p):
    size = n // p # partition size, except for last partition
    starts = list(range(0, n+1, size))[0:p] # p start values
    stops = list(range(0, n+1, size))[1:p] + [n+1] # p stop values
    return list(zip(starts, stops))

def count_in_circle(size, results):
    count = 0
    for i in range(size):
        x = random()
        y = random()
        if x * x + y * y < 1:
            count += 1
    results.put(count)

def pi_processes(n, p):
    results = multiprocessing.Queue() # shared memory
    processes = []
    for start, stop in partition(n, p):
        size = stop - start
        process = multiprocessing.Process(
            target=count_in_circle, args=[size, results])
        processes.append(process)
    for pr in processes: pr.start()
    for pr in processes: pr.join()
    sum_ = 0
    while not results.empty():
        sum_ += results.get()
    pi = sum_ / n * 4
    return pi

#Connect to the legacy server using TCP or UDP
def legacy_server(protocol):
    if protocol == "tcp":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            pi_value = s.recv(1024).decode()
    elif protocol == "udp":
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(b'', (HOST, PORT))
            pi_value = s.recv(1024).decode()
    return pi_value

@app.post("/pi")
def do_pi():
    global count #Get global count
    with open(jsonfile, 'r') as file:   #Read the data from JSON file
        statisticsdata = json.load(file)
    count = statisticsdata.get("Count")
    data = request.get_json()   #Get data from the client
    username = data.get("username")
    if not username or not isinstance(username,str) or not username.isdigit() or len(username) != 4:    #Check the user name is correct
        return jsonify({"error": "user info error"}), 401
    password = data.get("password")
    if not password or password != username + "-pw":    #Check the password is correct
        return jsonify({"error": "user info error"}), 401
    simulations = data.get("simulations")
    if not simulations:     #Check have simulations
        return jsonify({"error": "missing field simulations"}), 400
    elif not isinstance(simulations,int) or simulations < 100 or simulations > 100000000:   #Check the simulations is correct
        return jsonify({"error": "invalid field simulations"}), 400
    concurrency = data.get("concurrency")
    if not concurrency or concurrency < 1 or concurrency > 8:   #Check the concurrency is correct
        return jsonify({"error": "invalid field concurrency"}), 400
    start_time = timeit.default_timer()
    pi = pi_processes(simulations, concurrency)   #Get the PI
    end_time = timeit.default_timer()
    execution_time = end_time - start_time    #Calculating the execution_time
    result = {"simulations":simulations, "concurrency":concurrency, "PI": pi, "execution_time": execution_time}
    count += 1  #Count how much the user request
    with open(jsonfile, 'w') as f:  #Write the data to the JSON file
        json.dump({"username":username, "Count":count}, f)
    return jsonify(result)  #Send result back to client

@app.post("/legacy_pi")
def do_legacy_pi():
    global count    #Get global count
    with open(jsonfile, 'r') as file:   #Read the data from JSON file
        statisticsdata = json.load(file)
    count = statisticsdata.get("Count")
    data = request.get_json()   #Get data from the client
    username = data.get("username")
    if not username or not isinstance(username,str) or not username.isdigit() or len(username) != 4:   #Check the user name is correct
        return jsonify({"error": "user info error"}), 401
    password = data.get("password")
    if not password or password != username + "-pw":   #Check the password is correct
        return jsonify({"error": "user info error"}), 401
    protocol = data.get("protocol")
    if not protocol:        #Check have protocol
        return jsonify({"error": "missing field protocol"}), 400
    elif  not ((protocol == "tcp") or (protocol == "udp")):     #Check the protocol is correct
        return jsonify({"error": "invalid field protocol"}), 400
    concurrency = data.get("concurrency")
    if not concurrency or concurrency < 1 or concurrency > 8:   #Check the concurrency is correct
        return jsonify({"error": "invalid field concurrency"}), 400
    start_time = timeit.default_timer()
    pi = legacy_server(protocol)    #Get the PI
    end_time = timeit.default_timer()
    execution_time = end_time - start_time    #Calculating the execution_time
    result = {"protocol":protocol, "concurrency":concurrency, "PI": pi, "execution_time": execution_time}
    with open(jsonfile, 'w') as f:     #Write the data to the JSON file
        json.dump({"username":username, "Count":count}, f)
    return jsonify(result)      #Send result back to client

@app.post("/statistics")
def do_statistics():
    global count    #Get global count
    global username_s   #Get global username_s
    with open(jsonfile, 'r') as file:   #Read the data from JSON file
        statisticsdata = json.load(file)
    count = statisticsdata.get("Count")
    username_s = statisticsdata.get("username")
    data = request.get_json()   #Get data from the client
    username = data.get("username")
    if not username or not isinstance(username,str) or not username.isdigit() or len(username) != 4:    #Check the user name is correct
        return jsonify({"error": "user info error"}), 401
    password = data.get("password")
    if not password or password != username + "-pw":    #Check the password is correct
        return jsonify({"error": "user info error"}), 401
    result = {"username":username_s, "Count":count}
    return jsonify(result)  #Send result back to client

if __name__ == "__main__":
    app.run()