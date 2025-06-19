"""
Game interaction methods for Colony 4B.
Contains all NPC quest handlers and special location interactions.
"""
import logging
import time
import sys
import random
from typing import Optional, List
from items import Item, ITEMS
from room import Room
from game_constants import *

class GameInteractions:
    """Mixin class containing all game interaction methods."""

    def _complete_quest(
        self,
        quest_flag_name: str,
        npc_name: str,
        npc_room: Room,
        appreciation_func: callable,
        item_to_remove: Optional[Item] = None
    ) -> bool:
        """
        A generic method to handle the completion of an NPC quest.
        """
        if item_to_remove:
            self.player.remove_from_inventory(item_to_remove)

        setattr(self.player, quest_flag_name, True)
        logging.info(f"Player completed {npc_name}'s quest.")

        try:
            # Find the NPC with or without the checkmark
            original_npc_name = npc_name.replace(" ✓", "").strip()
            npc_to_find = next(
                (npc for npc in npc_room.npcs if original_npc_name in npc),
                None
            )
            if npc_to_find:
                npc_index = npc_room.npcs.index(npc_to_find)
                npc_room.npcs[npc_index] = f"{original_npc_name} ✓"
        except (ValueError, AttributeError):
            logging.warning(
                f"Could not find {npc_name} in {npc_room.name} to update status."
            )
        
        appreciation_func()

        if self.player.all_quests_complete():
            self.display_good_ending()
            return True
        
        self.current_room.set_interaction_state("main")
        return True

    def _handle_cecil_coin_quest(self) -> bool:
        """
        Handles the logic for giving the lucky coin to Greyman Cecil.
        """
        if self.current_room.current_interaction_state != "cecil_quest_prompt":
            self.current_room.add_message("That doesn't make sense right now.")
            return True

        if not self.player.has_item(ITEMS["lucky coin"]):
            self.current_room.add_message("You don't have the lucky coin to offer.")
            return True
        
        return self._complete_quest(
            quest_flag_name="cecil_quest_complete",
            npc_name="Greyman Cecil",
            npc_room=self.residential_corridor,
            appreciation_func=self.display_cecil_appreciation,
            item_to_remove=ITEMS["lucky coin"]
        )

    def _handle_ephsus_soil_quest(self) -> bool:
        """
        Handles the logic for turning in Thebian Ground Soil to Science Officer Ephsus.

        Checks the player's inventory for soil, updates the quest progress,
        removes the soil, and triggers the quest completion if the required
        amount has been provided.
        """
        if self.current_room.current_interaction_state != "ephsus_quest_prompt":
            self.current_room.add_message("That doesn't make sense right now.")
            return True

        soil_in_inventory = [item for item in self.player.inventory if item.name == "Thebian Ground Soil"]
        soil_count = len(soil_in_inventory)
        
        needed = SOIL_SAMPLES_REQUIRED - self.player.ephsus_soil_given

        if soil_count == 0:
            self.current_room.add_message(
                "You have no Thebian Ground Soil in your inventory. Ephsus "
                "looks at you with anticipation."
            )
            return True

        gave_count = min(soil_count, needed)
        
        for _ in range(gave_count):
            self.player.inventory.remove(next(item for item in self.player.inventory 
                                          if item.name == "Thebian Ground Soil"))
            
        self.player.ephsus_soil_given += gave_count
        
        if self.player.ephsus_soil_given >= SOIL_SAMPLES_REQUIRED:
            return self._complete_quest(
                quest_flag_name="ephsus_quest_complete",
                npc_name="Science Officer Ephsus",
                npc_room=self.central_plaza,
                appreciation_func=self.display_ephsus_appreciation
            )
        else:
            remaining = SOIL_SAMPLES_REQUIRED - self.player.ephsus_soil_given
            self.current_room.add_message(
                f"You gave Ephsus {gave_count} Thebian Ground Soil samples. "
                f"Just {remaining} more to go. Thank you very much Marmoris. "
                f"I appreciate that massively."
            )
        return True

    def _handle_creedal_food_quest(self) -> bool:
        """
        Handles the logic for giving Steamed Buns to Security Officer Creedal.
        """
        if self.current_room.current_interaction_state != "creedal_quest_prompt":
            self.current_room.add_message("That doesn't make sense right now.")
            return True

        if not self.player.has_item(ITEMS["Steamed Buns"]):
            self.current_room.add_message("You don't have Steamed Buns to offer.")
            return True

        return self._complete_quest(
            quest_flag_name="creedal_quest_complete",
            npc_name="Security Officer Creedal",
            npc_room=self.current_room,
            appreciation_func=self.display_creedal_appreciation,
            item_to_remove=ITEMS["Steamed Buns"]
        )

    def _handle_weatherbee_spirits_quest(self) -> bool:
        """
        Handles the logic for giving a high five to Security Officer Weatherbee.
        """
        if self.current_room.current_interaction_state != "weatherbee_spirits_prompt":
            self.current_room.add_message("That doesn't make sense right now.")
            return True

        return self._complete_quest(
            quest_flag_name="weatherbee_quest_complete",
            npc_name="Security Officer Weatherbee",
            npc_room=self.security_checkpoint_industrial,
            appreciation_func=self.display_weatherbee_appreciation
        )

    def _handle_buy_comms_tower_card(self) -> bool:
        """
        Handles the logic for purchasing the Communications Tower ID Card.
        """
        if self.current_room.current_interaction_state != "blackest_market":
            self.current_room.add_message("You can only do this at the Blackest of Markets stall.")
            return True

        if self.player.bought_blackest_market_card:
            self.current_room.add_message("The shadowy figure is gone.")
            return True

        if self.player.minshin >= BLACK_MARKET_ID_PRICE:
            if self.player.is_inventory_full():
                self.current_room.add_message("Your inventory is full.")
                return True

            self.player.minshin -= BLACK_MARKET_ID_PRICE
            self.player.add_to_inventory(ITEMS["Communications Tower ID Card"])
            self.player.bought_blackest_market_card = True
            
            self.current_room.add_message("You slide the Minshin across. The "
                                          "figure hands you a surprisingly "
                                          "well-made ID card and melts back "
                                          "into the shadows. The stall is gone.")
            
            # Remove the stall interaction from the market
            self.colony_market.interaction_states["main"].interactions.remove(
                "approach Blackest of Markets stall"
            )
            self.current_room.set_interaction_state("main")

        else:
            self.current_room.add_message(
                f"You don't have enough Minshin. The figure scoffs at your "
                f"{self.player.minshin} Minshin."
            )
        
        return True

    def handle_donation(self, amount_str: str) -> bool:
        """
        Handles the player's input when in the 'donating' state.
        """
        if amount_str.lower() == "go back":
            self.current_room.set_interaction_state("main")
            self.current_room.add_message("You step back from the donation bucket.")
            return False

        try:
            amount = int(amount_str)
            if amount < MINIMUM_DONATION:
                self.current_room.add_message(f"You must donate at least {MINIMUM_DONATION} Minshin.")
            elif amount > self.player.minshin:
                self.current_room.add_message(f"You don't have enough Minshin. You only have {self.player.minshin}.")
            else:
                self.player.minshin -= amount
                self.total_donations += amount
                self.current_room.add_message(
                    f"You donated {amount} Minshin. You feel a bit better "
                    f"about the state of the colony."
                )
                self.current_room.set_interaction_state("main")
                self.check_for_foreman_spawn()
        except (ValueError, TypeError):
            self.current_room.add_message("Please enter a valid number or type 'go back'.")
        
        return False

    def mine_away(self) -> None:
        """
        Handles the 'MINE AWAY' command.
        """
        if self.time.hours >= FACILITY_CLOSE_HOUR:
            self.current_room.add_message(
                f"The mines are closed. It's too late in the day. "
                f"Mines are open from 00:00 to {FACILITY_CLOSE_HOUR}:00."
            )
            return
            
        if not self.player.has_item(ITEMS["mining gun"]):
            self.current_room.add_message("You need a mining gun to mine.")
            return
        
        if self.player.is_inventory_full():
            self.current_room.add_message(
                "Your inventory is full. You can't carry any more resources."
            )
            return

        animation_chars = ['|', '/', '-', '\\']
        duration = random.uniform(0.5, 2.0)
        start_time = time.time()
        while time.time() - start_time < duration:
            for char in animation_chars:
                sys.stdout.write(f"\rMining... [{char}]")
                sys.stdout.flush()
                time.sleep(0.1)
                if time.time() - start_time > duration:
                    break
        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()
        
        self.time.advance_time(0.5)
        
        mine_count = 3 if self.player.bought_mining_gun_upgrade else 1
        
        mined_items = []
        for _ in range(mine_count):
            self.mining_attempts += 1 

            if (self.mining_attempts >= SKELETON_DISCOVERY_THRESHOLD and
                    random.random() < SKELETON_DISCOVERY_CHANCE and
                    not self.player.has_found_skeleton):
                self.player.has_found_skeleton = True
                self._display_dramatic_discovery("you have mined:", "Skeleton")
                self.display_skeleton_ending()
                return

            if self.player.is_inventory_full():
                mined_items.append(
                    "Your inventory is now full. You can't carry any more resources."
                )
                break

            mining_results = [
                ("Thebian Ground Soil", 60),
                ("Ambrosium Crystal", 20),
                ("Clagnum Putty", 10),
                ("Matterstone Ore", 5),
                ("Ambrosium Cluster", 5)
            ]
            
            item_name = random.choices(
                [result[0] for result in mining_results],
                weights=[result[1] for result in mining_results]
            )[0]
            
            item = ITEMS[item_name]
            if self.player.add_to_inventory(item):
                mined_items.append(f"You have mined: {item.name}.")
            else:
                mined_items.append(
                    f"Could not add {item.name}, inventory is now full."
                )
        
        for msg in mined_items:
            self.current_room.add_message(msg)

    def deposit_resources(self) -> None:
        """
        Handles the process of depositing Ambrosium resources.
        """
        items_to_deposit = [item for item in self.player.inventory if item.name in ["Ambrosium Crystal", "Ambrosium Cluster"]]

        if not items_to_deposit:
            self.current_room.add_message("You have no Ambrosium to deposit.")
            return

        self.time.advance_time(0.5)
        
        self._run_deposit_terminal_animation([
            ("Starting spectroscopy...", random.uniform(1.0, 1.5)),
            ("Spectroscopy complete. Starting valuation assessment...", random.uniform(1.5, 2.0)),
            ("Valuation complete. Appending submission to quota...", random.uniform(1.0, 1.5)),
        ])

        from collections import Counter
        item_counts = Counter(item.name for item in items_to_deposit)
        
        total_quota_progress = 0
        total_earnings = 0
        deposit_messages = []

        is_post_quota = self.player.quota_fulfilled >= self.player.ambrosium_quota
        quota_met_before = is_post_quota

        if "Ambrosium Crystal" in item_counts:
            count = item_counts["Ambrosium Crystal"]
            if is_post_quota:
                earnings = count * MINSHIN_PER_AMBROSIUM_POST_QUOTA
                total_earnings += earnings
                self.player.minshin += earnings
                self.player.quota_fulfilled += count
                deposit_messages.append(
                    f"Successfully deposited Ambrosium Crystal x{count} for a "
                    f"bonus of {earnings} Minshin."
                )
            else:
                self.player.quota_fulfilled += count
                total_quota_progress += count
                deposit_messages.append(
                    f"Successfully deposited Ambrosium Crystal x{count}. Quota "
                    f"progress: +{count}."
                )

        if "Ambrosium Cluster" in item_counts:
            count = item_counts["Ambrosium Cluster"]
            if is_post_quota:
                earnings = count * AMBROSIUM_CLUSTER_VALUE * MINSHIN_PER_AMBROSIUM_POST_QUOTA
                total_earnings += earnings
                self.player.minshin += earnings
                self.player.quota_fulfilled += (count * AMBROSIUM_CLUSTER_VALUE)
                deposit_messages.append(
                    f"Successfully deposited Ambrosium Cluster x{count} for a "
                    f"bonus of {earnings} Minshin."
                )
            else:
                progress = count * AMBROSIUM_CLUSTER_VALUE
                self.player.quota_fulfilled += progress
                total_quota_progress += progress
                deposit_messages.append(
                    f"Successfully deposited Ambrosium Cluster x{count}. Quota "
                    f"progress: +{progress}."
                )

        self.player.inventory = [
            item for item in self.player.inventory 
            if item.name not in ["Ambrosium Crystal", "Ambrosium Cluster"]
        ]

        for msg in deposit_messages:
            print(msg)
        
        if total_quota_progress > 0:
            print(f"Total quota progress this deposit: {total_quota_progress}.")
        
        if total_earnings > 0:
            print(f"Total bonus earnings: {total_earnings} Minshin. Your balance is now {self.player.minshin}.")

        quota_met_after = self.player.quota_fulfilled >= self.player.ambrosium_quota
        if quota_met_after and not quota_met_before:
            self.suppress_next_room_display = False
            self.display_quota_celebration()
            self.player.quota_celebration_shown = True

    def deposit_non_ambrosium(self) -> None:
        """
        Handles the process of depositing non-Ambrosium materials for Minshin.
        """
        logging.info("deposit_non_ambrosium method called")
        
        minshin_rates = {
            "Thebian Ground Soil": SOIL_SELL_PRICE,
            "Clagnum Putty": CLAGNUM_SELL_PRICE,
            "Matterstone Ore": MATTERSTONE_SELL_PRICE
        }

        items_to_deposit = [item for item in self.player.inventory if item.name in minshin_rates]

        if not items_to_deposit:
            self.current_room.add_message("You have no non-Ambrosium materials to deposit.")
            return

        self.time.advance_time(0.5)
        
        self._run_deposit_terminal_animation([
            ("Sorting materials...", random.uniform(1.0, 1.5)),
            ("Assessing materials...", random.uniform(1.0, 1.5)),
            ("Checking condition...", random.uniform(1.5, 2.0)),
            ("Assessment complete. Appending respective Minshin to balance...", random.uniform(1.0, 1.5)),
        ])

        from collections import Counter
        item_counts = Counter(item.name for item in items_to_deposit)
        
        total_earnings = 0
        deposit_messages = []

        for item_name, count in item_counts.items():
            rate = minshin_rates[item_name]
            earnings = count * rate
            total_earnings += earnings
            
            deposit_messages.append(f"Successfully deposited {item_name} x{count} = {earnings} Minshin")

        inventory_counts = Counter(item.name for item in self.player.inventory)
        for item_name in item_counts:
            inventory_counts[item_name] -= item_counts[item_name]
        
        new_inventory = []
        for item in self.player.inventory:
            if inventory_counts[item.name] > 0:
                new_inventory.append(item)
                inventory_counts[item_name] -= 1
        self.player.inventory = new_inventory

        self.player.minshin += total_earnings

        for msg in deposit_messages:
            print(msg)
        
        if total_earnings > 0:
            print(f"Total earnings: {total_earnings} Minshin. Your balance is now {self.player.minshin}.")

    def display_deportation_ending(self) -> None:
        """
        Displays the standard game over screen for failing the quota.
        """
        paragraphs = [
            "Deportation Officer Grove approaches you.",
            "",
            "\"Marmoris Gold?\" he asks, his voice devoid of emotion.",
            "",
            "\"Yes,\" you respond quietly.",
            "",
            ("\"Come with me.\" He extends an arm, guiding you toward the "
             "communications tower. Walking in to the lobby of the communications tower "
             "it seems surprisingly empty.The guards step aside as you're led inside, "
             "their eyes carefully avoiding yours. You enter what appears to be "
             "a completely bare room, and Grove takes position behind you."),
            ("Standing tall with your 97 Thebian years of service, you feel "
             "prepared for whatever comes next. Security officers lay a "
             "human-shaped bag in front of you, decorated with Olympus Resources "
             "logos. One label in particular catches your eye: \"Please input "
             "all required information before submitting items for cremation.\""),
            "You feel something hard and cold pressed against the back of your head."
        ]
        self._display_ending_text(paragraphs, "GAME OVER")

    def display_skeleton_ending(self) -> None:
        """
        Displays the secret ending triggered by discovering the skeleton.
        """
        paragraphs = [
            ("The bones surface from the dirt, scattered across the mining floor. "
             "Your cry of alarm draws the other miners, and together you stare "
             "at the remains. Forensic analysis identifies the skeleton as Flek, "
             "an Ambrosium miner from Colony 4A. Flek was found with a bullet "
             "hole in their skull. The remains of the bullet "
             "was positively matched to standard Olympus Resources enforcer rounds."),
            ("Word spreads fast. Fueled by anger and fear, Colony 4B storms the "
             "communications tower. The two security officers behind the entrance "
             "fall with minimal resistance, but the lobby is nearly empty, just a single "
             "Deportation Officer, who swears the two guards were the only "
             "ones ever stationed there. Under questioning, Grove reveals that "
             "all directives arrive through a lobby terminal, the same one "
             "Foreman Long uses to receive his political directives. There is no "
             "access to the upper disk where the \"communications team\" "
             "supposedly works."),
            ("The search of the lobby turns up nothing but cremation bags, a "
             "crude reality to the \"deportation\", as well as no evidence of "
             "real communication with the outside. A desperate attempt to break "
             "into the upper levels finds only empty rooms lined with silent "
             "terminals, all set to auto-send reports to company headquarters."),
            ("Hacking these advanced terminals finally exposes the truth: Colony "
             "4A attempted rebellion, initially for increased salary and better working "
             "conditions, but they discovered the reality behind deportation."
             "Olympus Resources responded with riot "
             "suppression. When that failed, they sealed the colony. There was "
             "no collapse, it was an mass execution."),
            ("Worse, the archived data reveals a final betrayal to ensure that a "
             "riot will never happen again. All oxygen generators are programmed "
             "with a 100-year lifespan, to be switched off as a \"cost-effective\" "
             "measure. For Colony 4B, that means three years remain before the "
             "air runs out—no matter what you do."),
            ("You stand with your fellow miners, silent in the knowledge that "
             "death was always inevitable.")
        ]
        self._display_ending_text(paragraphs, "GAME OVER")

    def display_average_worker_ending(self) -> None:
        """
        Displays the 'average worker' ending.
        """
        paragraphs = [
            "The three day cycle is up.",
            ("Please check you personal terminal for updates regarding qoutas, "
             "news and more for the next cycle."),
            "'together we are strong' – Olympus Rescouces"
        ]
        self._display_ending_text(paragraphs, "THE END")

    def display_good_ending(self) -> None:
        """
        Displays the 'good' ending.
        """
        paragraphs = [
            ("After earning the respect and trust of members of Colony 4B, "
             "your influence cannot be ignored. On the morning of the subsequent "
             "day, Foreman Long gathers the entire colony. To everyone's "
             "surprise, he stands beside you."),
            ("\"This colony survives because we work together. From today, we are "
             "co-foremen.\""),
            ("With your leadership, the colony turns its focus from mere "
             "survival to real independence. Investigations into the recent mass oxygen "
             "generators failures and the "
             "discovery of a skeleton from the buried Colony 4A—reveal the truth: "
             "Olympus Resources sealed 4A to crush a rebellion, then covered up "
             "the atrocity."),
            ("Determined not to share the same fate, you and Long unite the "
             "colony behind a new plan. Every quota is met to avoid suspicion, "
             "but all political orders from Olympus Resources are quietly "
             "ignored. Work begins to overhaul the oxygen system: mass "
             "generator repairs, and, with Ephsus's help, the planting of hardy "
             "engineered crops grown from a single dormant seed found in one of her "
             "soil audits. Cecil, once a clagnum miner, becomes the colony's first "
             "gardener."),
            ("The communications tower, once the symbol of control, is bypassed "
             "entirely. When security finally intervenes, it's just two guards "
             "and a Deportation Officer. Outnumbered and unsure, they are "
             "simply invited into the new, self-governing society."),
            ("Centuries pass. Five hundred Thebian years after your promotion to leadership, "
             "the last oxygen generator is dismantled. The air is now rich "
             "with the breath of green life, and the colony's fields and "
            "gardens thrive. Olympus Resources continues to receive its regular "
             "shipments of Ambrosium, unaware that Colony 4B has quietly "
             "slipped its leash and built a future of its own making."),
            (" This colony is free—not by force, but by unity.")
        ]
        self._display_ending_text(paragraphs, "THE END")

    def display_foreman_appreciation(self) -> None:
        """
        Displays Colony Foreman Long's appreciation message.

        Triggered by completing his donation 'quest'. It runs the fireworks
        animation and shows his thank you message.
        """
        self._display_appreciation_animation(
            "Colony Foreman Long",
            "Marmoris my dear boy. You have donated more Minshin for the upkeep "
            "of our colony that I could count! I just wanted to swing by and "
            "give my thanks. We could be great together you know."
        )
        self.current_room.set_interaction_state("main")

    def display_ephsus_appreciation(self) -> None:
        """
        Displays Science Officer Ephsus's appreciation message.
        """
        self._display_appreciation_animation(
            "Science Officer Ephsus",
            "You may have just saved my skin marmoris! With these samples I can "
            "get my audit in tip top shape. I could even do a soil acidity "
            "test, or maybe even an enzyme assay... YAHOO!"
        )

    def display_cecil_appreciation(self) -> None:
        """
        Displays Greyman Cecil's appreciation message.
        """
        self._display_appreciation_animation(
            "Greyman Cecil",
            "Cecil takes a knee as he clutches the coin in hand. Raising his "
            "head he is brandishing a smile that has twisted his face out of "
            "proportion. 'You have made this poor greyman so damn happy'"
        )

    def display_creedal_appreciation(self) -> None:
        """
        Displays Security Officer Creedal's appreciation message.
        """
        self._display_appreciation_animation(
            "Security Officer Creedal",
            '"Woah. These look incredible..." "Delicious!" He seemed to be '
            'completely mesmerised.'
        )

    def display_weatherbee_appreciation(self) -> None:
        """
        Displays Security Officer Weatherbee's appreciation message.
        """
        self._display_appreciation_animation(
            "Security Officer Weatherbee",
            'Weatherbee\'s spirits became noticeably more optimistic. He '
            'repositioned himself on his chair so he sat tall, brandished a '
            'smile and wide optimistic eyes. "good for him" you think to yourself.'
        )

    def handle_market_stall(self) -> None:
        """
        Handles the interaction with Merchant Armeda's stall.
        """
        self.current_room.set_interaction_state("market_stall")
        
        if self.player.bought_xl_backpack and self.player.bought_steamed_buns and self.player.bought_mining_gun_upgrade:
            self.current_room.add_message(
                "You have run me dry, please come back next cycle for new goods!."
            )
            self.current_room.interaction_states["market_stall"].interactions = ["go back"]
            return

        self.current_room.add_message("ah hello there. take a gander at my goods?")
        
        interactions = []
        if not self.player.bought_xl_backpack:
            interactions.append(f"buy Olympus XL Backpack ({BACKPACK_PRICE} Minshin)")
        else:
            interactions.append("Olympus XL Backpack -bought-")
            
        if not self.player.bought_steamed_buns:
            interactions.append(f"buy Steamed Buns ({STEAMED_BUNS_PRICE} Minshin)")
        else:
            interactions.append("Steamed Buns -bought-")
            
        if not self.player.bought_mining_gun_upgrade:
            interactions.append(
                f"buy Heavy Beam Mining Gun Upgrade ({MINING_UPGRADE_PRICE} Minshin)"
            )
        else:
            interactions.append("Heavy Beam Mining Gun Upgrade -bought-")
            
        interactions.append("go back")
        self.current_room.interaction_states["market_stall"].interactions = interactions

    def buy_market_item(self, item_key: str) -> None:
        """
        Handles the logic for purchasing an item from the market.
        """
        if self.current_room.current_interaction_state != "market_stall":
            self.current_room.add_message("You need to be at the stall to buy things.")
            return

        if item_key == "backpack":
            if self.player.bought_xl_backpack:
                self.current_room.add_message("You already bought the backpack.")
                return
            if self.player.minshin >= BACKPACK_PRICE:
                self.player.minshin -= BACKPACK_PRICE
                self.player.max_inventory = MAX_INVENTORY_UPGRADED
                self.player.bought_xl_backpack = True
                self.current_room.add_message(
                    f"Your inventory space has increased from {MAX_INVENTORY_DEFAULT} "
                    f"to {MAX_INVENTORY_UPGRADED}!"
                )
                self.handle_market_stall() 
            else:
                self.current_room.add_message("You don't have enough Minshin for that.")
        
        elif item_key == "buns":
            if self.player.bought_steamed_buns:
                self.current_room.add_message("You already bought the steamed buns.")
                return
            if self.player.minshin >= STEAMED_BUNS_PRICE:
                if self.player.is_inventory_full():
                    self.current_room.add_message("Your inventory is full.")
                    return
                self.player.minshin -= STEAMED_BUNS_PRICE
                self.player.add_to_inventory(ITEMS["Steamed Buns"])
                self.player.bought_steamed_buns = True
                self.current_room.add_message("You bought the Steamed Buns.")
                self.handle_market_stall()
            else:
                self.current_room.add_message("You don't have enough Minshin for that.")

        elif item_key == "gun":
            if self.player.bought_mining_gun_upgrade:
                self.current_room.add_message("You already bought the mining gun upgrade.")
                return
            if self.player.minshin >= MINING_UPGRADE_PRICE:
                self.player.minshin -= MINING_UPGRADE_PRICE
                self.player.bought_mining_gun_upgrade = True
                self.current_room.add_message("You bought the Heavy Beam Mining Gun Upgrade.")
                self.handle_market_stall()
            else:
                self.current_room.add_message("You don't have enough Minshin for that.")

    def visit_hinter(self) -> None:
        """
        Handles the interaction with Hinter's Prophecies.
        """
        self.current_room.set_interaction_state("hinter_prophecies")
        initial_message = "An old woman sits in a dimly lit corner, her eyes clouded but focused on you. 'The threads of fate are tangled,' she rasps. 'What is it you wish to know?'"
        self.current_room.add_message(initial_message)

    def handle_hinter_prophecy(self) -> None:
        """
        Handles the logic for receiving a prophecy from Hinter.
        """
        if self.current_room.current_interaction_state != "hinter_prophecies":
            self.current_room.add_message("That doesn't make sense right now.")
            return

        if self.player.minshin < PROPHECY_COST:
            self.current_room.add_message(f"You do not have enough Minshin. A reading costs {PROPHECY_COST}.")
            return

        self.player.minshin -= PROPHECY_COST

        prophecies = []
        if not self.player.creedal_quest_complete:
            prophecies.append("'Even guards need to eat sometimes. I heard the steamed buns next door are lovely.'")
        if not self.player.long_quest_complete:
            prophecies.append("'Donations are always welcome at the memorial pond.'")
        if not self.player.cecil_quest_complete:
            prophecies.append("'One of the miners has lost their coin.'")
        if not self.player.weatherbee_quest_complete:
            prophecies.append(
                "'Sometimes the job vacancies on the bulletin board can help "
                "more than just you'"
            )
        if not self.player.ephsus_quest_complete:
            prophecies.append("'Someone really needs some soil'")

        if not prophecies:
            self.player.minshin += PROPHECY_COST
            self.current_room.add_message(
                "'The threads of fate are clear to you now. There is nothing "
                "more I can show you.' Your Minshin is returned."
            )
        else:
            prophecy = random.choice(prophecies)
            self.current_room.add_message(
                f"Hinter takes your {PROPHECY_COST} Minshin and her eyes cloud "
                f"over. {prophecy}"
            )