import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from rich.console import Console
from shipsight.config import ShipSightConfig

console = Console()

class CaptureEngine:
    def __init__(self, config: ShipSightConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)

    async def capture_screenshots(self, base_url: str):
        routes = self.config.capture.routes
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Set high device_scale_factor for "Retina" quality (perfect for LinkedIn/README)
            context = await browser.new_context(
                viewport=self.config.capture.viewport,
                device_scale_factor=2 
            )
            page = await context.new_page()

            for route in routes:
                url = f"{base_url.rstrip('/')}/{route.lstrip('/')}"
                console.print(f"[yellow]Capturing high-res screenshot: {url}[/yellow]")
                try:
                    await page.goto(url, wait_until="load", timeout=60000)
                    
                    # 1. Auto-scroll to trigger lazy loading / animations
                    await self._auto_scroll(page)
                    
                    # 2. Final wait for stability
                    await asyncio.sleep(2)
                    
                    filename = route.replace("/", "_").strip("_") or "index"
                    filepath = self.output_dir / "screenshots" / f"{filename}.png"
                    await page.screenshot(path=str(filepath), full_page=True)
                    console.print(f"[green]Saved 2x-res screenshot to {filepath}[/green]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Capture issues for {url}: {e}[/yellow]")
                    try:
                        filename = route.replace("/", "_").strip("_") or "index"
                        filepath = self.output_dir / "screenshots" / f"{filename}_partial.png"
                        await page.screenshot(path=str(filepath), full_page=True)
                    except:
                        pass

            await browser.close()

    async def _auto_scroll(self, page):
        """Scroll to the bottom of the page to trigger lazy loading."""
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 100;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)

    async def record_walkthrough(self, base_url: str, duration: int = 5):
        """Simple GIF/Walkthrough placeholder (sequence of screenshots for now)."""
        # In a real production tool, we'd use a screen recorder or sequence preservation
        console.print("[yellow]Recording walkthrough (GIF)...[/yellow]")
        # TODO: Implement GIF recording using ffmpeg or similar
        pass
