#!/usr/bin/env node

// Instructions:
// 
// 1. Get node (http://nodejs.org/#download)
//    - configure, make and make install
// 2. node load-navistore.js
//
// This example performs a micro-benchmark of Navistore, a key-value store,
// running on localhost:8888. First, it first loads 2000 objects into the store as quickly
// as possible. Then, it performs a 90% read + 10% update test at total request rate of 300 rps.
// From minutes 5-8, the read load is increased by 100 rps. The test runs for 10 minutes.


var sys = require('sys'),
    nl = require('../lib/nodeloadlib')

function navistoreUpdate(loopFun, client, url, body) {
    var req = nl.traceableRequest(client, 'GET', url, { 'host': 'localhost' });
    req.on('response', function(response) {
        if (response.statusCode != 200 && response.statusCode != 404) {
            loopFun({req: req, res: response});
        } else {
            var headers = { 
                'content-type': 'application/x-www-form-urlencoded', 
                };
            req = nl.traceableRequest(client, 'PUT', url, headers, body);
            req.on('response', function(response) {
                loopFun({req: req, res: response});
            });
            req.end();
        }
    });
    req.end();
}

var i=0;
nl.runTest({
    name: "Load Data",
    host: 'localhost',
    port: 8888,
    numClients: 20,
    numRequests: 2000,
    timeLimit: Infinity,
    successCodes: [200],
    reportInterval: 2,
    stats: ['result-codes', 'latency', 'concurrency', 'uniques'],
    requestLoop: function(loopFun, client) {
        navistoreUpdate(loopFun, client, '/key' + i++, 'original value');
    }
}, startRWTest);

function startRWTest() {
    console.log("Running read + update test.");
    
    var reads = nl.addTest({
        name: "Read",
        host: 'localhost',
        port: 8888,
        numClients: 30,
        timeLimit: 600,
        targetRps: 270,
        successCodes: [200,404],
        reportInterval: 2,
        stats: ['result-codes', 'latency', 'concurrency', 'uniques'],
        requestGenerator: function(client) {
            var url = '/key' + Math.floor(Math.random()*8000);
            return nl.traceableRequest(client, 'GET', url, { 'host': 'localhost' });
        }
    });
    var writes = nl.addTest({
        name: "Write",
        host: 'localhost',
        port: 8888,
        numClients: 5,
        timeLimit: 600,
        targetRps: 30,
        successCodes: [200],
        reportInterval: 2,
        stats: ['result-codes', 'latency', 'concurrency', 'uniques'],
        requestLoop: function(loopFun, client) {
            var url = '/key' + Math.floor(Math.random()*8000);
            navistoreUpdate(loopFun, client, url, 'updated value');
        }
    });
    
    // From minute 5, schedule 10x 10 read requests per second in 3 minutes = adding 100 requests/sec
    nl.addRamp({
        test: reads,
        numberOfSteps: 10,
        rpsPerStep: 10,
        clientsPerStep: 2,
        timeLimit: 180,
        delay: 300
    });
    
    nl.startTests();
}
