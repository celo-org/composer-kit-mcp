"""Hardcoded Composer Kit component data."""

from .models import Component, ComponentExample, ComponentProp, InstallationGuide

# Installation guides for different package managers
INSTALLATION_GUIDES = {
    "npm": InstallationGuide(
        package_manager="npm",
        install_command="npm install @composer-kit/ui",
        setup_code="""import { ComposerKitProvider } from "@composer-kit/ui";

function App() {
  return <ComposerKitProvider>{/* Your app content */}</ComposerKitProvider>;
}""",
        additional_steps=[
            "Configure the ComposerKitProvider in your app",
            "Import components as needed from their specific paths",
        ],
    ),
    "yarn": InstallationGuide(
        package_manager="yarn",
        install_command="yarn add @composer-kit/ui",
        setup_code="""import { ComposerKitProvider } from "@composer-kit/ui";

function App() {
  return <ComposerKitProvider>{/* Your app content */}</ComposerKitProvider>;
}""",
        additional_steps=[
            "Configure the ComposerKitProvider in your app",
            "Import components as needed from their specific paths",
        ],
    ),
    "pnpm": InstallationGuide(
        package_manager="pnpm",
        install_command="pnpm add @composer-kit/ui",
        setup_code="""import { ComposerKitProvider } from "@composer-kit/ui";

function App() {
  return <ComposerKitProvider>{/* Your app content */}</ComposerKitProvider>;
}""",
        additional_steps=[
            "Configure the ComposerKitProvider in your app",
            "Import components as needed from their specific paths",
        ],
    ),
    "bun": InstallationGuide(
        package_manager="bun",
        install_command="bun add @composer-kit/ui",
        setup_code="""import { ComposerKitProvider } from "@composer-kit/ui";

function App() {
  return <ComposerKitProvider>{/* Your app content */}</ComposerKitProvider>;
}""",
        additional_steps=[
            "Configure the ComposerKitProvider in your app",
            "Import components as needed from their specific paths",
        ],
    ),
}

# Component data
COMPONENTS = [
    Component(
        name="Address",
        category="Core Components",
        description="Display an Ethereum address with truncation and copy functionality",
        detailed_description="The Address component is used to display an Ethereum address. It can be used to display an address in a readable format or to copy the address to the clipboard.",
        import_path="@composer-kit/ui/address",
        props=[
            ComponentProp(
                name="address",
                type="string",
                description="The actual address to display. This is a required prop.",
                required=True,
            ),
            ComponentProp(
                name="isTruncated",
                type="boolean",
                description="Determines if the address should be truncated for display. Truncation typically hides the middle part of long addresses.",
                default="false",
            ),
            ComponentProp(
                name="className",
                type="string",
                description="A custom CSS class to apply styles to the component.",
            ),
            ComponentProp(
                name="copyOnClick",
                type="boolean",
                description="If true, the address will be copied to the clipboard when clicked.",
                default="false",
            ),
            ComponentProp(
                name="onCopyComplete",
                type="(message: string) => void",
                description="A callback that is triggered after the address is copied. It receives an address in case of success else 'Failed to copy address' that can be used for feedback or notifications.",
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Address Display",
                description="Basic usage of the Address component with copy functionality",
                code="""import { Address } from "@composer-kit/ui/address";
import { useState } from "react";

export const Basic = () => {
  const [isCopied, setIsCopied] = useState(false);
  return (
    <div>
      <Address
        address="0x208B03553D46A8A16ed53e8632743249dd2E79c3"
        className="bg-white dark:bg-black p-2 rounded-md font-semibold"
        onCopyComplete={() => {
          setIsCopied(true);
          setTimeout(() => {
            setIsCopied(false);
          }, 1000);
        }}
      />
      {isCopied && (
        <p className="mt-2 text-white dark:text-black bg-black dark:bg-white p-1 font-medium text-sm text-center w-[4rem] rounded-md">
          Copied
        </p>
      )}
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="Balance",
        category="Core Components",
        description="Display and manage token balances with precision control",
        detailed_description="The Balance component is designed to display and manage token balances seamlessly.",
        import_path="@composer-kit/ui/balance",
        subcomponents=["BalanceInput", "BalanceOptions", "BalanceText"],
        props=[
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The content to be rendered inside the Balance component.",
                required=True,
            ),
            ComponentProp(
                name="precision",
                type="number",
                description="The number of decimal places to display in the balance.",
                default="18",
            ),
            ComponentProp(
                name="tokens",
                type="Token[]",
                description="An array of Token objects to display as selectable options.",
                required=True,
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Balance Display",
                description="Basic usage of the Balance component with input and options",
                code="""import {
  BalanceInput,
  BalanceOptions,
  BalanceText,
  Balance,
} from "@composer-kit/ui/balance";
import { swapableTokens } from "../../utils/constants";

export const BalanceBasic = () => {
  return (
    <div className="flex items-center justify-center">
      <div className="w-96 p-4 bg-white dark:bg-black rounded-lg shadow-lg">
        <Balance>
          <div className="flex flex-col gap-4">
            <BalanceOptions tokens={swapableTokens} />
            <BalanceInput />
          </div>
          <div className="mt-4">
            <BalanceText />
          </div>
        </Balance>
      </div>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="Identity",
        category="Core Components",
        description="Display user information with address, name, balance, and social links",
        detailed_description="The Identity component displays user information such as address, name, balance, and social links in a visually appealing way.",
        import_path="@composer-kit/ui/identity",
        subcomponents=["Avatar", "Name", "Social"],
        props=[
            ComponentProp(
                name="address",
                type="Address",
                description="The address of the identity.",
                required=True,
            ),
            ComponentProp(
                name="token",
                type='"CELO" | "cUSD" | "USDT"',
                description="The type of token associated with the identity.",
            ),
            ComponentProp(
                name="isTruncated",
                type="boolean",
                description="Whether the name should be truncated.",
            ),
            ComponentProp(
                name="precision",
                type="number",
                description="The precision for displaying the balance.",
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Identity Display",
                description="Basic usage of the Identity component with avatar, name, balance, and social link",
                code="""import {
  Avatar,
  Balance,
  Identity,
  Name,
  Social,
} from "@composer-kit/ui/identity";

export const IdentityBasic = () => {
  return (
    <div className="flex items-center justify-center">
      <div className="w-auto p-6 bg-white dark:bg-black rounded-lg shadow-lg min-w-[200px]">
        <Identity
          address="0xE1061b397cC3C381E95a411967e3F053A7c50E70"
          className="flex gap-4 items-center"
          token="cUSD"
        >
          <Avatar />
          <div className="flex flex-col">
            <Name />
            <Balance />
          </div>
          <Social tag="twitter" />
        </Identity>
      </div>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="NFT",
        category="NFT Components",
        description="Display NFT details and provide minting interface",
        detailed_description="The NFTCard and NFTMint components are designed to display NFT details and provide a minting interface for NFTs.",
        import_path="@composer-kit/ui/nft",
        subcomponents=["NFTCard", "NFTImage", "NFTMeta", "NFTTokenId", "NFTMint"],
        props=[
            ComponentProp(
                name="tokenId",
                type="bigint",
                description="The token ID of the NFT.",
                required=True,
            ),
            ComponentProp(
                name="contractAddress",
                type="string",
                description="The contract address of the NFT.",
                required=True,
            ),
            ComponentProp(
                name="className",
                type="string",
                description="Custom CSS class for styling the NFT card or subcomponents.",
            ),
            ComponentProp(
                name="style",
                type="React.CSSProperties",
                description="Inline styles for custom styling.",
            ),
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="Additional elements inside the card.",
            ),
        ],
        examples=[
            ComponentExample(
                title="NFT Preview",
                description="Display NFT information with image, metadata, and token ID",
                code="""import {
  NFT,
  NFTCard,
  NFTImage,
  NFTMeta,
  NFTTokenId,
} from "@composer-kit/ui/nft";

export const NftPreview = () => {
  return (
    <div className="flex items-center justify-center">
      <NFT
        contractAddress="0xd447209176470be0db276549c7143265a559Fb6b"
        tokenId={BigInt("2334")}
      >
        <NFTCard>
          <NFTMeta />
          <NFTImage />
          <NFTTokenId />
        </NFTCard>
      </NFT>
    </div>
  );
};""",
                example_type="basic",
            ),
            ComponentExample(
                title="NFT Mint",
                description="NFT display with minting functionality",
                code="""import {
  NFT,
  NFTCard,
  NFTImage,
  NFTMeta,
  NFTMint,
  NFTTokenId,
} from "@composer-kit/ui/nft";

export const NftMint = () => {
  return (
    <div className="flex items-center justify-center">
      <NFT
        contractAddress="0xd447209176470be0db276549c7143265a559Fb6b"
        tokenId={BigInt("2334")}
      >
        <NFTCard>
          <NFTMeta />
          <NFTImage />
          <NFTTokenId />
          <NFTMint />
        </NFTCard>
      </NFT>
    </div>
  );
};""",
                example_type="advanced",
            ),
        ],
    ),
    Component(
        name="Payment",
        category="Payment & Transactions",
        description="Send payments with built-in dialog and error handling",
        detailed_description="The Payment component is designed to send payment to a recipient address with built-in dialog and error handling.",
        import_path="@composer-kit/ui/payment",
        subcomponents=["PaymentDialog", "PaymentError"],
        props=[
            ComponentProp(
                name="amount",
                type="string",
                description="The amount to be paid.",
                required=True,
            ),
            ComponentProp(
                name="tokenAddress",
                type="Address",
                description="The address of the token being used for the payment.",
                required=True,
            ),
            ComponentProp(
                name="recipientAddress",
                type="Address",
                description="The address of the recipient receiving the payment.",
                required=True,
            ),
            ComponentProp(
                name="chain",
                type="Chain",
                description="The blockchain chain to use for the payment.",
                required=True,
            ),
            ComponentProp(
                name="onSuccess",
                type="(txHash: string) => void",
                description="Callback function triggered upon successful payment.",
            ),
            ComponentProp(
                name="onError",
                type="(error: Error) => void",
                description="Callback function triggered when an error occurs.",
            ),
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The children nodes to render inside the provider.",
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Payment",
                description="Basic payment component with dialog and error handling",
                code="""import { useState } from "react";
import { Payment, PaymentError, PaymentDialog } from "@composer-kit/ui/payment";
import { celo } from "viem/chains";

export const PaymentBasic = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [txHash, setTxHash] = useState("");

  return (
    <div className="w-full items-center justify-center flex flex-col gap-4">
      <Payment
        amount="0.001"
        //@ts-ignore
        chain={celo}
        onSuccess={(hash) => {
          setTxHash(hash);
          setIsOpen(false);
        }}
        onError={(error) => {
          console.error("Payment error", error);
        }}
        recipientAddress="0x717F8A0b80CbEDe59EcA195F1E3D8E142C84d4d6"
        tokenAddress="0x765de816845861e75a25fca122bb6898b8b1282a"
      >
        <button
          className="bg-black font-medium dark:bg-white text-white dark:text-black px-4 py-2 rounded"
          onClick={() => {
            setIsOpen(!isOpen);
          }}
        >
          Paynow
        </button>
        <PaymentDialog
          onOpenChange={() => {
            setIsOpen(!isOpen);
          }}
          open={isOpen}
        />
        <PaymentError />
      </Payment>
      {txHash && <p>{txHash}</p>}
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="Swap",
        category="Payment & Transactions",
        description="Token exchange interface with swappable token selection",
        detailed_description="The Swap component allows users to exchange tokens seamlessly with a simple interface.",
        import_path="@composer-kit/ui/swap",
        subcomponents=["SwapButton", "SwapHeader", "SwapToggle", "SwapToken"],
        props=[
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The child components of the Swap container.",
                required=True,
            ),
            ComponentProp(
                name="className",
                type="string",
                description="Optional additional class names.",
            ),
            ComponentProp(
                name="swapableTokens",
                type="SwapableTokens[]",
                description="List of tokens available for swapping.",
                required=True,
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Swap",
                description="Basic token swap interface with toggle and swap button",
                code="""import {
  Swap,
  SwapButton,
  SwapHeader,
  SwapToggle,
  SwapToken,
} from "@composer-kit/ui/swap";
import { swapableTokens } from "../../utils/constants";

export const SwapBasic = () => {
  return (
    <div className="flex items-center justify-center">
      <Swap>
        <SwapHeader />
        <SwapToken label="Sell" swapableTokens={swapableTokens} type="from" />
        <SwapToggle />
        <SwapToken label="Buy" swapableTokens={swapableTokens} type="to" />
        <SwapButton onSwap={() => {}} />
      </Swap>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="TokenSelect",
        category="Token Management",
        description="Search and select tokens from a list with filtering",
        detailed_description="The TokenSelect component is designed to search in a list of tokens and select a token.",
        import_path="@composer-kit/ui/token-select",
        subcomponents=[
            "TokenSelectDropdown",
            "TokenSelectGroup",
            "TokenSelectInput",
            "TokenSelectOption",
        ],
        props=[
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The children nodes to render inside the select.",
                required=True,
            ),
            ComponentProp(
                name="defaultToken",
                type="Token",
                description="The default token to be selected.",
            ),
            ComponentProp(
                name="delayMs",
                type="number",
                description="Delay time in milliseconds before updating the select.",
            ),
            ComponentProp(
                name="onChange",
                type="(token: Token) => void",
                description="Callback function that is called when the token is changed.",
            ),
            ComponentProp(
                name="className",
                type="string",
                description="CSS class name for styling the option or dropdown.",
            ),
            ComponentProp(
                name="placeholder",
                type="string",
                description="The placeholder text to show when the dropdown is empty.",
                required=True,
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Token Select",
                description="Token selection with search and filtering",
                code="""import {
  TokenSelect,
  TokenSelectDropdown,
  TokenSelectGroup,
  TokenSelectInput,
  TokenSelectOption,
} from "@composer-kit/ui/token-select";
import { swapableTokens } from "../../utils/constants";

export const TokenSelectBasic = () => {
  return (
    <div className="flex items-center justify-center">
      <TokenSelect delayMs={300}>
        <TokenSelectDropdown placeholder="Search tokens...">
          <TokenSelectInput />
          <TokenSelectGroup heading="Available tokens">
            {swapableTokens.map((token) => (
              <TokenSelectOption key={token.address} token={token} />
            ))}
          </TokenSelectGroup>
        </TokenSelectDropdown>
      </TokenSelect>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="Transaction",
        category="Payment & Transactions",
        description="Facilitate blockchain transactions with status tracking",
        detailed_description="The Transaction component facilitates blockchain transactions with a simple interface, providing built-in status tracking and error handling.",
        import_path="@composer-kit/ui/transaction",
        subcomponents=["TransactionButton", "TransactionStatus"],
        props=[
            ComponentProp(
                name="chainId",
                type="number",
                description="The ID of the blockchain network to use for the transaction.",
                required=True,
            ),
            ComponentProp(
                name="transaction",
                type="TransactionConfig",
                description="Configuration object for the transaction.",
                required=True,
            ),
            ComponentProp(
                name="onSuccess",
                type="(result: any) => void",
                description="Callback function triggered upon successful transaction.",
            ),
            ComponentProp(
                name="onError",
                type="(error: any) => void",
                description="Callback function triggered when an error occurs.",
            ),
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The children nodes to render inside the transaction component.",
                required=True,
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Transaction",
                description="Basic transaction with button and status tracking",
                code="""import {
  Transaction,
  TransactionButton,
  TransactionStatus,
} from "@composer-kit/ui/transaction";

export const TransactionBasic = () => {
  return (
    <div className="w-full items-center justify-center flex flex-col gap-4">
      <Transaction
        chainId={42220}
        onError={(error: any) => {
          console.log("error", error);
        }}
        onSuccess={(result: any) => {
          console.log("result", result);
        }}
        transaction={{
          abi: [
            {
              name: "transfer",
              type: "function",
              stateMutability: "nonpayable",
              inputs: [
                { name: "recipient", type: "address" },
                { name: "amount", type: "uint256" },
              ],
              outputs: [{ name: "", type: "bool" }],
            },
          ],
          address: "0x765de816845861e75a25fca122bb6898b8b1282a",
          args: ["0x717F8A0b80CbEDe59EcA195F1E3D8E142C84d4d6", 1],
          functionName: "transfer",
        }}
      >
        <TransactionButton>Send</TransactionButton>
        <TransactionStatus />
      </Transaction>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
    Component(
        name="Wallet",
        category="Wallet Integration",
        description="Wallet connection and user information display",
        detailed_description="The Wallet component provides functionality for connecting wallets and displaying user information.",
        import_path="@composer-kit/ui/wallet",
        subcomponents=["Avatar", "Connect", "Name"],
        props=[
            ComponentProp(
                name="children",
                type="React.ReactNode",
                description="The content inside the component, typically Avatar and Name.",
                required=True,
            ),
            ComponentProp(
                name="label",
                type="React.ReactNode",
                description="The text or element to display on the connect button.",
                default='"Connect"',
            ),
            ComponentProp(
                name="onConnect",
                type="() => void",
                description="A callback function that is triggered when the connection is successful.",
            ),
            ComponentProp(
                name="isTruncated",
                type="boolean",
                description="Whether the name should be truncated (e.g., for display in small spaces).",
                default="false",
            ),
            ComponentProp(
                name="className",
                type="string",
                description="CSS class name for styling the button, avatar, or name.",
            ),
        ],
        examples=[
            ComponentExample(
                title="Basic Wallet Connection",
                description="Basic wallet connection with avatar and name display",
                code="""import { Avatar, Connect, Name, Wallet } from "@composer-kit/ui/wallet";

export const WalletBasic = () => {
  return (
    <div className="flex items-center justify-center">
      <Wallet>
        <Connect
          label="Connect Now"
          onConnect={() => {
            console.log("Connected");
          }}
        >
          <Avatar />
          <Name />
        </Connect>
      </Wallet>
    </div>
  );
};""",
                example_type="basic",
            )
        ],
    ),
]

# Categories
CATEGORIES = [
    "Core Components",
    "Wallet Integration",
    "Payment & Transactions",
    "Token Management",
    "NFT Components",
]
