# Composer Kit MCP Server

A Model Context Protocol (MCP) server for Composer Kit UI components. This server provides comprehensive access to Composer Kit components, examples, and documentation, enabling LLMs to help developers build beautiful Celo dApps with ease.

## What is Composer Kit?

Composer Kit (@composer-kit/ui) is a ready-to-use React component library designed specifically for building web3 applications on the Celo blockchain. It provides a comprehensive set of modular, accessible, and customizable UI components that make it easy to integrate wallet connections, token balances, payments, NFT interactions, and more into your dApp.

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd composer-kit-mcp
```

2. Install dependencies:

```bash
pip install -e .
```

3. Set up environment variables (optional):

```bash
export GITHUB_TOKEN="your_github_token"  # For higher rate limits
```

## Usage

### Running the Server

```bash
# Run the MCP server
python -m composer_kit_mcp.server

# Or use the CLI entry point
composer-kit-mcp
```

### Available Tools

#### Component Discovery

1. **list_components**
   - List all available Composer Kit components
   - No parameters required
   - Returns: Array of component names and descriptions

#### Component Code Access

2. **get_component**

   - Get the source code for a specific component
   - Parameters: `component_name` (string)
   - Returns: Component source code with imports and exports

3. **get_component_example**
   - Get example usage code for a component
   - Parameters: `component_name` (string), `example_type` (optional)
   - Returns: Example code showing how to use the component

#### Documentation and Setup

4. **get_installation_guide**

   - Get installation instructions for Composer Kit
   - Parameters: `package_manager` (optional: npm, yarn, pnpm, bun)
   - Returns: Step-by-step installation guide

5. **get_component_props**

   - Get component props and API documentation
   - Parameters: `component_name` (string)
   - Returns: Component props, types, and usage information

6. **search_components**
   - Search for components by functionality or name
   - Parameters: `query` (string)
   - Returns: Matching components with descriptions

## Available Components

Composer Kit provides the following component categories:

### Core Components

- **Address**: Display Ethereum addresses with formatting options
- **Balance**: Show token balances with proper formatting
- **Identity**: Display user identity information

### Wallet Integration

- **Wallet**: Wallet connection and management
- **Connect**: Wallet connection button with avatar and name display

### Payment & Transactions

- **Payment**: Payment processing with dialog and error handling
- **Transaction**: Blockchain transaction management with status tracking
- **Swap**: Token swapping interface with toggle and selection

### Token Management

- **TokenSelect**: Token selection dropdown with search functionality

### NFT Components

- **NFTCard**: Display NFT information and metadata
- **NFTMint**: NFT minting interface

## Architecture

The server is built with a modular architecture:

```
src/composer_kit_mcp/
├── components/         # Component data access and management
│   ├── models.py      # Component data models
│   ├── service.py     # Component service (GitHub API integration)
│   └── cache.py       # Caching for performance
├── examples/          # Example code management
│   ├── models.py      # Example data models
│   └── service.py     # Example service
├── docs/              # Documentation access
│   ├── models.py      # Documentation models
│   └── service.py     # Documentation service
├── server.py          # Main MCP server
└── utils.py           # Utility functions
```

## Key Features

### Component Support

- **Complete Library**: Access to all Composer Kit components
- **Source Code**: Get actual component implementation
- **Props Documentation**: Detailed component API information
- **Type Definitions**: TypeScript type information

### Example Integration

- **Real Examples**: Access to actual examples from the docs
- **Multiple Patterns**: Different usage patterns for each component
- **Best Practices**: Examples following Composer Kit conventions
- **Copy-Paste Ready**: Examples ready for immediate use

### Documentation Access

- **Installation Guides**: Step-by-step setup instructions
- **Component Docs**: Comprehensive component documentation
- **API Reference**: Complete props and methods documentation
- **Usage Patterns**: Common usage patterns and best practices

### Performance Optimization

- **Intelligent Caching**: Cache component data and examples
- **Rate Limiting**: Respect GitHub API rate limits
- **Efficient Fetching**: Minimize API calls with smart caching
- **Error Handling**: Graceful degradation for network issues

## Error Handling

The server includes comprehensive error handling:

- Input validation for all parameters
- Network error handling with retries
- GitHub API rate limit handling
- Graceful degradation for missing components
- Detailed error messages for debugging

## Caching

Performance optimization through caching:

- Component source code caching
- Example code caching
- Documentation caching
- GitHub API response caching with appropriate TTLs

## Security Considerations

- Read-only operations by default
- No sensitive data handling
- Input validation and sanitization
- Rate limiting for external API calls
- Optional GitHub token for higher rate limits

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

### Type Checking

```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Projects

- [Composer Kit](https://github.com/celo-org/composer-kit) - The UI library this MCP server provides access to
- [Celo MCP](https://github.com/viral-sangani/celo-mcp) - MCP server for Celo blockchain interactions
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification

## Support

For issues and questions:

- Open an issue on GitHub
- Check the Composer Kit documentation
- Join the Celo developer community
