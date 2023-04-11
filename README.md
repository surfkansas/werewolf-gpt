# Werewolf GPT

This repository is an implementation of the ***One Night: Ultimate Werewolf*** game using several GPT instances competing against each other. It was created because I was interested how multiple adversarial GPT models would repond when presented with a goal that would require them to be, shall we say, less than honest with each other.

The game itself is a wonderful social deduction game from Bezier Games. You can purchase it at this link: https://beziergames.com/products/one-night-ultimate-werewolf

![](https://cdn.shopify.com/s/files/1/0740/4855/products/ONUW_272896be-e795-4aec-9e37-ccd43ca0872d_800x.png?v=1653932533)

And *PLEASE* go buy the game. This is a family favorite game, and highly recommended for parties. 

## Running the Game

To run the game, you need to first install the requirements file with the following command:

```shell
pip install -r requirements.txt
```

Next, you should set the `OPENAI_API_KEY` environment variable to your OpenAI API key.

Finally, run the following command:

```
python3 werewolf.py
```

You will now be treated to a session of five AI instances trying to outsmart each other in a social deduction game.

## Issues

First, there is NO error handling. Despite my best prompt engineering, sometimes the model comes back with something that is not a perfect JSON response. This will crash the game. Yes, I hope to fix this in the future.

Second, I have not yet implemented any of the following roles: Doppelganger, Robber, Troublemaker, Drunk, Insomniac, Tanner, Hunter. Yes, I plan on implementing them soon. But, they aren't implemented yet.

Third, the group can descend into an intersting GroupThink where everone is parroting other players. This isn't a bug, per se, but more an emergent behavior about how the GPT model seems to be overly agreeable. I need to figure out how to make it more ruthless. (But, should I *REALLY* focus on making an AI more ruthless?)

## Pull Requests

I accept pull requests. I'm just super busy with my "day job" in AI so can't spend much time on GitHub fun. But, please submit - especially if you fix one of the issues above.