#!/bin/bash
# Test runner script for mcp-gitlab

echo "Running MCP GitLab Tests..."
echo "=========================="

# Install test dependencies if needed
echo "Installing test dependencies..."
pip install -e ".[test]" --quiet

# Run tests with coverage
echo -e "\nRunning unit tests..."
python -m pytest tests/ -v --tb=short --cov=mcp_gitlab --cov-report=term-missing --cov-report=html

# Run specific test categories
echo -e "\nTest Summary:"
echo "-------------"
python -m pytest tests/ --tb=no -q --co -m unit | grep -c "test_" | xargs echo "Unit tests:"
python -m pytest tests/ --tb=no -q --co -m integration 2>/dev/null | grep -c "test_" | xargs echo "Integration tests:"

echo -e "\nCoverage report generated in htmlcov/"
echo "Run 'open htmlcov/index.html' to view detailed coverage"