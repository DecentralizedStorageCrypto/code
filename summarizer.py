import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config

model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')

text = """There are a lot of changes in the crypto market these days, and they will indeed affect the new coins and currencies. Investors are not oriented to the classic crypto as coins but more to the uncommon investing models. One of those significant high interest and gains was Dash 2 Trade, the new rising star on the crypto sky.

Buyers have also shown increased interest in investing in Arweave, Filecoin, and others. If you are interested in safe and sustainable investment, you should consider Calvaria, IMPT, and Tamadoge for your next buy. Those three have shown high potential to double your investment quickly. Along with that, you will invest in intelligent and eco-friendly options, too.

Why is everyone buying Filecoin and Arweave these days?

Filecoin and its native token, FIL, is a decentralized storage network that gained 15% over 24 hours. This token currently trades at $5.96, up by 13.6% over the past day. Also, FIL's highest gain was 19.7% within seven days and 2.0% through one month. This currency's highest gain was when Meta shared the plans to use a decentralized data storage solution to archive its creators' digital collectibles.

Arweave is also a data storage solution, and its native token, AR, is also gaining after Meta announced that they would use Arweave to store the digital collectibles owned by users of the social media platforms. Since Meta is a parent company of Facebook and Instagram, you know how many users, and potential the currency has. The market cap is above $1 trillion, and trading volume increased to $450 million in one day.

Experienced investors are turned to more safe and payable options these days, though. There is a third, much safer, and potentially opportunity, Dash 2 Trade, a new double-money star on the crypto market. After the first weeks of the presale, it has shown a fantastic potential to grow steadily, attracting many investors. Along with that, you should consider three more coins to invest. The battle card game with an impressively high number of players after the first days of presale and an eco-friendly token that saves the planet IMPT.

Why consider Dash 2 Trade?

Dash 2 Trade has made an impressive change in the crypto market in only a few weeks of the presale. It has become a new, potentially growing crypto and the most exciting movement on the internet. As a specialized and informed trading analytics platform, Dash 2 Trade and its native token (D2T) has changed how we view cryptocurrency. The platform provides in-depth market insights and helps create market-beating strategies, allowing access to signals, metrics, and social trading tools. Traders can get support and a place to invest, no matter how skilled or experienced.

The platform will offer three versions, or tiers, for each type of investor and trader. If you are a beginner, you should have entry to the basic level, which will not require holding D2T tokens. The player can learn about the venue and crypto investing on this platform. Once you become skilled and have more experience, you can enter the second tier and access on-chain data and fundamental insights into notable presale launches. This platform allows you to move up to the third tier, premium, as intimate access to all Dash 2 Trade features.

>> Buy Dash 2 Trade Now <<

What is Calvaria (RIA)?

If you are more interested in investing in the P2E battle card game, Calvaria is the best option for you. The platform's primary goal is not a crypto investment but speeding up the mass adoption of crypto through the platform and creating the first effective match between crypto and the real world. The platform has two models, the basic or primary and the premium model. The direct option is a free-to-play model for beginners and those that want to try this game before investing. T

After you learn more about the game, you can access the higher model, the play-to-earn one, which is held on blockchain function and allows the creator to make the game accessible without constraining barriers. They will also be convinced that their decision is made without being told to, leading to better responses. With this full access, gamers will get all earnings in the game, like tokens, NFTs, skins, potions, etc. The competition attracts a wide range of players and traders, making the game more potential for investments.

>> Buy Calvaria Now <<

Is investing in IMPT eco-friendly?

More and more new investors are interested in investing in eco-friendly and green currency models. IMPT is one of the potentially greenest projects in the crypto world that will change how we view crypto. Since it supports more than 10,000 projects, each investment promotes environmental protection. Eco-friendly crypto is a possible model for investing. The first weeks of presale have attracted an impressive number of investors, and the first $220k tokens have been sold during the first 24 hours. The first week has raised almost $3 million in tokens, nearly a third of the total $10.8 million. The price rises as the number of sold tokens rise, so hurry up to join the real battle for the planet.

>> Buy IMPT Now <<

Consider Tamadoge as a great model for investing

Tamadoge is now a well-known P2E model that has attracted many investors. The game is based on the pet-nurturing match, where players buy a pet and all additions needed to grow it until adulthood. There will be great additions, like avatars, clothes, and decorations, and you can sell them as NFTs.

>> Buy Tamadoge Now <<

Conclusion

Investing in crypto is never easy; choosing the correct currency is complex. Fortunately, now you can choose among a few exciting and potential currencies and become a part of the big crypto world. Be sure to choose Dash 2 Trade if you want to know all news about the investments and IMPT to resolve the problems with planet pollution. Calvaria or Tamadoge are great for those that love to play games. Any of them could bring you significant earnings."""

device = torch.device('cpu')
preprocess_text = text.strip().replace("\n", "")
t5_prepared_Text = "summarize: "+preprocess_text
tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=1024, truncation=True).to(device)
summary_ids = model.generate(tokenized_text,
                            num_beams=4,
                            min_length=80,
                            max_length=150,
                            length_penalty=2.0,
                            )

print(summary_ids, end="\n")
output = tokenizer.decode(summary_ids[0])
print(output)
