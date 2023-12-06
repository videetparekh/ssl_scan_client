from client.request_agent import RequestAgent
from client.classes import EndpointCollection, Endpoint
import argparse


def main():
    parser = argparse.ArgumentParser(description="SSL Scanner CLI")
    parser.add_argument("--host", type=str, required=True, help="Specify the host")
    parser.add_argument("--use_cached", action="store_true", default=False, help="Accept cached results")
    parser.add_argument("--max_retries", type=int, default=15, help="Number of retries to limit the analysis completion check to.")
    parser.add_argument("--wait_time", type=int, default=30, help="Number of seconds between each retry.")

    args = parser.parse_args()

    agent = RequestAgent()
    host_data = agent.get_host_data(args.host, use_cached=args.use_cached, max_retries=args.max_retries, wait_time=args.wait_time)

    if not host_data:
        raise ValueError(f"Your analysis could not be completed. Consider increasing the wait time and number of retries.")
    
    if host_data["status"] == "ERROR":
        raise ValueError(f"Host could not be analyzed. \nStatusMessage: {host_data['statusMessage']}")
        
    if "endpoints" in host_data:
        endpoints = host_data.pop("endpoints")
        endpoint_collection = EndpointCollection()
        for i, endpoint in enumerate(endpoints):
            endpoint_collection.add(Endpoint.from_response(endpoint, host_data))
        endpoint_collection.save()


if __name__ == "__main__":
    main()
