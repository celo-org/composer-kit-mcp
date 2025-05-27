#!/usr/bin/env python3
"""Test script to verify we can fetch specific example files."""

import asyncio
from src.composer_kit_mcp.components import ComponentService


async def test_fetch():
    service = ComponentService()

    # Test fetching the address basic example
    content = await service._get_raw_file_content(
        "apps/docs/examples/address/basic.tsx"
    )
    if content:
        print("✅ Successfully fetched address/basic.tsx")
        print(f"Content length: {len(content)} characters")
        print("First few lines:")
        for line in content.split("\n")[:5]:
            print(f"  {line}")
    else:
        print("❌ Failed to fetch address/basic.tsx")

    # Test fetching the nft mint example
    nft_content = await service._get_raw_file_content("apps/docs/examples/nft/mint.tsx")
    if nft_content:
        print("\n✅ Successfully fetched nft/mint.tsx")
        print(f"Content length: {len(nft_content)} characters")
        print("First few lines:")
        for line in nft_content.split("\n")[:5]:
            print(f"  {line}")
    else:
        print("\n❌ Failed to fetch nft/mint.tsx")

    # Test fetching transaction basic example
    tx_content = await service._get_raw_file_content(
        "apps/docs/examples/transaction/basic.tsx"
    )
    if tx_content:
        print("\n✅ Successfully fetched transaction/basic.tsx")
        print(f"Content length: {len(tx_content)} characters")
    else:
        print("\n❌ Failed to fetch transaction/basic.tsx")


if __name__ == "__main__":
    asyncio.run(test_fetch())
