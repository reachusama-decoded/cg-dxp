# Interview transcript: the US end-of-day price sheet

Recorded on a laptop with Voice Memos during a Day 1 style role-play. Three people: **Sam** (data product creator, interviewing), **Priya** (producer: runs the vendor price feed in Data Operations), **Marcus** (consumer: pricing analyst on the US product team). Lightly cleaned; the hesitations are left in because that is what a real transcript looks like.

---

**Sam:** Thanks both. I want to understand what you need before anyone builds anything. Marcus, start with the decision. What decision do you make with this data?

**Marcus:** Every morning the US product team publishes the daily price sheet for our US-listed products. Pricing ops uses it to confirm the closes, sales uses it to answer client questions, and risk takes the USD values into their exposure numbers. The decision is really "are these the closes we stand behind today". If a price looks wrong we hold the sheet and chase it.

**Sam:** How do you make that decision today?

**Marcus:** Honestly, a spreadsheet. Priya's team drops the vendor file somewhere on the share, one of us opens it, filters to our instruments, pastes into the sheet, converts the non-dollar ones by hand with yesterday's FX, and eyeballs anything that moved more than a few percent. It takes about forty minutes if nothing is odd. If the file is late we are late.

**Sam:** Who uses the result directly?

**Marcus:** Three analysts on my team, the sales desk through the morning email, and risk pull the USD column into their own model. Risk is the one that complains if a number changes after they have taken it.

**Sam:** Priya, how is the source generated?

**Priya:** The vendor sends a global end-of-day file after each market closes, so for US names it lands around nine in the evening Eastern. It has every instrument they cover, in the instrument's own currency. Sometimes they re-send a corrected file an hour or two later; the second file has a later vendor timestamp and the same date. We land whatever arrives. We do not do anything to it.

**Sam:** Does the file tell you which instruments are US-listed?

**Priya:** No. That is in the instrument master, which is ours. ISIN is the join. The vendor file has the ISIN and a close price and the price currency. Ticker and market come from the master.

**Sam:** What do the terms mean in your work? When Marcus says "close", is that the same as your "price"?

**Priya:** The vendor's close is the official close on the primary listing. For dual-listed names there can be two rows; we only want the primary one, and the master says which that is.

**Marcus:** And when I say "price" I always mean USD. If something trades in London I still want dollars on the sheet, with the rate we used next to it so risk can check it.

**Sam:** Which rate?

**Marcus:** The same day's close rate. Not yesterday's. That is one of the things the spreadsheet gets wrong.

**Sam:** How do you recognise that the result is usable?

**Marcus:** Every active US instrument has a price for the date. If one is missing I need to know it is missing, not have it silently dropped, because sales will ask about it. Nothing moved more than five percent without someone having looked at it. And it is there by seven thirty Eastern, because the email goes at eight.

**Sam:** When do you read it?

**Marcus:** Seven thirty to eight, Eastern, on US business days. Not weekends, not market holidays. If it is going to be late I want to know by seven, not find out at seven thirty.

**Sam:** Priya, is seven thirty realistic from a nine p.m. file?

**Priya:** Yes, if the FX file is also in. That one comes around five in the afternoon Eastern from a different team. If either is missing at six a.m. we should not pretend. I would rather the run fail loudly than publish yesterday's rate.

**Sam:** What happens today when it is wrong?

**Marcus:** I get a message from risk asking why a number changed. Then I go back through the emails to find out which file we used. I cannot always answer. That is the thing I most want fixed: when a price changes because the vendor corrected it, I want to be able to say "the sheet at seven thirty had the first file; the vendor corrected at nine; here is both".

**Sam:** Who owns this data?

**Priya:** The vendor contract sits with Investment Data. The business owner for prices is the head of pricing operations. My team is the technical owner of the landing, not of what it means.

**Sam:** Is there anything this should not do?

**Marcus:** It should not try to be real-time. People say they want real-time and then they look at it once a day. And it is not a valuation; it is a price sheet. Valuation is somebody else's product.

**Sam:** Last one. Who else would use it if it existed?

**Marcus:** The London product team asked for the same thing for their listings. Different market, same shape. I would build it so that is a filter, not a rewrite.

**Sam:** Thank you both.
