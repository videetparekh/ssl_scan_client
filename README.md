# SSL Scan Client

This tool will use [SSLLabs-Scan](https://github.com/ssllabs/ssllabs-scan/) to scan the certificates of a given host and produce an Excel report. 

## Instructions

Build the Docker image with the following command:
```
docker build -t ssl_scan_client:latest .
```

Run the image with the following command:
```
docker run -it -v "$PWD":/workspace ssl_scan_client:latest
```

Inside the docker container, run:
```
ssl_scan_client --host www.elliottmgmt.com 
```
Additional arguments include `--max_retries` and `wait_time` and `--use_cached`.

At the successful completion of this script, an Excel file will be created in a folder called artifacts. It will contain information about the host, endpoints and certificates.


## Assumptions

This package is built under the following assumptions:
1. This script will be used to generate reports on daily or weekly basis (low-frequency) on a single host at a time, and as such will not serve as a bottleneck to operations at the moment (v1.0). 
2. Repeated host data is not a problem. The goal of the report is information, not a prettified report. 


## Answers to System Questions

### How would you scale this script and run it with resiliency to e.g. handle 1000s of domains?

Currently scanning a single domain takes anywhere from a minute to a few minutes. As the number of domains increases, this approach will no longer be sufficient. Two things could be done to scale, and the single-node scaling would be limited by how many calls we can make to the service before being rate-limited:

   1. Create a host queue. Iterate through the host queue to ping the service, and if the host's analysis is still in process, re-add to the host queue as a retry. 
   2. Create a thread per host and a session per thread. Unsure how memory usage would scale in practice, but would likely be more than option 1 with a smaller upside.

Both the above can have the adverse effect of the host queue becoming too big at some point, so when we spend much longer than we should waiting for a host to respond, it might make sense to start scaling horizontally and deploying multiple nodes running this script. Assignment can be random or load-balanced. 

### How would you monitor/alert on this service?

To start, it needs more robust error handling and logging. In the case of odd exceptions or errored requests, the tools should start publishing persisted logs and periodically send an email to notify the maintainer of any Error/Warning logs. 

My understanding is that tools like Prometheus+Grafana can also help observe the performance of these scripts, but I do not have practical experience to comment any further. 

### What would you do to handle adding new domains to scan or certificate expiry events from your service?

It depends on how frequently new domains are added. If these domains are added at a very low frequency, it's not a big deal to just maintain a list of domains to scan and add them one at a time, or even have script iterate over them via a bash run. This list could be local or in a cloud bucket, based on how this system is scaled. 

domains.txt
```
www.apple.com
www.google.com
```

If domains are being added on a regular basis, and we are testing 1000s of domains with this script already, there may be value in creating a client-server architecture, where a user can register/deregister a domain on the backend using the client. A load-balancer/randomizer between the client and server can decide which node to allocate the domain to.


Certificate expiry events can be automated by the the Endpoint object (preferred over Certificate object due to the scope of information it can provide about the certificate). This can also be done as above, via email or Grafana alerts. 


### After some time, your report requires more enhancements requested by the Tech team of the company. How would you handle these "continuous" requirement changes in a sustainable manner?

1. Establish a ticket mechanism of some sort. It's important to be able to prioritize and document changes to the product.
2. Build out a test suite to ensure changes don't break existing functionality.
3. Serve this via CI/CD, deploy as a pypi or as a docker image, depending on how updates are pushed to existing nodes.
