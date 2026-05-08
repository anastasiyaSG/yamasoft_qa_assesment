async def safe_click(page, locator, retries = 3):
    try: 
        await wait_for_toasts_to_disapper(page)
    except:
        pass
    for attempt in range(retries):
        try:
            await locator.click()
            return
        except Exception as e:
            if attempt < retries - 1:
                print(f"Click failed on attempt {attempt + 1}. Retrying...")
                await page.wait_for_timeout(1000)  # Wait for 1 second before retrying
            else:
                print(f"Click failed after {retries} attempts.")
                raise e
            
async def wait_for_toasts_to_disapper(page):  
    try:
        await page.wait_for_selector('.jq-toast-single', state='detached', timeout=5000)
    except:
        pass