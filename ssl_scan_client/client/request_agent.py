import requests
import time


class RequestAgent:
    """
    Manages host requests to the SSL Labs API.
    """
    
    def get_opts(self, host, use_cached=False, retry_mode=False):
        """
        Generate Parameters for GET https://api.ssllabs.com/api/v2/analyze
        """

        baseline_opts = {"all": "on", "host": host}
        if retry_mode:
            pass
        elif use_cached:
            baseline_opts.update({"fromCache": True})
        elif not use_cached and not retry_mode:
            baseline_opts.update({"startNew": True})
        return baseline_opts

    def get_host_data(self, host, use_cached=False, max_retries=15, wait_time=30) -> dict:
        """
        This function executes the analysis and returns results once complete. 
        GET https://api.ssllabs.com/api/v2/analyze

        Parameters
        ----------
        host: str
            URL of the domain to be analysed
        use_cached: bool
            When enabled, cached results are prioritized over a brand new assessment.
        max_retries: int
            After how many attempts to assume the non-completion of the analysis and return.
        wait_time: int
            How many seconds we want to wait between retries.

        Returns
        -------
        dict
            Analysis of host.
        """
        
        call = "https://api.ssllabs.com/api/v2/analyze"
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'ElliottMgmt Agent'})
        first_run_params = self.get_opts(host, use_cached=use_cached)
        retry = 0

        print(f"Initiating Analysis of {host}.")
        if use_cached:
            print("Caching Mode enabled.")

        response = requests.get(call, first_run_params, headers=headers)
        while retry < max_retries:
            stat_code = response.status_code
            response = response.json()

            if stat_code == 200:
                api_status = response["status"]
                if api_status in ["READY", "ERROR"]:
                    print("Host Analysis completed.")
                    return response
                else:
                    time.sleep(wait_time)

            retry += 1
            print(f"Checking analysis status. Retry {retry} of {max_retries}")
            response = requests.get(call, self.get_opts(host, retry_mode=True), headers=headers)

        return None
