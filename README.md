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

## Command Arguments

If you want to do cool things like use GPT-4 (assuming you have access to the API), render results to Markdown, or control the size of the game, you can use additional command line args. I am using the `click` library to make this a possibility.

The following example shows all of the args in use:

```shell
python3 werewolf.py --player-count 4 --discussion-depth 3 --use-gpt4 --render-markdown
```

If you want to the see the help for the game, you can run the following command, which will supply help on all args.

```shell
python3 werewolf.py --help

Usage: werewolf.py [OPTIONS]

Options:
  --player-count INTEGER      Number of players
  --discussion-depth INTEGER  Number of discussion questions
  --use-gpt4                  Use GPT-4 for discussion
  --render-markdown           Render output as markdown
  --help                      Show this message and exit.
```

The defaults are 5 players, 20 discussion questions, rendering the console, using the GPT 3.5 Turbo model.

## Recorded Playthroughs

I have included some recorded playthroughs in the [/recorded-games](recorded-games/) folder. These allow people to see the AI and broker in action *without* having to run locally. (And they are great links to share to social media to show of how amazing AI has become!)

## On Names

The simulation utilizes names that are intended to invoke a Transylvanian ambiance.

Initially, I employed an AI to generate a list of names based on the following prompt:

```
Please come up with {player_count} player names for a game of Werewolf. 

Each player name must be unique. Please pick common Transylvanian names. Please pick no names that are also English words.

Please respond with ONLY the names seperated by a semicolon and NO ADDITIONAL TEXT.
```

However, the simulation occasionally encountered errors like the one below:

> As an AI language model, my goal is to promote inclusivity and avoid content that may perpetuate racial or regional stereotypes. I cannot fulfill this request. If you have any other questions or need assistance, please feel free to ask.

I admire OpenAI's decision to raise such concerns, as it demonstrates a commitment to fostering a more inclusive and respectful environment.

To ensure the simulation's functionality, I decided to hard code a list of names in the `get_player_names` method. This list also features names from the *Underworld* movies, which are among my personal favorites, as well as the iconic name of *Dracula*.

My intention in using "stereotypical" Transylvanian names was to bring forth a specific fictional genre in this experiment. However, I want to clarify that I do not aim to perpetuate harmful stereotypes, particularly those concerning the Roma people. The Roma community has faced significant, and at times extreme, racial prejudice. My use of "Transylvanian" names is not meant to reinforce these stereotypes. Striking a balance between referencing popular culture and showing respect for a rich and multifaceted culture can be challenging. I hope that my approach leans towards respect and sensitivity.

## Issues

First, I have not yet implemented any of the following roles: Doppelganger, Robber, Troublemaker, Drunk, Insomniac, Tanner, Hunter. Yes, I plan on implementing them soon. But, they aren't implemented yet.

Second, the group can descend into an intersting GroupThink where everone is parroting other players. This isn't a bug, per se, but more an emergent behavior about how the GPT model seems to be overly agreeable. I need to figure out how to make it more ruthless. (But, should I *REALLY* focus on making an AI more ruthless?). This is only an issue when running with the GPT 3.5 backend, so I might leave this as a cool example of how the two models differ.

Third, the AI seems to *"miss"* on deeper strategy. The main miss is that the Minion player will sometimes try to avoid suspicion and implicate a Werewolf. I need to do some additional prompt engineering to include some strategy hint. (Note: It is cool to see how much strategy the model - especially GPT 4 - is able to derived *just* from the rules.)

## Future Ideas

I realized I (rather poorly) built the voting logic as procedural code. This should *ABSOLUTELY* be an AI doing the scoring. Please drop a PR for that!

## Pull Requests

I accept pull requests. I'm just super busy with my "day job" in AI so can't spend much time on GitHub fun. But, please submit - especially if you fix one of the issues above.

## Contribution Credits

* Yosef Frost - [@FrostyTheSouthernSnowman](https://github.com/FrostyTheSouthernSnowman) - Contributed the *very* cool use of the AI to help re-write bad JSON from responses! (And this dude is still in ***HIGH SCHOOL!*** I am *super* impressed with the creativity!)