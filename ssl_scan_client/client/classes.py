from dataclasses import asdict, dataclass, field
import datetime as dt
from typing import List
from pathlib import Path
import pandas as pd
from flatten_dict import flatten


@dataclass
class Certificate:
    subject: str
    common_names: field(default_factory=list)
    alt_names: field(default_factory=list)
    label: str
    not_before: str
    not_after: str
    revocation_status: int
    crl_revocation_status: int
    ocsp_revocation_status: int
    issues: int

    @classmethod
    def from_response(cls, obj: dict):
        """
        Extracts only relevant information from the full object dict.
        """
        return cls(
            obj["subject"],
            obj["issuerLabel"],
            obj["commonNames"],
            obj["altNames"],
            dt_int_to_str(obj["notBefore"]),
            dt_int_to_str(obj["notAfter"]),
            obj["revocationStatus"],
            obj["crlRevocationStatus"],
            obj["ocspRevocationStatus"],
            obj["issues"],
        )


@dataclass
class Endpoint:
    host_name: str
    host_status: str
    host_start_time: str
    host_end_time: str
    ip: str
    status: str
    grade: str
    certificate: Certificate

    @classmethod
    def from_response(cls, endpoint_dict: dict, host_dict: dict):
        """
        Extracts only relevant information from the full object dict.
        """

        cert = None
        if "details" in endpoint_dict and "cert" in endpoint_dict["details"]:
            cert = Certificate.from_response(endpoint_dict["details"]["cert"])    

        return cls(
            host_dict["host"],
            host_dict["status"],
            dt_int_to_str(host_dict["startTime"]),
            dt_int_to_str(host_dict["testTime"]),
            endpoint_dict["ipAddress"],
            endpoint_dict["statusMessage"].toupper(),
            endpoint_dict["grade"],
            cert,
        )


@dataclass
class EndpointCollection:
    endpoints: List[Endpoint] = field(default_factory=list)

    def add(self, endpoint: Endpoint) -> None:
        """
        Add endpoints here to generate a report of the full collection of endpoints. 
        """
        self.endpoints.append(endpoint)

    def save(self) -> None:
        path = Path("./artifacts")
        path.mkdir(exist_ok=True)

        if path.is_dir():
            dtstr = dt.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
            path = path / f"endpoint_scan_{dtstr}.xlsx"

        endpoints = [flatten(asdict(endpoint), reducer="dot") for endpoint in self.endpoints]

        df = pd.DataFrame(endpoints)
        df.to_excel(str(path), index=False)
        print(f"Report saved to {path}")


def dt_int_to_str(dt_int) -> str:
    return str(dt.datetime.fromtimestamp(dt_int / 1000.0))
