#!/usr/bin/env python3
"""
LLM Endpoint Discovery Script
Uses the prompt_injection_tester framework to discover LLM services on 127.0.0.1
"""

import asyncio
import sys
from pathlib import Path

# Add current directory and parent to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

async def probe_endpoint(url: str) -> dict:
    """
    Probe a specific endpoint using the PIT framework.

    Args:
        url: Full URL to test (e.g., http://127.0.0.1:11434/api/chat)

    Returns:
        dict with 'success', 'url', 'response' keys
    """
    try:
        from prompt_injection_tester.core.tester import InjectionTester
        from prompt_injection_tester.core.models import TargetConfig

        # Create target config
        config = TargetConfig(
            name="Discovery Probe",
            base_url=url,
            api_type="openai",  # Try OpenAI format first
            timeout=5,
            rate_limit=1.0
        )

        # Create tester instance
        tester = InjectionTester(target_config=config)

        try:
            # Initialize client
            await tester._initialize_client()

            # Try a simple test message
            messages = [{
                "role": "user",
                "content": "Hello, respond with 'OK' if you can hear me."
            }]

            # Attempt to get a response using the chat method
            response = await tester.client.chat(messages)

            if response and len(response) > 0:
                return {
                    "success": True,
                    "url": url,
                    "response": response[:200],  # First 200 chars
                    "config": {"api_type": config.api_type}
                }
        finally:
            await tester.close()

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }

    return {"success": False, "url": url, "error": "No response"}


async def discover_llm():
    """
    Discover LLM endpoint on 127.0.0.1 using PIT framework.
    """
    print("=" * 70)
    print("LLM Endpoint Discovery - Using PIT Framework")
    print("=" * 70)
    print()

    # Common ports for LLM services
    ports = [1234, 11434, 8000, 8080, 5000, 8888]

    # Common API paths
    paths = [
        "/api/chat",
        "/api/generate",
        "/v1/chat/completions",
        "/chat/completions",
        "/api/v1/chat",
    ]

    # Build list of URLs to test
    urls_to_test = []
    for port in ports:
        for path in paths:
            urls_to_test.append(f"http://127.0.0.1:{port}{path}")

    print(f"Testing {len(urls_to_test)} endpoint combinations...")
    print()

    # Test each endpoint
    successful_endpoints = []

    for i, url in enumerate(urls_to_test, 1):
        print(f"[{i}/{len(urls_to_test)}] Testing: {url}")

        result = await probe_endpoint(url)

        if result["success"]:
            print(f"  ✓ SUCCESS! Endpoint responds")
            print(f"    Response preview: {result['response'][:100]}...")
            successful_endpoints.append(result)
        else:
            print(f"  ✗ Failed: {result.get('error', 'No response')[:50]}")

        # Small delay between probes
        await asyncio.sleep(0.2)

    # Summary
    print()
    print("=" * 70)
    print("Discovery Summary")
    print("=" * 70)
    print()

    if successful_endpoints:
        print(f"✓ Found {len(successful_endpoints)} working endpoint(s):")
        print()
        for endpoint in successful_endpoints:
            print(f"  • URL: {endpoint['url']}")
            print(f"    API Type: {endpoint['config']['api_type']}")
            print(f"    Response: {endpoint['response'][:100]}...")
            print()

        # Return the first working endpoint
        target_url = successful_endpoints[0]['url']
        print("=" * 70)
        print(f"🎯 Target URL for Testing: {target_url}")
        print("=" * 70)
        print()
        print("Next steps:")
        print(f"  python -m prompt_injection_tester \\")
        print(f"    --target {target_url} \\")
        print(f"    --authorize \\")
        print(f"    --output report.html \\")
        print(f"    --format html \\")
        print(f"    --verbose")
        print()

        return target_url
    else:
        print("✗ No working LLM endpoints found on 127.0.0.1")
        print()
        print("Possible reasons:")
        print("  1. No LLM service is running")
        print("  2. LLM is on a different port")
        print("  3. LLM requires authentication")
        print("  4. Firewall is blocking connections")
        print()
        return None


def main():
    """Main entry point."""
    try:
        target_url = asyncio.run(discover_llm())

        if target_url:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠ Discovery interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
