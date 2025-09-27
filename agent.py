import asyncio
from langchain_community.agent_toolkits import PlaywrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_playwright_agent

async def main():
    # 1. Setup the browser and the tools
    print("🚀 Initializing browser and tools...")
    browser = await create_async_playwright_browser()
    # This toolkit correctly wraps the browser and provides the tools
    toolkit = PlaywrightBrowserToolkit.from_browser(async_browser=browser)
    tools = toolkit.get_tools()

    # 2. Initialize the Gemini LLM with the API key directly in the code
    print("🧠 Initializing Google Gemini model...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        temperature=0,
        google_api_key="AIzaSyCFD8gx0Ie96MvIMC1ZQcC-7ApK4JollEc"
    )

    # 3. Create the agent executor
    agent_executor = create_playwright_agent(
        llm=llm,
        tools=tools,
        verbose=True
    )

    # 4. Define the task for the agent to perform
    task = "Navigate to the Google Store, find the price of the latest Pixel phone, and state what colors it is available in."
    print(f"▶️  Running agent with task: {task}")

    # 5. Invoke the agent
    response = await agent_executor.ainvoke({"input": task})

    # 6. Print the final answer
    print("\n✅ Agent finished. Final Answer:")
    print(response['output'])

    # 7. Clean up
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())