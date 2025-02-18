import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import ollama  # Make sure to import ollama if it's used

async def crawl_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Change to False for headful mode
        page = await browser.new_page()
        try:
            print(f"Crawling URL: {url}")
            await page.goto(url, wait_until='load', timeout=60000)  # Increased timeout to 60 seconds
            content = await page.content()
            return content
        except Exception as e:
            print(f"Error during crawling: {e}")
            return None
        finally:
            await browser.close()

async def extract_meta_descriptions(content):
    soup = BeautifulSoup(content, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_descriptions = []
    for tag in meta_tags:
        if 'name' in tag.attrs and tag.attrs['name'] == 'description':
            meta_descriptions.append(tag.attrs.get('content', ''))
    return meta_descriptions

def generate_prompt(query, stored_content):
    """Generates a structured prompt for SEO insights."""
    return f"""
Analyze the following website content and answer the user's SEO question:

Website Content:
{stored_content}

User Query:
{query}

Strictly format the output as follows:
● User: "{query}"
● AI: "<SEO Insight>"
"""

async def seo_chatbot(url, query):
    content = await crawl_page(url)
    if content:
        meta_descriptions = await extract_meta_descriptions(content)
        if not meta_descriptions:
            print("Crawled pages with missing meta descriptions: No meta descriptions found.")
        else:
            print(f"Crawled pages with missing meta descriptions: {meta_descriptions}")

        # Prepare to generate insights
        stored_content = content  # You can store the relevant content for the prompt
        prompt = generate_prompt(query, stored_content)

        try:
            # Using loop.run_in_executor instead of asyncio.to_thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": prompt}])
            )

            seo_insight = response.get("message", {}).get("content", "").strip()

            if seo_insight:
                return {
                    "user": query,
                    "ai": seo_insight
                }
            else:
                return {"error": "Failed to generate SEO insights."}
        except Exception as e:
            return {"error": f"Error generating SEO insights: {e}"}
    else:
        return {"error": "Failed to retrieve content."}

if __name__ == "__main__":
    url = input("Enter the website URL: ")
    question = input("Enter your SEO question: ")
    result = asyncio.run(seo_chatbot(url, question))
    print(result)
