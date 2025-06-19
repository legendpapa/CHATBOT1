import asyncio
import speedtest
from pyrogram import filters, Client
from pyrogram.types import Message

# Speedtest result template
server_result_template = (
    "✯ Speedtest Results ✯\n\n"
    "Client:\n"
    "» ISP: {isp}\n"
    "» Country: {country}\n\n"
    "Server:\n"
    "» Name: {server_name}\n"
    "» Country: {server_country}, {server_cc}\n"
    "» Sponsor: {sponsor}\n"
    "» Latency: {latency} ms\n"
    "» Ping: {ping} ms"
)

# Function to run Speedtest
def run_speedtest():
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    results = test.results.dict()
    try:
        results["share"] = test.results.share()  # Attempt to get a share link
    except Exception:
        results["share"] = None  # Fallback if share fails
    return results

# Command to handle speedtest
@Client.on_message(filters.command(["speedtest", "spt"], prefixes=["/"]))
async def speedtest_function(client, message: Message):
    m = await message.reply_text("Running speed test...")
    try:
        # Run speedtest in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_speedtest)

        # Prepare output
        output = server_result_template.format(
            isp=result["client"]["isp"],
            country=result["client"]["country"],
            server_name=result["server"]["name"],
            server_country=result["server"]["country"],
            server_cc=result["server"]["cc"],
            sponsor=result["server"]["sponsor"],
            latency=result["server"]["latency"],
            ping=result["ping"],
        )

        # Send results with optional image
        if result["share"]:
            await message.reply_photo(photo=result["share"], caption=output)
        else:
            await message.reply_text(output)

        await m.delete()
    except Exception as e:
        # Handle errors gracefully
        await m.edit_text(f"An error occurred: {e}")