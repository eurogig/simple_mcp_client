Welcome to Simple MCP Client's documentation!
==============================================

A simple and lightweight client implementation for the Model Context Protocol (MCP).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   contributing

Features
--------

* Easy-to-use MCP client implementation
* Command-line interface for quick interactions
* Extensible architecture for custom integrations
* Comprehensive test coverage
* Modern Python packaging with ``pyproject.toml``

Quick Start
----------

.. code-block:: python

    from simple_mcp_client import MCPClient

    # Create a client
    client = MCPClient("http://localhost:8000")

    # Connect to the server
    client.connect()

    # Send a request
    response = client.send_request("tools/list")
    print(response)

Installation
-----------

.. code-block:: bash

    pip install simple-mcp-client

For development installation:

.. code-block:: bash

    git clone https://github.com/yourusername/simple_mcp_client.git
    cd simple_mcp_client
    pip install -e ".[dev]"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 