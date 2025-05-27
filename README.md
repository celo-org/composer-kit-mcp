# Composer Kit MCP Server

A Model Context Protocol (MCP) server for accessing Composer Kit UI components documentation, examples, and usage information. This server provides comprehensive access to the Composer Kit React component library designed for building web3 applications on the Celo blockchain.

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

## Usage

### Running the Server

```bash
# Run the MCP server
python -m composer_kit_mcp.server

# Or use the CLI entry point
composer-kit-mcp
```

### Available Tools

#### Component Information

1. **list_components**

   - List all available Composer Kit components with their descriptions and categories
   - No parameters required

2. **get_component**

   - Get detailed information about a specific component, including source code, props, and usage information
   - Parameters: `component_name` (e.g., 'button', 'wallet', 'payment', 'swap')

3. **get_component_example**

   - Get example usage code for a specific component with real-world examples
   - Parameters: `component_name`, `example_type` (optional: 'basic', 'advanced', 'with-props')

4. **search_components**

   - Search for components by name, description, or functionality
   - Parameters: `query` (e.g., 'wallet', 'payment', 'token', 'nft')

5. **get_component_props**
   - Get detailed prop information for a specific component, including types, descriptions, and requirements
   - Parameters: `component_name`

#### Installation and Setup

6. **get_installation_guide**

   - Get installation instructions for Composer Kit, including setup steps and configuration
   - Parameters: `package_manager` (optional: 'npm', 'yarn', 'pnpm', 'bun')

7. **get_components_by_category**
   - Get all components in a specific category
   - Parameters: `category` (e.g., 'Core Components', 'Wallet Integration', 'Payment & Transactions')

## Available Components

### Core Components

- **Address**: Display Ethereum addresses with truncation and copy functionality
- **Balance**: Display and manage token balances with precision control
- **Identity**: Display user information with address, name, balance, and social links

### Wallet Integration

- **Wallet**: Wallet connection and user information display
- **Connect**: Wallet connection button with callback support

### Payment & Transactions

- **Payment**: Send payments with built-in dialog and error handling
- **Transaction**: Facilitate blockchain transactions with status tracking
- **Swap**: Token exchange interface with swappable token selection

### Token Management

- **TokenSelect**: Search and select tokens from a list with filtering

### NFT Components

- **NFT**: Display NFT details and provide minting interface
- **NFTCard**: Card layout for NFT display
- **NFTImage**: NFT image display component
- **NFTMeta**: NFT metadata display
- **NFTMint**: NFT minting interface

## Key Features

### Component Documentation

- **Complete API Reference**: Detailed prop information for all components
- **Usage Examples**: Real-world code examples for each component
- **Installation Guides**: Step-by-step setup instructions
- **Category Organization**: Components organized by functionality

### Search and Discovery

- **Semantic Search**: Find components by functionality or use case
- **Category Filtering**: Browse components by category
- **Prop Documentation**: Detailed type information and requirements

### Code Examples

- **Basic Usage**: Simple implementation examples
- **Advanced Patterns**: Complex usage scenarios
- **Best Practices**: Recommended implementation patterns

## Architecture

The server provides access to hardcoded Composer Kit component data:

```
src/composer_kit_mcp/
├── components/         # Component data and models
│   ├── data.py        # Hardcoded component information
│   └── models.py      # Pydantic models for components
├── server.py          # Main MCP server
└── __init__.py        # Package initialization
```

## Component Categories

### Core Components

Essential UI components for basic functionality

### Wallet Integration

Components for wallet connection and user management

### Payment & Transactions

Components for handling payments and blockchain transactions

### Token Management

Components for token selection and management

### NFT Components

Components for NFT display and interaction

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

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:

- GitHub Issues: [composer-kit-mcp/issues](https://github.com/viral-sangani/composer-kit-mcp/issues)
- Documentation: [Composer Kit Docs](https://github.com/celo-org/composer-kit)
