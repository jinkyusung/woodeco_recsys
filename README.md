# Woodeco RecSys

**Remarks**  
* Files with the prefix `_` in their names are python scripts for some thesis experiments.
* This python program encapsulates API secrets by using `.env` files. So, you _should configure it **yourself**_.
* The Papago Translate API and OpenAI API are time-consuming and expensive, so this program uses cached data to minimize API calls.
This is beneficial because the data for API calculations is largely redundant.