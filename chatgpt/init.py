from revChatGPT.V2 import Chatbot
API_KEY="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"
MAIL="leanylff@gmail.com",
SECRET= "Tio-Plato"
async def main():
    chatbot = Chatbot(email=MAIL, password=SECRET)
    async for line in chatbot.ask("Hello"):
        print(line["choices"][0]["text"].replace("<|im_end|>", ""), end="", flush = True)
    print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())