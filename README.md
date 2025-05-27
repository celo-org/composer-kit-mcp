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

## MCP Client Setup

### Setting up in Cursor

1. **Install the MCP server** (if not already done):

   ```bash
   pip install composer-kit-mcp
   ```

2. **Configure Cursor** by adding the MCP server to your Cursor settings:

   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to "Features" → "Model Context Protocol"
   - Add a new MCP server with the following configuration:

   ```json
   {
     "mcpServers": {
       "composer-kit-mcp": {
         "command": "uvx",
         "args": ["composer-kit-mcp"]
       }
     }
   }
   ```

3. **Restart Cursor** to load the MCP server

4. **Verify the setup** by asking Cursor about Composer Kit components:
   - "What Composer Kit components are available?"
   - "Show me how to use the Wallet component"
   - "Search for payment-related components"

### Setting up in Claude Desktop

1. **Install the MCP server** (if not already done):

   ```bash
   pip install composer-kit-mcp
   ```

2. **Locate your Claude Desktop config file**:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Edit the config file** to add the MCP server:

   ```json
   {
     "mcpServers": {
       "composer-kit-mcp": {
         "command": "uvx",
         "args": ["composer-kit-mcp"]
       }
     }
   }
   ```

   If the file doesn't exist, create it with the above content.

4. **Restart Claude Desktop** to load the MCP server

5. **Verify the setup** by asking Claude about Composer Kit:
   - Look for the 🔌 icon in the chat interface indicating MCP tools are available
   - Ask: "What Composer Kit components can you help me with?"
   - Try: "Show me examples of using the Payment component"

### Alternative Installation Methods

#### Using pipx (Recommended for isolation)

```bash
# Install pipx if you haven't already
pip install pipx

# Install composer-kit-mcp in an isolated environment
pipx install composer-kit-mcp

# The command will be available globally
composer-kit-mcp
```

#### Using virtual environment

```bash
# Create a virtual environment
python -m venv composer-kit-mcp-env
source composer-kit-mcp-env/bin/activate  # On Windows: composer-kit-mcp-env\Scripts\activate

# Install the package
pip install composer-kit-mcp

# Use the full path in your MCP config
# e.g., /path/to/composer-kit-mcp-env/bin/composer-kit-mcp
```

### Troubleshooting

#### Common Issues

1. **Command not found**: Make sure the package is installed and the command is in your PATH

   ```bash
   which composer-kit-mcp  # Should show the path to the command
   ```

2. **Permission errors**: Try installing with `--user` flag or use pipx

   ```bash
   pip install --user composer-kit-mcp
   ```

3. **MCP server not connecting**: Check that the command path in your config is correct

   ```bash
   composer-kit-mcp  # Should start the server (will wait for input)
   ```

4. **Python version issues**: Ensure you're using Python 3.11 or higher
   ```bash
   python --version  # Should be 3.11+
   ```

#### Debugging

To test if the MCP server is working correctly:

```bash
# Test the server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | composer-kit-mcp
```

This should return a JSON response with the available tools.

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
