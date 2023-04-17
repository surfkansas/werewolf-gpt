import json
import os
import random
import time

import click
import colorama
import dotenv
import openai
from colorama import Fore, Style

colorama.init()

if os.path.isfile('.env'):
    dotenv.load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

def return_dict_from_json_or_fix(message_json, use_gpt4):
    """
    If the data is valid json, return it as a dictionary, if not, it will attempt to use AI to intelligently fix the JSON.
    If that still does not work, it will print the original (bad) JSON, the new bad JSON, and then exit gracefully.

    This totally badass code came from Yosef Frost: https://github.com/FrostyTheSouthernSnowman
    """

    model = 'gpt-3.5-turbo' if not use_gpt4 else 'gpt-4'

    try:
        message_dict = json.loads(message_json)

    except ValueError:
        completion = openai.ChatCompletion.create(model=model, temperature=0.8, messages=[
            {
                'role': 'user', 
                'content': 'I have a JSON string, but it is not valid JSON. Possibly, the message contains other text besides just the JSON. Could you make it valid? Or, ' \
                + 'if there is valid JSON in the response, please just extact the JSON and do NOT update it. Please respond ONLY in valid JSON! Do not comment on your response. Do not start or ' \
                + 'end with backpacks ("`" or "```")!  You must ONLY respond in JSON! Anything after the colon is JSON I need you to fix. The original message that contains the ' \
                + f'bad JSON is: \n {message_json}'
            }])
        fixed_json = completion.choices[0].message.content
        try:
            message_dict = json.loads(fixed_json)

        except ValueError:
            print('Unable to get valid JSON response from GPT. Exiting program gracefully.')
            print(f'Debug info:\n\tOriginal Response: {message_json}\n\tAttempted Fix: {fixed_json}')
            exit(1)

    return message_dict

class Player:

    def __init__(self, player_name, player_number, other_players, card, card_list, use_gpt4):
        self.player_number = player_number
        self.player_name = player_name
        self.other_players = other_players
        self.card = card
        self.card_thought = card
        self.display_card = card
        self.rules_prompt_prefix = open('prompts/rules.txt').read().format(player_name = player_name, other_players = '; '.join(other_players), card = card, card_list = card_list)
        self.memory = []
        self.use_gpt4 = use_gpt4

    def append_memory(self, memory_item):
        self.memory.append(memory_item)

    def run_prompt(self, prompt):
        full_prompt = self.rules_prompt_prefix

        if len(self.memory) > 0:
            full_prompt += '\n\nYou have the following memory of interactions in this game: \n\n' + '\n\n'.join(self.memory)

        full_prompt += prompt

        model = 'gpt-3.5-turbo' if not self.use_gpt4 else 'gpt-4'
        completion = openai.ChatCompletion.create(model=model, temperature=0.8, messages=[{'role': 'user', 'content': full_prompt}])
        return completion.choices[0].message.content

class ConsoleRenderingEngine:

    player_colors = [Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    def __init__(self):
        pass

    def get_player_colored_name(self, player):
        return f'{self.player_colors[player.player_number - 1]}{Style.BRIGHT}{player.player_name}{Style.RESET_ALL}'

    def type_line(self, text):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(random.uniform(0.005, 0.015))
        print()

    def render_system_message(self, statement, ref_players=[], ref_cards=[], no_wait=False):
        print()
        ref_players_formatted = []
        for player in ref_players:
            ref_players_formatted.append(self.get_player_colored_name(player))
        ref_cards_formatted = []
        for card in ref_cards:
            ref_cards_formatted.append(f'{Fore.RED}{Style.BRIGHT}{card}{Style.RESET_ALL}')
        print(statement.format(ref_players = ref_players_formatted, ref_cards = ref_cards_formatted));
        if not no_wait:
            time.sleep(random.uniform(1, 3))

    def render_phase(self, phase):
        print()
        print(f'=== The {Fore.RED}{Style.BRIGHT}{phase}{Style.RESET_ALL} phase will now commence. ===')

    def render_game_statement(self, statement):
        print()
        print(f'{Fore.WHITE}{Style.BRIGHT}GAME{Style.RESET_ALL}: ', end='')
        self.type_line(statement)
        time.sleep(random.uniform(1, 3))
        
    def render_player_turn_init(self, player):
        print()
        player_colored_name = self.get_player_colored_name(player)
        print(f'{player_colored_name} (thoughts as {player.card_thought}): ', end='', flush=True)

    def render_player_turn(self, player, statement, reasoning):
        player_colored_name = self.get_player_colored_name(player)
        self.type_line(reasoning)
        time.sleep(random.uniform(1, 3))
        if statement is not None:
            print(f'{player_colored_name}: ', end='')
            self.type_line(statement)

    def render_player_vote(self, player, voted_player, reasoning):
        player_colored_name = self.get_player_colored_name(player)
        self.type_line(reasoning)
        time.sleep(random.uniform(1, 3))
        print(f'{player_colored_name} [{player.display_card}]: ', end='')
        self.type_line(f'I am voting for {voted_player}.')

    def render_vote_results(self, votes, players):
        print()
        print('The votes were:')
        print()
        for player in players:
            if votes[player.player_name] > 0:
                print(f'{player.player_name} : {player.card} : {votes[player.player_name]}')

    def render_game_details(self, player_count, discussion_depth, use_gpt4):
        model = 'gpt-3.5-turbo' if not use_gpt4 else 'gpt-4'

        print()
        print('## Run Details')
        print()
        print(f'* Model: {model}')
        print(f'* Player Count: {player_count}')
        print(f'* Discussion Depth: {discussion_depth}')
        print()

class MarkdownRenderingEngine:

    def __init__(self):
        print('# Werewolf GPT - Recorded Play')

    def render_system_message(self, statement, ref_players=[], ref_cards=[], no_wait=False):
        print()
        ref_players_formatted = []
        for player in ref_players:
            ref_players_formatted.append(f'**{player.player_name}**')
        ref_cards_formatted = []
        for card in ref_cards:
            ref_cards_formatted.append(f'***{card}***')
        print(statement.format(ref_players = ref_players_formatted, ref_cards = ref_cards_formatted));

    def render_phase(self, phase):
        print()
        print('---')
        print()
        print(f'## The ***{phase}*** phase will now commence.')

    def render_game_statement(self, statement, ref_players=[], ref_cards=[]):
        print()
        print(f'>***GAME:*** {statement}')

    def render_player_turn_init(self, player):
        # Markdown rendering doesn't need to do anything here. This method is called when
        # an AI begins to think of it's actions.
        pass

    def render_player_turn(self, player, statement, reasoning):
        print()
        print(f'***{player.player_name} (thoughts as {player.card_thought}):*** {reasoning}')
        if statement is not None:
            print(f'> **{player.player_name}:** {statement}')

    def render_player_vote(self, player, voted_player, reasoning):
        print()
        print(f'***{player.player_name} (thoughts as {player.card_thought}):*** {reasoning}')
        print(f'> **{player.player_name} [{player.display_card}]:** I am voting for {voted_player}.')

    def render_vote_results(self, votes, players):
        print()
        print('The votes were:')
        print()
        for player in players:
            if votes[player.player_name] > 0:
                print(f'* {player.player_name} : {player.card} : {votes[player.player_name]}')

    def render_game_details(self, player_count, discussion_depth, use_gpt4):
        model = 'gpt-3.5-turbo' if not use_gpt4 else 'gpt-4'

        print()
        print('## Run Details')
        print()
        print(f'* Model: {model}')
        print(f'* Player Count: {player_count}')
        print(f'* Discussion Depth: {discussion_depth}')

class Game:

    def __init__(self, player_count, discussion_depth, use_gpt4, render_markdown):
        self.player_count = player_count
        self.discussion_depth = discussion_depth
        self.card_list = None
        self.player_names = []
        self.players = []
        self.middle_cards = []
        self.use_gpt4 = use_gpt4

        if render_markdown:
            self.rendering_engine = MarkdownRenderingEngine()
        else:
            self.rendering_engine = ConsoleRenderingEngine()

    def play(self):

        self.initialize_game()
        
        self.rendering_engine.render_system_message(open('intro.txt').read().strip(), no_wait=True)

        self.rendering_engine.render_system_message(self.card_list, no_wait=True)
    
        self.introduce_players()

        self.show_middle_cards()

        self.rendering_engine.render_phase('NIGHT')

        self.rendering_engine.render_game_statement('Everyone, close your eyes.')

        self.night_werewolf()

        self.night_minion()

        self.night_mason()

        self.night_seer()

        self.rendering_engine.render_phase('DAY')

        self.day()

        self.rendering_engine.render_phase('VOTE')

        self.vote()

        self.rendering_engine.render_game_details(self.player_count, self.discussion_depth, self.use_gpt4)

    def initialize_game(self):
        if self.player_count < 3 or self.player_count > 5:
            raise ValueError('Number of players must be between 3 and 5 inclusive.')

        alloted_cards = ['Werewolf', 'Werewolf', 'Seer', 'Mason', 'Mason']

        while len(alloted_cards) < self.player_count + 3:
            if 'Minion' not in alloted_cards:
                alloted_cards.append('Minion')
            else:
                alloted_cards.append('Villager')
        
        card_list = '* ' + '\n* '.join(alloted_cards)
        self.card_list = card_list
        
        random.shuffle(alloted_cards) 

        self.player_names = self.get_player_names(self.player_count)
        self.players = [Player(name, i, self.get_other_players(i, self.player_names), alloted_cards[i - 1], card_list, self.use_gpt4) for i, name in enumerate(self.player_names, 1)]
        self.middle_cards = alloted_cards[self.player_count:] 

    def introduce_players(self):
        for player in self.players:
            self.rendering_engine.render_system_message(f'Player number {player.player_number} is named {{ref_players[0]}}, and they have the {{ref_cards[0]}} card.',
                ref_players=[player], ref_cards=[player.card], no_wait=True)

    def show_middle_cards(self):
        self.rendering_engine.render_system_message('The cards face-down in the middle of the board are {ref_cards[0]}, {ref_cards[1]}, and {ref_cards[2]}.',
            ref_cards=self.middle_cards)    

    def night_werewolf(self):
        self.rendering_engine.render_game_statement('Werewolves, wake up and look for other Werewolves.')

        werewolf_players = [player for player in self.players if player.card == 'Werewolf']

        if len(werewolf_players) == 0:
            self.rendering_engine.render_system_message('There are no werewolves in play.')
        elif len(werewolf_players) == 1:
            middle_card = random.choice(self.middle_cards)

            message = f'GAME: You are the only werewolf. You can deduce that the other werewolf card is in the middle cards. ' \
                + 'You randomly picked one of the center cards and were able to see that it was: {middle_card}'
            werewolf_players[0].append_memory(message)

            self.rendering_engine.render_system_message('There is one werewolf in play, {ref_players[0]}. The werewolf randomly viewed the middle card: {ref_cards[0]}.', 
                ref_players = werewolf_players, ref_cards = [middle_card])
        else:
            message_one = f'GAME (NIGHT PHASE): You are have seen that the other werewolf is {werewolf_players[1].player_name}.'
            werewolf_players[0].append_memory(message_one)
            message_two = f'GAME (NIGHT PHASE): You are have seen that the other werewolf is {werewolf_players[0].player_name}.'
            werewolf_players[1].append_memory(message_two)

            self.rendering_engine.render_system_message('There are two werewolves in play, {ref_players[0]} and {ref_players[1]}. They are both now aware of each other.',
                ref_players = werewolf_players)

        self.rendering_engine.render_game_statement('Werewolves, close your eyes.')

    def night_minion(self):
        self.rendering_engine.render_game_statement('Minion, wake up. Werewolves, stick out your thumb so the Minion can see who you are.')

        minion_players = [player for player in self.players if player.card == 'Minion']
        werewolf_players = [player for player in self.players if player.card == 'Werewolf']

        if len(minion_players) == 0:
            self.rendering_engine.render_system_message('There are no minions in play.')
        else:
            if len(werewolf_players) == 0:
                message = 'GAME (NIGHT PHASE): There are no werewolves in play. Both werewolves are currently in the middle cards.'
                minion_players[0].append_memory(message)

                self.rendering_engine.render_system_message('{ref_players[0]} is a minion and is aware that no one is a werewolf.',
                    ref_players = minion_players)
            elif len(werewolf_players) == 1:
                message = f'GAME (NIGHT PHASE): There are is one werewolf in play. {werewolf_players[0].player_name} is a werewolf. They do not know that you are the minion. ' \
                    + 'The other werewolf is in the middle cards.'
                minion_players[0].append_memory(message)

                self.rendering_engine.render_system_message('{ref_players[0]} is a minion and is aware that {ref_players[1]} is a werewolf.',
                    ref_players = minion_players + werewolf_players)
            else:
                message = f'GAME (NIGHT PHASE): There are two werewolves in play. {werewolf_players[0].player_name} and {werewolf_players[1].player_name} are a werewolves. ' \
                    + 'They do not know that you are the minion.'
                minion_players[0].append_memory(message)

                self.rendering_engine.render_system_message('{ref_players[0]} is a minion and is aware that both {ref_players[1]} and {ref_players[2]} are werewolves.',
                    ref_players = minion_players + werewolf_players)

        self.rendering_engine.render_game_statement('Werewolves, put your thumbs away. Minion, close your eyes.')

    def night_mason(self):
        self.rendering_engine.render_game_statement('Masons, wake up and look for other Masons.')

        mason_players = [player for player in self.players if player.card == 'Mason']

        if len(mason_players) == 0:
            self.rendering_engine.render_system_message('There are no masons in play.')
        elif len(mason_players) == 1:
            message = f'GAME: You are the only mason. You can deduce that the other mason card is in the middle cards.'
            mason_players[0].append_memory(message)

            self.rendering_engine.render_system_message('There is one mason in play, {ref_players[0]}. They are aware they are the only mason in play.',
                ref_players = mason_players)
        else:
            message_one = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[1].player_name}.'
            mason_players[0].append_memory(message_one)
            message_two = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[0].player_name}.'
            mason_players[1].append_memory(message_two)

            self.rendering_engine.render_system_message('There are two masons in play, {ref_players[0]} and {ref_players[1]}. ' \
                + 'They are both now aware of each other.', ref_players = mason_players)

        self.rendering_engine.render_game_statement('Masons, close your eyes.')

    def night_seer(self):
        self.rendering_engine.render_game_statement('Seer, wake up. You may look at another player’s card or two of the center cards.')

        seer_players = [player for player in self.players if player.card == 'Seer']

        if len(seer_players) == 0:
            self.rendering_engine.render_system_message('There are no seers in play.')
        else:
            self.rendering_engine.render_system_message('There is one seer in play, {ref_players[0]}. They are thinking about their action.'
                , ref_players = seer_players)
            
            self.rendering_engine.render_player_turn_init(seer_players[0])

            prompt = open('prompts/seer.txt').read()
            response = seer_players[0].run_prompt(prompt)

            action = return_dict_from_json_or_fix(response, self.use_gpt4)
            reasoning = action['reasoning']
            choice = action['choice']
            
            thoughts_message = f'NIGHT ROUND THOUGHTS: {reasoning}'
            seer_players[0].append_memory(thoughts_message)

            self.rendering_engine.render_player_turn(seer_players[0], None, reasoning)

            if choice == 'player':
                player_name = action['player']
                player = next((p for p in self.players if p.player_name == player_name), None)
                
                message = f'GAME (NIGHT PHASE): You are have seen that {player.player_name} has the card: {player.card}.'
                seer_players[0].append_memory(message)

                self.rendering_engine.render_system_message('The seer looked at a card from {ref_players[0]} and saw the card {ref_cards[0]}',
                    ref_players = [player], ref_cards = [player.card])
            else:
                viewed_cards = random.sample(self.middle_cards, k=2)
                
                message = f'GAME (NIGHT PHASE): You have seen two cards in the center of the table: {viewed_cards[0]} and {viewed_cards[1]}'
                seer_players[0].append_memory(message)
                
                self.rendering_engine.render_system_message('The seer looked at two cards from the center of the table and saw the cards {ref_cards[0]} and {ref_cards[1]}',
                    ref_cards = viewed_cards)

        self.rendering_engine.render_game_statement('Seer, close your eyes.')

    def day(self):
        self.rendering_engine.render_game_statement('Everyone, Wake up!')

        day_prompt = open('prompts/day.txt').read()

        pointer = -1

        discussion_count = 0

        target_player = None

        while discussion_count < self.discussion_depth:
            if target_player is None:
                pointer += 1
                if pointer > len(self.players) - 1:
                    pointer = 0
                player = self.players[pointer]
            else:
                try:
                    player = [player for player in self.players if player.player_name == target_player][0]
                    target_player = None
                except:
                    print()
                    print(f'SYSTEM NOTE: The AI supplied {target_player} as the target player. To avoid a crash, we will skip this directed discussion.')
                    print()

            self.rendering_engine.render_player_turn_init(player)

            response = player.run_prompt(day_prompt)

            action = return_dict_from_json_or_fix(response, self.use_gpt4)
            reasoning = action['reasoning']
            statement = action['statement']
            if 'target_player' in action:
                target_player = action['target_player']

            thoughts_message = f'DAY ROUND THOUGHTS: {reasoning}'
            player.append_memory(thoughts_message)

            message = f'{player.player_name}: {statement}'
            for i_player in self.players:
                i_player.append_memory(message)

            self.rendering_engine.render_player_turn(
                player,
                statement,
                reasoning
            )

            discussion_count += 1

    def vote(self):
        self.rendering_engine.render_game_statement('It\'s time to vote!')

        vote_prompt = open('prompts/vote.txt').read()

        votes = {}

        for player in self.players:
            votes[player.player_name] = 0

        for player in self.players:
            self.rendering_engine.render_player_turn_init(player)

            response = player.run_prompt(vote_prompt)

            action = return_dict_from_json_or_fix(response, self.use_gpt4)
            reasoning = action['reasoning']
            voted_player = action['voted_player']

            self.rendering_engine.render_player_vote(player, voted_player, reasoning)

            votes[voted_player] += 1

        self.rendering_engine.render_vote_results(votes, self.players)

        max_votes = max(votes.values())

        if max_votes == 1:
            werewolf_players = [player for player in self.players if player.card == 'Werewolf']
            minion_players = [player for player in self.players if player.card == 'Minion']

            if len(werewolf_players) + len(minion_players) == 0:
                game_result = 'No player was voted out. The villagers win.'
            else:
                game_result = 'No player was voted out. The werewolves win.'
        else:
            players_with_max_votes = [player for player in self.players if votes[player.player_name] == max_votes]

            if len(players_with_max_votes) > 1:
                game_result = f'There was a tie between {", ".join([player.player_name for player in players_with_max_votes])}.'
                if players_with_max_votes[0].card != 'Werewolf' and players_with_max_votes[1].card != 'Werewolf':
                    game_result += ' The werewolves win.'
                else:
                    game_result += ' The villagers win.'
            else:
                killed_player = players_with_max_votes[0]
                game_result = f'{killed_player.player_name} was killed.'

                if killed_player.card == 'Werewolf':
                    game_result += ' The villagers win.'
                else:
                    game_result += ' The werewolves win.'

        self.rendering_engine.render_game_statement(game_result)

    def get_player_names(self, player_count):
        name_options = ['Alexandra', 'Alexia', 'Andrei', 'Cristina', 'Dragos', 'Dracula', 'Emil', 'Ileana', 'Kraven', 'Larisa', 'Lucian', 'Marius', 'Michael', 'Mircea', 'Radu', 'Semira', 'Selene', 'Stefan', 'Viktor', 'Vladimir']
        return random.sample(name_options, player_count)

    def get_other_players(self, player_number, player_names):
        return [name for i, name in enumerate(player_names, 1) if i != player_number]

#game = Game(player_count = 5, discussion_depth = 20, use_gpt4 = True    , render_markdown = False)
#game.play()

@click.command()
@click.option('--player-count', type=int, default=5, help='Number of players')
@click.option('--discussion-depth', type=int, default=20, help='Number of discussion rounds')
@click.option('--use-gpt4', is_flag=True, default=False, help='Use GPT-4 for discussion')
@click.option('--render-markdown', is_flag=True, default=False, help='Render output as markdown')
def play_game(player_count, discussion_depth, use_gpt4, render_markdown):
    game = Game(player_count=player_count, discussion_depth=discussion_depth, use_gpt4=use_gpt4, render_markdown=render_markdown)
    game.play()

if __name__ == '__main__':
    play_game()
