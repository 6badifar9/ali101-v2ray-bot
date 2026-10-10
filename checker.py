import subprocess
import tempfile
import json
import os


def test_config(config):

    try:

        cfg = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": 10808,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth"
                    }
                }
            ],
            "outbounds": [
                {
                    "protocol": "freedom",
                    "settings": {}
                }
            ]
        }


        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False
        ) as f:

            json.dump(cfg, f)

            path = f.name


        process = subprocess.Popen(
            [
                "xray",
                "run",
                "-c",
                path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


        process.wait(timeout=5)


        os.remove(path)


        if process.returncode == 0:
            return True


    except:

        return False


    return False
