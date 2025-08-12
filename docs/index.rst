.. MCP GitLab documentation master file

MCP GitLab Server Documentation
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   configuration
   usage
   api_reference
   contributing
   changelog

Introduction
------------

MCP GitLab is a Model Context Protocol (MCP) server that provides comprehensive GitLab API integration. 
This server enables LLMs to interact with GitLab repositories, manage merge requests, issues, and perform various Git operations.

Features
--------

* 🔐 **Authentication & Users** - Get current user info and lookup user profiles
* 🔍 **Project Management** - List, search, and get details about GitLab projects  
* 📝 **Issues** - List, read, search, and comment on issues
* 🔀 **Merge Requests** - List, read, update, approve, and merge MRs
* 📁 **Repository Files** - Browse, read, and commit changes to files
* 🌳 **Branches & Tags** - List and manage branches and tags
* 🔧 **CI/CD Pipelines** - View pipeline status, jobs, and artifacts
* 💬 **Discussions** - Read and resolve merge request discussions
* 🎯 **Smart Operations** - Batch operations, AI summaries, and smart diffs

Quick Start
-----------

.. code-block:: bash

   # Install with pip
   pip install mcp-gitlab

   # Or run with uvx (no installation needed)
   uvx mcp-gitlab

   # Configure environment
   export GITLAB_PRIVATE_TOKEN="your-token-here"
   export GITLAB_URL="https://gitlab.com"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`