# Ionizer Interface

`IonizerServer` is a specialized server designed to extend `pydase` applications for seamless integration with the Ionizer system. By acting as a bridge between your `pydase` service and Ionizer, this server ensures that changes or events in your service are communicated between pydase and Ionizer in real-time.

## How to Use

To deploy `IonizerServer` alongside your service, follow these steps:

```python
from pydase_service_base.ionizer_interface import IonizerServer

class YourServiceClass:
    # your implementation...


if __name__ == "__main__":
    # Instantiate your service
    service = YourServiceClass()

    # Start the main pydase server with IonizerServer as an additional server
    Server(
        service,
        additional_servers=[
            {
                "server": IonizerServer,
                "port": 8002,
                "kwargs": {},
            }
        ],
    ).run()
```

This sets up your primary `pydase` server with `YourServiceClass` as the service. Additionally, it integrates the `IonizerServer` on port `8002`.

For further details, issues, or contributions, please refer to the [official documentation](https://pydase.readthedocs.io/en/latest/) or contact the maintainers.
