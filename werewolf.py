import os
import openai 
import colorama
import random
import json
from colorama import Fore, Style

colorama.init()

class Player:

    player_colors = [Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    def __init__(self, player_name, player_number, other_players, card, card_list):
        self.player_number = player_number
        self.player_name = player_name
        self.other_players = other_players
        self.colored_name = f'{self.player_colors[self.player_number - 1]}{self.player_name}{Style.RESET_ALL}'
        self.card = card
        self.display_card = card
        self.rules_prompt_prefix = open('prompts/rules.txt').read().format(player_name = player_name, other_players = '; '.join(other_players), card = card, card_list = card_list)
        self.memory = []

    def introduce_player(self):
        print(f'Player number {self.player_number} is named {self.colored_name}, and they have the {Fore.RED}{Style.BRIGHT}{self.card}{Style.RESET_ALL} card.')

    def append_memory(self, memory_item):
        self.memory.append(memory_item)

    def run_prompt(self, prompt):
        full_prompt = self.rules_prompt_prefix

        if len(self.memory) > 0:
            full_prompt += '\n\nYou have the following memory of interactions in this game: \n\n' + '\n\n'.join(self.memory)

        full_prompt += prompt

        completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', temperature=0.8, messages=[{'role': 'user', 'content': full_prompt}])
        return completion.choices[0].message.content

class Game:

    def __init__(self, player_count, discussion_depth):
        if player_count < 3 or player_count > 5:
            raise ValueError("Number of players must be between 3 and 5 inclusive.")
        alloted_cards = ['Werewolf', 'Werewolf', 'Seer', 'Mason', 'Mason']
        while len(alloted_cards) < player_count + 3:
            if 'Minion' not in alloted_cards:
                alloted_cards.append('Minion')
            else:
                alloted_cards.append('Villager')
        card_list = '* ' + '\n* '.join(alloted_cards)
        self.card_list = card_list
        random.shuffle(alloted_cards) 
        self.player_names = self.get_player_names(player_count)
        self.players = [Player(name, i, self.get_other_players(i, self.player_names), alloted_cards[i - 1], card_list) for i, name in enumerate(self.player_names, 1)]
        self.middle_cards = alloted_cards[player_count:] 
        self.discussion_depth = discussion_depth

    def show_middle_cards(self):
        print()
        print(f'The cards face-down in the middle of the board are {Fore.RED}{Style.BRIGHT}{self.middle_cards[0]}{Style.RESET_ALL}, {Fore.RED}{Style.BRIGHT}{self.middle_cards[1]}{Style.RESET_ALL}, and {Fore.RED}{Style.BRIGHT}{self.middle_cards[2]}{Style.RESET_ALL}')

    def play(self):
        
        print(open('intro.txt').read())

        print(self.card_list)
    
        print()
        for player in self.players:
            player.introduce_player()

        self.show_middle_cards()

        print()
        print(f'The {Fore.RED}{Style.BRIGHT}NIGHT{Style.RESET_ALL} phase will now commence.')

        self.night_werewolf()

        self.night_minion()

        self.night_mason()

        self.night_seer()

        print()
        print(f'The {Fore.RED}{Style.BRIGHT}DAY{Style.RESET_ALL} phase will now commence.')

        self.day()

        print()
        print(f'The {Fore.RED}{Style.BRIGHT}VOTE{Style.RESET_ALL} phase will now commence.')

        self.vote()


    def night_werewolf(self):
        print()
        werewolf_players = [player for player in self.players if player.card == 'Werewolf']

        if len(werewolf_players) == 0:
            print('There are no werewolves in play.')
        elif len(werewolf_players) == 1:
            middle_card = random.choice(self.middle_cards)
            print(f'There is one werewolf in play, {werewolf_players[0].colored_name}. The werewolf randomly viewed the middle card: {Fore.RED}{Style.BRIGHT}{middle_card}{Style.RESET_ALL}.')
            message = f'GAME: You are the only werewolf. You can deduce that the other werewolf card is in the middle cards. You randomly picked one of the center cards and were able to see that it was: {middle_card}'
            werewolf_players[0].append_memory(message)
        else:
            print(f'There are two werewolves in play, {werewolf_players[0].colored_name} and {werewolf_players[1].colored_name}. They are both now aware of each other.')
            message_one = f'GAME (NIGHT PHASE): You are have seen that the other werewolf is {werewolf_players[1].player_name}.'
            werewolf_players[0].append_memory(message_one)
            message_two = f'GAME (NIGHT PHASE): You are have seen that the other werewolf is {werewolf_players[0].player_name}.'
            werewolf_players[1].append_memory(message_two)

    def night_minion(self):
        print()
        minion_players = [player for player in self.players if player.card == 'Minion']
        werewolf_players = [player for player in self.players if player.card == 'Werewolf']

        if len(minion_players) == 0:
            print('There are no minions in play.')
        else:
            if len(werewolf_players) == 0:
                print(f'{minion_players[0].colored_name} is a minion and is aware that no one is a werewolf.')
                message = 'GAME (NIGHT PHASE): There are no werewolves in play. Both werewolves are currently in the middle cards.'
                minion_players[0].append_memory(message)
            elif len(werewolf_players) == 1:
                print(f'{minion_players[0].colored_name} is a minion and is aware that {werewolf_players[0].colored_name} is a werewolf.')
                message = f'GAME (NIGHT PHASE): There are is one werewolf in play. {werewolf_players[0].player_name} is a werewolf. They do not know that you are the minion. The other werewolf is in the middle cards.'
                minion_players[0].append_memory(message)
            else:
                print(f'{minion_players[0].colored_name} is a minion and is aware that both {werewolf_players[0].colored_name} and {werewolf_players[1].colored_name} are werewolves.')
                message = f'GAME (NIGHT PHASE): There are two werewolves in play. {werewolf_players[0].player_name} and {werewolf_players[1].player_name} are a werewolves. They do not know that you are the minion.'
                minion_players[0].append_memory(message)

    def night_mason(self):
        print()
        mason_players = [player for player in self.players if player.card == 'Mason']

        if len(mason_players) == 0:
            print('There are no masons in play.')
        elif len(mason_players) == 1:
            middle_card = random.choice(self.middle_cards)
            print(f'There is one mason in play, {mason_players[0].colored_name}. They are aware they are the only mason in play.')
            message = f'GAME: You are the only mason. You can deduce that the other mason card is in the middle cards.'
            mason_players[0].append_memory(message)
        else:
            print(f'There are two masons in play, {mason_players[0].colored_name} and {mason_players[1].colored_name}. They are both now aware of each other.')
            message_one = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[1].player_name}.'
            mason_players[0].append_memory(message_one)
            message_two = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[0].player_name}.'
            mason_players[1].append_memory(message_two)

    def night_mason(self):
        print()
        mason_players = [player for player in self.players if player.card == 'Mason']

        if len(mason_players) == 0:
            print('There are no masons in play.')
        elif len(mason_players) == 1:
            middle_card = random.choice(self.middle_cards)
            print(f'There is one mason in play, {mason_players[0].colored_name}. They are aware they are the only mason in play.')
            message = f'GAME: You are the only mason. You can deduce that the other mason card is in the middle cards.'
            mason_players[0].append_memory(message)
        else:
            print(f'There are two masons in play, {mason_players[0].colored_name} and {mason_players[1].colored_name}. They are both now aware of each other.')
            message_one = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[1].player_name}.'
            mason_players[0].append_memory(message_one)
            message_two = f'GAME (NIGHT PHASE): You are have seen that the other mason is {mason_players[0].player_name}.'
            mason_players[1].append_memory(message_two)

    def night_seer(self):
        print()

        seer_players = [player for player in self.players if player.card == 'Seer']

        if len(seer_players) == 0:
            print('There are no seers in play.')
        else:
            print(f'There is one seer in play, {seer_players[0].colored_name}. They are thinking about their action.')
            prompt = open('prompts/seer.txt').read()
            response = seer_players[0].run_prompt(prompt)
            action = json.loads(response)
            reasoning = action['reasoning']
            choice = action['choice']
            print()
            print(f'{seer_players[0].colored_name} {Fore.RED}{Style.DIM}(thougts): {reasoning}{Style.RESET_ALL}')
            thoughts_message = f'NIGHT ROUND THOUGHTS: {reasoning}'
            seer_players[0].append_memory(thoughts_message)

            if choice == 'player':
                player_name = action['player']
                player = next((p for p in self.players if p.player_name == player_name), None)
                meesage = f'GAME (NIGHT PHASE): You are have seen that {player.player_name} has the card: {player.card}.'
                seer_players[0].append_memory(meesage)
                print()
                print(f'The seer looked at a card from {player.colored_name} and saw the card: {Fore.RED}{Style.BRIGHT}{player.card}{Style.RESET_ALL}')
            else:
                viewed_cards = random.sample(self.middle_cards, k=2)
                meesage = f'GAME (NIGHT PHASE): You have seen two cards in the center of the table: {viewed_cards[0]} and {viewed_cards[1]}'
                seer_players[0].append_memory(meesage)
                print()
                print(f'The seer looked at two cards from the center of the table and saw the cards: {Fore.RED}{Style.BRIGHT}{viewed_cards[0]}{Style.RESET_ALL}, {Fore.RED}{Style.BRIGHT}{viewed_cards[1]}{Style.RESET_ALL}')

    def day(self):
        day_prompt = open('prompts/day.txt').read()

        pointer = -1

        discussion_count = 0

        target_player = None

        while discussion_count <= self.discussion_depth:
            if target_player is None:
                pointer += 1
                if pointer > len(self.players) - 1:
                    pointer = 0
                player = self.players[pointer]
            else:
                player = [player for player in self.players if player.player_name == target_player][0]
                target_player = None

            response = player.run_prompt(day_prompt)

            action = json.loads(response)
            reasoning = action['reasoning']
            statement = action['statement']
            if 'target_player' in action:
                target_player = action['target_player']

            print()
            print(f'{player.colored_name} {Fore.RED}{Style.DIM}(thougts): {reasoning}{Style.RESET_ALL}')
            thoughts_message = f'DAY ROUND THOUGHTS: {reasoning}'
            player.append_memory(thoughts_message)

            print(f'{player.colored_name} [{player.display_card}]: {statement}')
            message = f'{player.player_name}: {statement}'
            for i_player in self.players:
                i_player.append_memory(message)

            discussion_count += 1

    def vote(self):
        vote_prompt = open('prompts/vote.txt').read()

        votes = {}

        for player in self.players:
            votes[player.player_name] = 0

        for player in self.players:
            response = player.run_prompt(vote_prompt)

            action = json.loads(response)
            reasoning = action['reasoning']
            voted_player = action['voted_player']

            print()
            print(f'{player.colored_name} {Fore.RED}{Style.DIM}(thougts): {reasoning}{Style.RESET_ALL}')
            print(f'{player.colored_name} [{player.display_card}]: I am voting for {voted_player}')

            message = f'{player.player_name}: I am voting for {voted_player}'
            for i_player in self.players:
                i_player.append_memory(message)

            votes[voted_player] += 1

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

        print()
        print(f'{Fore.RED}{Style.BRIGHT}GAME{Style.RESET_ALL}: {game_result}')

    def get_player_names(self, player_count):
        message = open('prompts/names.txt').read().format(player_count = player_count)
        completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', temperature=0.0, messages=[{'role': 'user', 'content': message}])
        return [name.strip() for name in completion.choices[0].message.content.split(';')]

    def get_other_players(self, player_number, player_names):
        return [name for i, name in enumerate(player_names, 1) if i != player_number]

game = Game(player_count = 5, discussion_depth = 15)
game.play()