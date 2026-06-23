import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

TARGET_URL = "https://reanime.to"


def format_expiry(expires):
    if not expires or expires <= 0:
        return "Session Cookie"

    return datetime.fromtimestamp(expires).strftime("%Y-%m-%d %H:%M:%S")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            slow_mo=100,
        )

        context = await browser.new_context()

        page = await context.new_page()

        print("=" * 70)
        print(f"Opening {TARGET_URL}")
        print("=" * 70)

        await page.goto(TARGET_URL)

        cookies = await context.cookies()

        print(f"\nFound {len(cookies)} cookies.\n")

        for cookie in cookies:
            print("=" * 70)
            print(f"Name      : {cookie['name']}")
            print(f"Value     : {cookie['value']}")
            print(f"Domain    : {cookie['domain']}")
            print(f"Path      : {cookie['path']}")
            print(f"Expires   : {format_expiry(cookie['expires'])}")
            print(f"Secure    : {cookie['secure']}")
            print(f"HttpOnly  : {cookie['httpOnly']}")
            print(f"SameSite  : {cookie['sameSite']}")

        cf = [
            c
            for c in cookies
            if c["name"].startswith("cf_")
            or c["name"].startswith("__cf")
        ]

        print("\n")
        print("=" * 70)
        print("Cloudflare Cookies")
        print("=" * 70)

        if cf:
            for c in cf:
                print(f"Name: {c['name']}")
                print(f"Expires: {format_expiry(c['expires'])}")

                if c["expires"] > 0:
                    remaining = c["expires"] - datetime.now().timestamp()
                    print(f"Remaining: {remaining/60:.1f} minutes")

                print()
        else:
            print("No Cloudflare cookies found.")

        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)

        await context.storage_state(path="storage_state.json")

        cookie_header = "; ".join(
            f"{c['name']}={c['value']}" for c in cookies
        )

        print("\n")
        print("=" * 70)
        print("Cookie Header")
        print("=" * 70)
        print(cookie_header)

        print("\nSaved:")
        print(" - cookies.json")
        print(" - storage_state.json")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())